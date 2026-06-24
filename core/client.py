from __future__ import annotations

import binascii
import base64
import json
import random
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import urljoin

from config.game import DEFAULTS
from core.crypto import decode_bytes, decrypt_response_base64
from core.error import SessionRestoreError
from core.packet import PacketMeta, build_packet_detailed
from core.protocol import protocol_value, request_protocol
from utils.proxy import normalize_proxy_url, requests_proxy_map


@dataclass(frozen=True)
class BuiltRequest:
    protocol: int
    packet: bytes
    request_bytes: bytes
    meta: PacketMeta
    serialized_request_bytes: bytes = b""


DEFAULT_BESTHTTP_USER_AGENT = DEFAULTS.besthttp_user_agent
DEFAULT_BESTHTTP_MULTIPART_BOUNDARY_PREFIX = DEFAULTS.besthttp_boundary_prefix


class BAReplayClient:

    def __init__(
        self,
        *,
        host_url: str = "",
        api_url: str = "",
        session_api_url: str = "",
        bundle_version: str | None = None,
        client_version: str | None = None,
        aes_key: bytes | str | None = None,
        aes_iv: bytes | str | None = None,
        aes_encrypted_key: bytes | str | None = None,
        aes_encrypted_iv: bytes | str | None = None,
        session_key: Mapping[str, Any] | None = None,
        account_id: int | None = None,
        server_time_ticks: int | None = None,
        signed_key: bytes | str | None = None,
        signed_iv: bytes | str | None = None,
        sqlcipher_key: bytes | str | None = None,
        sqlcipher_license: str | None = None,
        account_check_state: Mapping[str, Any] | None = None,
        timeout: float = 20.0,
        byte_encoding: str = "auto",
        headers: Mapping[str, str] | None = None,
        proxy: str | None = None,
        proxies: Mapping[str, str] | None = None,
    ) -> None:
        self.host_url = host_url
        self.api_host_url = api_url
        self.session_api_host_url = session_api_url
        self.bundle_version = bundle_version
        self.client_version = client_version or ""
        self.aes_key = decode_bytes(aes_key, encoding=byte_encoding)
        self.aes_iv = decode_bytes(aes_iv, encoding=byte_encoding)
        self.aes_encrypted_key = decode_bytes(aes_encrypted_key, encoding=byte_encoding)
        self.aes_encrypted_iv = decode_bytes(aes_encrypted_iv, encoding=byte_encoding)
        self.session_key = dict(session_key) if session_key else None
        self.account_id = account_id
        self.server_time_ticks = server_time_ticks
        self.signed_key = decode_bytes(signed_key, encoding=byte_encoding)
        self.signed_iv = decode_bytes(signed_iv, encoding=byte_encoding)
        self.sqlcipher_key = decode_bytes(sqlcipher_key, encoding=byte_encoding)
        self.sqlcipher_license = str(sqlcipher_license or "")
        self.account_check_state = dict(account_check_state) if account_check_state else None
        self.timeout = timeout
        self.headers = dict(headers or {})
        self.proxy = normalize_proxy_url(proxy)
        self.proxies = dict(proxies) if proxies is not None else requests_proxy_map(self.proxy)
        self._http_session = None
        self._async_http_client = None
        self._restored_cookies: dict[str, str] = {}
        self.last_exchange: dict[str, Any] | None = None

    @classmethod
    def from_session(
        cls,
        session: Mapping[str, Any],
        *,
        timeout: float = 20.0,
        proxy: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> "BAReplayClient":
        if not isinstance(session, Mapping):
            raise SessionRestoreError("session payload must be a mapping")
        host_url = _session_text(session, "host_url", "gateway_url")
        api_url = _session_text(session, "api_url")
        if not host_url:
            raise SessionRestoreError("session payload is missing host_url")
        if not api_url:
            raise SessionRestoreError("session payload is missing api_url")

        client = cls(
            host_url=host_url,
            api_url=api_url,
            session_api_url=_session_text(session, "session_api_url"),
            bundle_version=_session_text(session, "bundle_version") or None,
            client_version=_session_text(session, "client_version"),
            aes_key=_session_bytes(session, "aes_key"),
            aes_iv=_session_bytes(session, "aes_iv"),
            aes_encrypted_key=_session_bytes(session, "aes_encrypted_key"),
            aes_encrypted_iv=_session_bytes(session, "aes_encrypted_iv"),
            signed_key=_session_bytes(session, "signed_key"),
            signed_iv=_session_bytes(session, "signed_iv"),
            sqlcipher_key=_session_sqlcipher_key(session),
            sqlcipher_license=_session_sqlcipher_license(session),
            session_key=_session_mapping(session, "session_key", "SessionKey"),
            account_id=_session_int(session, "account_id", "AccountId"),
            server_time_ticks=_session_int(session, "server_time_ticks", "ServerTimeTicks"),
            account_check_state=_session_mapping(session, "account_check_state"),
            timeout=timeout,
            headers=headers,
            proxy=proxy,
        )
        client._restored_cookies = _session_cookies(session)
        return client

    def export_session(self) -> dict[str, Any]:
        return {
            "version": 1,
            "host_url": self.host_url,
            "api_url": self.api_host_url,
            "session_api_url": self.session_api_url,
            "gateway_url": self.gateway_url,
            "bundle_version": self.bundle_version,
            "client_version": self.client_version,
            "account_id": self.account_id,
            "server_time_ticks": self.server_time_ticks,
            "session_key": dict(self.session_key) if self.session_key else None,
            "aes_key": _b64(self.aes_key),
            "aes_iv": _b64(self.aes_iv),
            "aes_encrypted_key": _b64(self.aes_encrypted_key),
            "aes_encrypted_iv": _b64(self.aes_encrypted_iv),
            "signed_key": _b64(self.signed_key),
            "signed_iv": _b64(self.signed_iv),
            "sqlcipher": {
                "key": _b64(self.sqlcipher_key),
                "license": self.sqlcipher_license,
            }
            if self.sqlcipher_key and self.sqlcipher_license
            else None,
            "account_check_state": self.account_check_state,
            "cookies": self._session_cookies(),
        }

    def set_crypto(
        self,
        *,
        aes_key: bytes | str | None = None,
        aes_iv: bytes | str | None = None,
        aes_encrypted_key: bytes | str | None = None,
        aes_encrypted_iv: bytes | str | None = None,
        byte_encoding: str = "auto",
    ) -> None:
        if aes_key is not None:
            self.aes_key = decode_bytes(aes_key, encoding=byte_encoding)
        if aes_iv is not None:
            self.aes_iv = decode_bytes(aes_iv, encoding=byte_encoding)
        if aes_encrypted_key is not None:
            self.aes_encrypted_key = decode_bytes(aes_encrypted_key, encoding=byte_encoding)
        if aes_encrypted_iv is not None:
            self.aes_encrypted_iv = decode_bytes(aes_encrypted_iv, encoding=byte_encoding)

    def set_sqlcipher(
        self,
        *,
        sqlcipher_key: bytes | str | None = None,
        sqlcipher_license: str | None = None,
        byte_encoding: str = "base64",
    ) -> None:
        if sqlcipher_key is not None:
            self.sqlcipher_key = decode_bytes(sqlcipher_key, encoding=byte_encoding)
        if sqlcipher_license is not None:
            self.sqlcipher_license = str(sqlcipher_license)

    def build(
        self,
        protocol_or_request: int | str,
        fields: Mapping[str, Any] | bytes | bytearray | str | None = None,
        *,
        session_key: Mapping[str, Any] | None = None,
        inject_hash: bool = True,
        include_base_defaults: bool = False,
        include_protocol_field: bool = True,
        omit_none: bool = True,
        counter: int | None = None,
        aes_encrypted_key: bytes | None = None,
        aes_encrypted_iv: bytes | None = None,
        encrypt_request: bool | None = None,
    ) -> BuiltRequest:
        protocol = self._resolve_protocol(protocol_or_request)
        resolved_aes_encrypted_key = self.aes_encrypted_key if aes_encrypted_key is None else aes_encrypted_key
        resolved_aes_encrypted_iv = self.aes_encrypted_iv if aes_encrypted_iv is None else aes_encrypted_iv
        packet, meta, request_bytes, serialized_request_bytes = build_packet_detailed(
            protocol,
            fields or {},
            aes_encrypted_key=resolved_aes_encrypted_key,
            aes_encrypted_iv=resolved_aes_encrypted_iv,
            session_key=session_key if session_key is not None else self.session_key,
            inject_hash=inject_hash,
            include_base_defaults=include_base_defaults,
            include_protocol_field=include_protocol_field,
            omit_none=omit_none,
            counter=counter,
            request_aes_key=self.aes_key,
            request_aes_iv=self.aes_iv,
            encrypt_request=encrypt_request,
        )
        return BuiltRequest(protocol, packet, request_bytes, meta, serialized_request_bytes)

    def post(
        self,
        protocol_or_request: int | str,
        fields: Mapping[str, Any] | bytes | bytearray | str | None = None,
        *,
        url: str | None = None,
        body_mode: str = "besthttp-multipart",
        decrypt: bool = True,
        json_response: bool = True,
        **build_kwargs: Any,
    ) -> Any:
        built = self.build(protocol_or_request, fields, **build_kwargs)
        response_text = self.post_packet(built.packet, url=url, body_mode=body_mode)
        if decrypt:
            response_text = self.decode_response(response_text)
        if json_response:
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                return response_text
        return response_text

    async def post_async(
        self,
        protocol_or_request: int | str,
        fields: Mapping[str, Any] | bytes | bytearray | str | None = None,
        *,
        url: str | None = None,
        body_mode: str = DEFAULTS.body_mode,
        decrypt: bool = True,
        json_response: bool = True,
        **build_kwargs: Any,
    ) -> Any:
        built = self.build(protocol_or_request, fields, **build_kwargs)
        response_text = await self.post_packet_async(built.packet, url=url, body_mode=body_mode)
        if decrypt:
            response_text = self.decode_response(response_text)
        if json_response:
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                return response_text
        return response_text

    def post_packet(self, packet: bytes, *, url: str | None = None, body_mode: str = "besthttp-multipart") -> str:
        import requests

        target_url = url or self.gateway_url
        headers = self.default_headers()
        session = self._get_http_session()
        try:
            if body_mode == "multipart":
                response = session.post(
                    target_url,
                    headers=headers,
                    files={"mx": ("mx", packet, "application/octet-stream")},
                    timeout=self.timeout,
                    proxies=self.proxies or None,
                )
            elif body_mode == "besthttp-multipart":
                body, content_type = build_besthttp_multipart("mx", packet)
                headers["Content-Type"] = content_type
                response = session.post(
                    target_url,
                    headers=headers,
                    data=body,
                    timeout=self.timeout,
                    proxies=self.proxies or None,
                )
            elif body_mode == "raw":
                response = session.post(
                    target_url,
                    headers=headers,
                    data=packet,
                    timeout=self.timeout,
                    proxies=self.proxies or None,
                )
            else:
                raise ValueError("body_mode must be 'multipart', 'besthttp-multipart', or 'raw'")
        except requests.exceptions.InvalidSchema as exc:
            if "SOCKS" in str(exc).upper():
                raise RuntimeError(
                    "SOCKS proxy requires PySocks support; run: python -m pip install requests[socks]"
                ) from exc
            raise
        self.last_exchange = self._build_exchange_meta(response, body_mode=body_mode)
        if response.status_code >= 400 and not response.text:
            response.raise_for_status()
        return response.text

    async def post_packet_async(
        self,
        packet: bytes,
        *,
        url: str | None = None,
        body_mode: str = DEFAULTS.body_mode,
    ) -> str:
        target_url = url or self.gateway_url
        headers = self.default_headers()
        client = self._get_async_http_client()
        if body_mode == "multipart":
            response = await client.post(
                target_url,
                headers=headers,
                files={"mx": ("mx", packet, "application/octet-stream")},
            )
        elif body_mode == "besthttp-multipart":
            body, content_type = build_besthttp_multipart("mx", packet)
            headers["Content-Type"] = content_type
            response = await client.post(target_url, headers=headers, content=body)
        elif body_mode == "raw":
            response = await client.post(target_url, headers=headers, content=packet)
        else:
            raise ValueError("body_mode must be 'multipart', 'besthttp-multipart', or 'raw'")
        self.last_exchange = self._build_async_exchange_meta(response, body_mode=body_mode)
        if response.status_code >= 400 and not response.text:
            response.raise_for_status()
        return response.text

    def decode_response(self, encrypted_base64_or_json: str) -> str:
        return decode_gateway_response(encrypted_base64_or_json, aes_key=self.aes_key, aes_iv=self.aes_iv).payload

    def default_headers(self) -> dict[str, str]:
        headers = {
            "mx": "2",
            "Accept-Encoding": "identity",
            "User-Agent": DEFAULT_BESTHTTP_USER_AGENT,
        }
        bundle_version = self.bundle_version or self.client_version
        if bundle_version:
            headers["Bundle-Version"] = bundle_version
        headers.update(self.headers)
        return headers

    def _get_http_session(self):
        import requests

        if self._http_session is None:
            self._http_session = requests.Session()
            self._http_session.trust_env = False
            if self._restored_cookies:
                self._http_session.cookies.update(self._restored_cookies)
        return self._http_session

    def _session_cookies(self) -> dict[str, str]:
        if self._http_session is None:
            return {}
        import requests

        return requests.utils.dict_from_cookiejar(getattr(self._http_session, "cookies", {}))

    def _get_async_http_client(self):
        import httpx

        if self._async_http_client is None:
            self._async_http_client = httpx.AsyncClient(
                timeout=self.timeout,
                proxy=self.proxy or None,
                trust_env=False,
                cookies=self._restored_cookies or None,
                follow_redirects=True,
            )
        return self._async_http_client

    async def aclose(self) -> None:
        if self._async_http_client is None:
            return
        await self._async_http_client.aclose()
        self._async_http_client = None

    def _build_exchange_meta(self, response: Any, *, body_mode: str) -> dict[str, Any]:
        return {
            "url": getattr(response, "url", ""),
            "status_code": getattr(response, "status_code", None),
            "reason": getattr(response, "reason", ""),
            "body_mode": body_mode,
            "response_len": len(getattr(response, "content", b"") or b""),
        }

    def _build_async_exchange_meta(self, response: Any, *, body_mode: str) -> dict[str, Any]:
        return {
            "url": str(getattr(response, "url", "")),
            "status_code": getattr(response, "status_code", None),
            "reason": getattr(response, "reason_phrase", ""),
            "body_mode": body_mode,
            "response_len": len(getattr(response, "content", b"") or b""),
        }

    @property
    def gateway_url(self) -> str:
        if not self.host_url:
            raise ValueError("host_url or explicit url is required to post")
        if self.host_url.endswith("/gateway"):
            return self.host_url
        if self.host_url.endswith("gateway"):
            return self.host_url
        return urljoin(self.host_url.rstrip("/") + "/", "gateway")

    @property
    def api_url(self) -> str:
        if self.api_host_url:
            return self.api_host_url
        if not self.host_url:
            raise ValueError("api_url or host_url is required to post API requests")
        if self.host_url.endswith("/gateway") or self.host_url.endswith("gateway"):
            raise ValueError("api_url is required when host_url points at gateway")
        return self.host_url

    @property
    def session_api_url(self) -> str:
        return self.session_api_host_url or self.api_url

    @staticmethod
    def _resolve_protocol(protocol_or_request: int | str) -> int:
        if isinstance(protocol_or_request, int):
            return protocol_or_request
        try:
            return protocol_value(protocol_or_request)
        except Exception:
            return request_protocol(protocol_or_request)[1]


@dataclass(frozen=True)
class GatewayResponse:
    protocol: str | int | None
    payload: str


def decode_gateway_response(response_text: str, *, aes_key: bytes | None, aes_iv: bytes | None) -> GatewayResponse:

    parsed = _parse_gateway_wrapper(response_text)
    if parsed is not None:
        protocol, packet = parsed
        if packet.lstrip().startswith(("{", "[")):
            payload = packet
        else:
            try:
                payload = decrypt_response_base64(aes_key, aes_iv, packet)
            except (binascii.Error, UnicodeDecodeError, ValueError):
                payload = packet
        return GatewayResponse(protocol=protocol, payload=payload)

    decrypted = decrypt_response_base64(aes_key, aes_iv, response_text)
    parsed = _parse_gateway_wrapper(decrypted)
    if parsed is not None:
        protocol, packet = parsed
        return GatewayResponse(protocol=protocol, payload=packet)
    protocol = None
    packet = response_text
    payload = decrypted
    return GatewayResponse(protocol=protocol, payload=payload)


def _parse_gateway_wrapper(text: str) -> tuple[str | int | None, str] | None:
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(obj, dict) and "packet" in obj:
        return obj.get("protocol"), str(obj.get("packet", ""))
    return None


def _b64(value: bytes | bytearray | memoryview | None) -> str:
    if not value:
        return ""
    return base64.b64encode(bytes(value)).decode("ascii")


def _session_text(session: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = session.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def _session_int(session: Mapping[str, Any], *keys: str) -> int | None:
    value = _session_text(session, *keys)
    if not value:
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise SessionRestoreError("session payload contains an invalid integer field") from exc


def _session_mapping(session: Mapping[str, Any], *keys: str) -> dict[str, Any] | None:
    for key in keys:
        value = session.get(key)
        if isinstance(value, Mapping):
            return dict(value)
    return None


def _session_bytes(session: Mapping[str, Any], key: str) -> bytes:
    value = session.get(key)
    if value in (None, ""):
        return b""
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value)
    text = str(value)
    try:
        return decode_bytes(text, encoding="base64")
    except Exception:
        try:
            return decode_bytes(text, encoding="auto")
        except Exception as exc:
            raise SessionRestoreError("session payload contains invalid key material") from exc


def _session_sqlcipher_key(session: Mapping[str, Any]) -> bytes:
    sqlcipher = session.get("sqlcipher")
    if isinstance(sqlcipher, Mapping):
        for key in ("key", "sqlcipher_key", "SqlCipherKey"):
            value = sqlcipher.get(key)
            if value not in (None, ""):
                return _decode_session_bytes(value)
    for key in ("sqlcipher_key", "SqlCipherKey"):
        value = session.get(key)
        if value not in (None, ""):
            return _decode_session_bytes(value)
    return b""


def _session_sqlcipher_license(session: Mapping[str, Any]) -> str:
    sqlcipher = session.get("sqlcipher")
    if isinstance(sqlcipher, Mapping):
        for key in ("license", "sqlcipher_license", "SqlCipherLicense"):
            value = sqlcipher.get(key)
            if value not in (None, ""):
                return str(value)
    for key in ("sqlcipher_license", "SqlCipherLicense"):
        value = session.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def _decode_session_bytes(value: Any) -> bytes:
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value)
    text = str(value)
    try:
        return decode_bytes(text, encoding="base64")
    except Exception:
        try:
            return decode_bytes(text, encoding="auto")
        except Exception as exc:
            raise SessionRestoreError("session payload contains invalid key material") from exc


def _session_cookies(session: Mapping[str, Any]) -> dict[str, str]:
    cookies = session.get("cookies")
    if not isinstance(cookies, Mapping):
        return {}
    return {str(key): str(value) for key, value in cookies.items() if value not in (None, "")}


def build_besthttp_multipart(
    field_name: str,
    content: bytes,
    *,
    file_name: str | None = None,
    mime_type: str | None = None,
    boundary: str | None = None,
) -> tuple[bytes, str]:

    boundary = boundary or f"{DEFAULT_BESTHTTP_MULTIPART_BOUNDARY_PREFIX}{random.randint(0, 2**31 - 1)}"
    file_name = file_name or f"{field_name}.dat"
    mime_type = mime_type or "application/octet-stream"

    lines = [
        f"--{boundary}\r\n",
        f'Content-Disposition: form-data; name="{field_name}"; filename="{file_name}"\r\n',
        f"Content-Type: {mime_type}\r\n",
        f"Content-Length: {len(content)}\r\n",
        "\r\n",
    ]
    body = "".join(lines).encode("utf-8") + bytes(content) + b"\r\n" + f"--{boundary}--\r\n".encode("utf-8")
    return body, f"multipart/form-data; boundary={boundary}"

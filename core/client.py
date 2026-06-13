"""High-level request builder and HTTP replay client."""

from __future__ import annotations

import binascii
import json
import random
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import urljoin

from core.crypto import decode_bytes, decrypt_response_base64
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


DEFAULT_BESTHTTP_USER_AGENT = "BestHTTP/2 v2.4.0"
DEFAULT_BESTHTTP_MULTIPART_BOUNDARY_PREFIX = "BestHTTP_HTTPMultiPartForm_"


class BAReplayClient:
    """Replay client for the main game gateway packet path."""

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
        self.account_check_state = dict(account_check_state) if account_check_state else None
        self.timeout = timeout
        self.headers = dict(headers or {})
        self.proxy = normalize_proxy_url(proxy)
        self.proxies = dict(proxies) if proxies is not None else requests_proxy_map(self.proxy)
        self._http_session = None
        self.last_exchange: dict[str, Any] | None = None

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
        return self._http_session

    def _build_exchange_meta(self, response: Any, *, body_mode: str) -> dict[str, Any]:
        import requests

        request = getattr(response, "request", None)
        session = self._get_http_session()
        history = []
        for item in getattr(response, "history", ()) or ():
            history.append(
                {
                    "status_code": getattr(item, "status_code", None),
                    "url": getattr(item, "url", ""),
                    "headers": dict(getattr(item, "headers", {}) or {}),
                }
            )
        return {
            "url": getattr(response, "url", ""),
            "status_code": getattr(response, "status_code", None),
            "reason": getattr(response, "reason", ""),
            "body_mode": body_mode,
            "request_method": getattr(request, "method", "POST"),
            "request_url": getattr(request, "url", ""),
            "request_headers": dict(getattr(request, "headers", {}) or {}),
            "response_headers": dict(getattr(response, "headers", {}) or {}),
            "response_cookies": requests.utils.dict_from_cookiejar(getattr(response, "cookies", {})),
            "session_cookies": requests.utils.dict_from_cookiejar(getattr(session, "cookies", {})),
            "redirect_history": history,
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
    packet: str
    payload: str
    raw: str


def decode_gateway_response(response_text: str, *, aes_key: bytes | None, aes_iv: bytes | None) -> GatewayResponse:
    """Parse NetworkService's ``protocol``/``packet`` wrapper and decrypt packet."""

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
        return GatewayResponse(protocol=protocol, packet=packet, payload=payload, raw=response_text)

    decrypted = decrypt_response_base64(aes_key, aes_iv, response_text)
    parsed = _parse_gateway_wrapper(decrypted)
    if parsed is not None:
        protocol, packet = parsed
        return GatewayResponse(protocol=protocol, packet=packet, payload=packet, raw=response_text)
    protocol = None
    packet = response_text
    payload = decrypted
    return GatewayResponse(protocol=protocol, packet=packet, payload=payload, raw=response_text)


def _parse_gateway_wrapper(text: str) -> tuple[str | int | None, str] | None:
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(obj, dict) and "packet" in obj:
        return obj.get("protocol"), str(obj.get("packet", ""))
    return None


def build_besthttp_multipart(
    field_name: str,
    content: bytes,
    *,
    file_name: str | None = None,
    mime_type: str | None = None,
    boundary: str | None = None,
) -> tuple[bytes, str]:
    """Build the single-file multipart body produced by BestHTTP AddBinaryData."""

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

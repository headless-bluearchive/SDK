
from __future__ import annotations

import hashlib
import hmac
import json
import re
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Mapping
from urllib.parse import urljoin

from config.game import DEFAULTS
from core.error import LoginError
from utils.proxy import normalize_proxy_url, requests_proxy_map
from modules.auth.toysdk_models import ToySdkCallbackResult, ToySdkLoginResult


COMMON_AES_KEY = bytes.fromhex("dd4763541be100910b568ca6d48268e3")
NXCOM_CRYPTO_KEY = "NexonUser"
DEFAULT_BOLT_URL = DEFAULTS.toy_bolt_url
DEFAULT_GW_BOLT_URL = DEFAULTS.toy_gw_bolt_url
DEFAULT_SERVICE_ID = DEFAULTS.service_id
DEFAULT_CLIENT_ID = DEFAULTS.client_id
DEFAULT_GAME_ID = DEFAULTS.game_id
DEFAULT_PACKAGE_NAME = DEFAULTS.package_name
DEFAULT_STORE_TYPE = DEFAULTS.store_type
DEFAULT_SDK_VERSION = DEFAULTS.sdk_version
DEFAULT_APP_VERSION_CODE = DEFAULTS.app_version_code
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
NXCOM_USER_ID_FIELD = "userID"
LOGIN_TYPE_NXCOM = 1
LOGIN_TYPE_NXARENA = 107


class ToySdkAndroidError(LoginError):
    pass


class ToySdkAndroidTurnstileRequired(ToySdkAndroidError):

    def __init__(self, result: Mapping[str, Any]):
        self.result = dict(result)
        self.error_code = result_error_code(result) or 0
        self.error_text = str(find_first(result, "errorText", "error_text", "message") or "")
        self.error_detail = str(find_first(result, "errorDetail", "error_detail", "detail") or "")
        self.cf_alt_token = str(find_first(result, "cfAltToken", "cf_alt_token") or "")
        message = f"TOYSDK signIn.nx requires Turnstile/cfToken retry: errorCode={self.error_code}"
        if self.error_text:
            message += f" errorText={self.error_text}"
        if self.cf_alt_token:
            message += " cfAltToken=<present>"
        super().__init__(message)


class ToySdkAndroidApiError(ToySdkAndroidError):

    def __init__(self, result: Mapping[str, Any], *, stage: str = "TOYSDK"):
        self.result = dict(result)
        self.stage = stage
        self.error_code = result_error_code(result) or 0
        self.error_text = str(find_first(result, "errorText", "error_text", "message") or "")
        self.error_detail = str(find_first(result, "errorDetail", "error_detail", "detail") or "")
        message = f"{stage} failed: errorCode={self.error_code}"
        if self.error_text:
            message += f" errorText={self.error_text}"
        super().__init__(message)


@dataclass(frozen=True)
class AndroidDeviceProfile:
    country: str = DEFAULTS.country
    locale: str = DEFAULTS.locale
    initial_country: str = DEFAULTS.country
    device_country: str = DEFAULTS.country
    uuid: str = ""
    uuid2: str = ""
    os: str = DEFAULTS.android_os_code
    os_version: str = DEFAULTS.android_os_version
    device_model: str = DEFAULTS.android_model
    carrier_name: str = ""
    mnc: int = 0
    mcc: int = 0
    advertising_id: str = ""
    app_set_scope: int = 0
    app_set_id: str = ""

    def with_generated_ids(self) -> "AndroidDeviceProfile":
        return AndroidDeviceProfile(
            country=self.country,
            locale=self.locale,
            initial_country=self.initial_country or self.country,
            device_country=self.device_country or self.country,
            uuid=self.uuid or str(uuid.uuid4()),
            uuid2=self.uuid2 or str(uuid.uuid4()),
            os=self.os,
            os_version=self.os_version,
            device_model=self.device_model,
            carrier_name=self.carrier_name,
            mnc=self.mnc,
            mcc=self.mcc,
            advertising_id=self.advertising_id,
            app_set_scope=self.app_set_scope,
            app_set_id=self.app_set_id,
        )


@dataclass(frozen=True)
class AndroidToyConfig:
    service_id: str = DEFAULT_SERVICE_ID
    client_id: str = DEFAULT_CLIENT_ID
    game_id: str = DEFAULT_GAME_ID
    package_name: str = DEFAULT_PACKAGE_NAME
    store_type: str = DEFAULT_STORE_TYPE
    sdk_version: str = DEFAULT_SDK_VERSION
    app_version_code: int = DEFAULT_APP_VERSION_CODE
    bolt_url: str = DEFAULT_BOLT_URL
    gw_bolt_url: str = DEFAULT_GW_BOLT_URL
    game_server_code: str = ""


@dataclass(frozen=True)
class AndroidToySession:
    np_sn: int | None = None
    guid: str = ""
    np_token: str = ""
    npa_code: str = ""
    session_token: str = ""
    um_key: str = ""
    member_id: str = ""
    member_type: str = ""
    ngsm_token: str = ""
    raw_login: dict[str, Any] | None = None
    raw_user_info: dict[str, Any] | None = None

    def to_toy_login_result(self) -> ToySdkLoginResult:
        raw_payload = json_compact(
            {
                "login": self.raw_login,
                "userInfo": self.raw_user_info,
                "ngsmToken": self.ngsm_token,
            }
        )
        return ToySdkLoginResult(
            np_sn=self.np_sn,
            np_token=self.np_token,
            npa_code=self.npa_code,
            session_token=self.session_token,
            guid=self.guid,
            member_id=self.member_id,
            member_type=self.member_type,
            um_key=self.um_key,
            ngsm_token=self.ngsm_token,
            callback=ToySdkCallbackResult(payload=raw_payload, parsed=json.loads(raw_payload)),
        )


def json_compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len]) * pad_len


def pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes:
    if not data or len(data) % block_size:
        raise ValueError("invalid PKCS7 padded data length")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("invalid PKCS7 padding length")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("invalid PKCS7 padding bytes")
    return data[:-pad_len]


def aes_ecb_pkcs7_encrypt(key: bytes | str, data: bytes) -> bytes:
    key_bytes = key.encode("utf-8") if isinstance(key, str) else bytes(key)
    key_bytes = key_bytes[:16].ljust(16, b"\x00")
    padded = pkcs7_pad(data)
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except Exception:
        from Crypto.Cipher import AES

        return AES.new(key_bytes, AES.MODE_ECB).encrypt(padded)
    encryptor = Cipher(algorithms.AES(key_bytes), modes.ECB()).encryptor()
    return encryptor.update(padded) + encryptor.finalize()


def aes_ecb_pkcs7_decrypt(key: bytes | str, data: bytes) -> bytes:
    key_bytes = key.encode("utf-8") if isinstance(key, str) else bytes(key)
    key_bytes = key_bytes[:16].ljust(16, b"\x00")
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except Exception:
        from Crypto.Cipher import AES

        return pkcs7_unpad(AES.new(key_bytes, AES.MODE_ECB).decrypt(data))
    decryptor = Cipher(algorithms.AES(key_bytes), modes.ECB()).decryptor()
    return pkcs7_unpad(decryptor.update(data) + decryptor.finalize())


def hmac_sha256_hex(key: str, data: str | bytes) -> str:
    raw = data.encode("utf-8") if isinstance(data, str) else data
    return hmac.new(key.encode("utf-8"), raw, hashlib.sha256).hexdigest().upper()


def sha512_hex_lower(data: str | bytes) -> str:
    raw = data.encode("utf-8") if isinstance(data, str) else data
    return hashlib.sha512(raw).hexdigest()


def npsn_aes128_key(np_sn: int) -> bytes:
    text = f"{int(np_sn):019d}"
    return aes_ecb_pkcs7_encrypt(text[3:], text[4:].encode("utf-8"))


def toy_encrypt(crypto_type: str, data: bytes, np_sn: int | None = None) -> bytes:
    kind = crypto_type.upper()
    if kind == "NONE":
        return data
    if kind == "COMMON":
        return aes_ecb_pkcs7_encrypt(COMMON_AES_KEY, data)
    if kind == "NPSN":
        if np_sn is None:
            raise ToySdkAndroidError("NPSN crypto requires np_sn")
        return aes_ecb_pkcs7_encrypt(npsn_aes128_key(np_sn), data)
    raise ValueError(f"unsupported TOYSDK crypto type: {crypto_type}")


def toy_decrypt(crypto_type: str, data: bytes, np_sn: int | None = None) -> bytes:
    kind = crypto_type.upper()
    if kind == "NONE":
        return data
    if kind == "COMMON":
        return aes_ecb_pkcs7_decrypt(COMMON_AES_KEY, data)
    if kind == "NPSN":
        if np_sn is None:
            raise ToySdkAndroidError("NPSN crypto requires np_sn")
        return aes_ecb_pkcs7_decrypt(npsn_aes128_key(np_sn), data)
    raise ValueError(f"unsupported TOYSDK crypto type: {crypto_type}")


def escape_password_for_java_json(password: str) -> bytes:
    out: list[str] = []
    for ch in password:
        code = ord(ch)
        if ch == "\b":
            out.append(r"\b")
        elif ch == "\t":
            out.append(r"\t")
        elif ch == "\n":
            out.append(r"\n")
        elif ch == "\f":
            out.append(r"\f")
        elif ch == "\r":
            out.append(r"\r")
        elif ch in ('"', "/", "\\"):
            out.append("\\" + ch)
        elif code <= 31:
            out.append(f"\\u{code:04x}")
        else:
            out.append(ch)
    return "".join(out).encode("utf-8")


def find_first(obj: Any, *names: str) -> Any:
    wanted = {name.lower() for name in names}
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            if str(key).lower() in wanted:
                return value
        for value in obj.values():
            found = find_first(value, *names)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = find_first(item, *names)
            if found is not None:
                return found
    return None


def as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def result_error_code(result: Mapping[str, Any]) -> int | None:
    return as_int(find_first(result, "errorCode", "error_code", "code"))


def result_is_success(result: Mapping[str, Any]) -> bool:
    code = result_error_code(result)
    return code is None or code == 0


class AndroidToySdkClient:

    def __init__(
        self,
        *,
        config: AndroidToyConfig | None = None,
        device: AndroidDeviceProfile | None = None,
        proxy: str | None = None,
        timeout: float = 30.0,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.config = config or AndroidToyConfig()
        self.device = (device or AndroidDeviceProfile()).with_generated_ids()
        self.proxy = normalize_proxy_url(proxy)
        self.proxies = requests_proxy_map(self.proxy)
        self.timeout = timeout
        self.extra_headers = dict(headers or {})
        self.session = AndroidToySession()
        self.terms_api_ver = 2
        self.policy_api_ver = 2
        self.last_requests: list[dict[str, Any]] = []
        self.available_login_types: list[int] = []
        self.service_flags: dict[str, Any] = {}
        self.last_login_type: int | None = None
        self.http = None

    def enter_toy(self, *, mnc: int | None = None, mcc: int | None = None) -> dict[str, Any]:
        body = {
            "mnc": self.device.mnc if mnc is None else int(mnc),
            "mcc": self.device.mcc if mcc is None else int(mcc),
            "termsApiVer": self.terms_api_ver,
            "policyApiVer": self.policy_api_ver,
        }
        result = self._post_bolt(
            "/sdk/enterToy.nx",
            body,
            encrypt_type="COMMON",
            decrypt_type="NONE",
            credential=self._credential(),
        )
        service = find_first(result, "service")
        if isinstance(service, Mapping):
            self.service_flags = dict(service)
            terms = as_int(service.get("termsApiVer"))
            policy = as_int(service.get("policyApiVer"))
            if terms is not None:
                self.terms_api_ver = terms
            if policy is not None:
                self.policy_api_ver = policy
        memberships = find_first(result, "useMemberships")
        parsed_memberships: list[int] = []
        if isinstance(memberships, list):
            for value in memberships:
                parsed = as_int(value)
                if parsed is not None:
                    parsed_memberships.append(parsed)
        if parsed_memberships:
            self.available_login_types = parsed_memberships
        for flag_name in ("useArena2FA", "useNexonOTP"):
            flag_value = find_first(result, flag_name)
            if flag_value is not None:
                self.service_flags[flag_name] = flag_value
        country = find_first(result, "country")
        if isinstance(country, str) and country:
            self.device = AndroidDeviceProfile(
                country=country,
                locale=self.device.locale,
                initial_country=self.device.initial_country or country,
                device_country=self.device.device_country,
                uuid=self.device.uuid,
                uuid2=self.device.uuid2,
                os=self.device.os,
                os_version=self.device.os_version,
                device_model=self.device.device_model,
                carrier_name=self.device.carrier_name,
                mnc=self.device.mnc,
                mcc=self.device.mcc,
                advertising_id=self.device.advertising_id,
                app_set_scope=self.device.app_set_scope,
                app_set_id=self.device.app_set_id,
            )
        return result

    def get_nexon_sn_by_nx_login(self, user_id: str, password: str, *, cf_token: str = "") -> dict[str, Any]:
        body = {
            NXCOM_USER_ID_FIELD: user_id,
            "uuid": self.device.uuid,
            "optional": {},
        }
        if cf_token:
            body["optional"]["cfToken"] = cf_token
        plain = self._nx_password_body(body, user_id, password)
        result = self._post_bolt_bytes(
            "/sdk/getNexonSNByNXKLogin.nx",
            toy_encrypt("COMMON", plain, self.session.np_sn),
            decrypt_type="COMMON",
            credential=self._credential(),
        )
        self._raise_for_sign_in_challenge(result)
        self._raise_for_api_error(result, stage="getNexonSNByNXKLogin.nx")
        return result

    def login_with_nx(
        self,
        user_id: str,
        password: str,
        *,
        login_type: int = LOGIN_TYPE_NXCOM,
        cf_token: str = "",
        cf_alt_token: str = "",
    ) -> AndroidToySession:
        body = {
            NXCOM_USER_ID_FIELD: user_id,
            "uuid": self.device.uuid,
            "uuid2": self.device.uuid2,
            "memType": int(login_type),
            "termsApiVer": self.terms_api_ver,
            "optional": self._optional_body(
                email=user_id if is_email(user_id) else "",
                cf_token=cf_token,
                cf_alt_token=cf_alt_token,
            ),
        }
        resolved_login_type = int(login_type)
        self.last_login_type = resolved_login_type
        if resolved_login_type == LOGIN_TYPE_NXCOM:
            plain = self._nx_password_body(body, user_id, password)
        elif resolved_login_type == LOGIN_TYPE_NXARENA:
            body["passwd"] = sha512_hex_lower(password)
            plain = json_compact(body).encode("utf-8")
        else:
            raise ToySdkAndroidError(f"unsupported Nexon login type: {resolved_login_type}")
        result = self._post_bolt_bytes(
            "/sdk/signIn.nx",
            toy_encrypt("COMMON", plain, self.session.np_sn),
            decrypt_type="COMMON",
            credential=self._credential(),
        )
        self._raise_for_sign_in_challenge(result)
        self._raise_for_api_error(result, stage="signIn.nx")
        self.session = self._session_from_login(result, existing=self.session)
        return self.session

    def create_np_token(self) -> dict[str, Any]:
        result = self._post_bolt_bytes(
            "/sdk/createNPToken.nx",
            b"",
            decrypt_type="NPSN",
            credential=self._credential(require=True),
            encrypt_type="NPSN",
        )
        np_token = str(find_first(result, "npToken", "nptoken") or "")
        if np_token:
            self.session = AndroidToySession(
                np_sn=self.session.np_sn,
                guid=self.session.guid,
                np_token=np_token,
                npa_code=self.session.npa_code,
                session_token=self.session.session_token,
                um_key=self.session.um_key,
                member_id=self.session.member_id,
                member_type=self.session.member_type,
                ngsm_token=self.session.ngsm_token,
                raw_login=self.session.raw_login,
                raw_user_info=self.session.raw_user_info,
            )
        return result

    def get_user_info(self, *, mem_token: str = "", session_token: str = "") -> dict[str, Any]:
        body: dict[str, Any] = {"adid": self.device.advertising_id or ""}
        token = mem_token
        sess = session_token or self.session.session_token
        if token:
            body["memToken"] = token
        if sess:
            body["sessionToken"] = sess
        result = self._post_bolt(
            "/sdk/getUserInfo.nx",
            body,
            encrypt_type="NPSN",
            decrypt_type="NPSN",
            credential=self._credential(require=True),
        )
        self.session = self._session_from_user_info(result, existing=self.session)
        return result

    def login_with_nx_flow(
        self,
        user_id: str,
        password: str,
        *,
        enter_toy: bool = True,
        get_user_info: bool = True,
        cf_token: str = "",
        cf_alt_token: str = "",
        preflight_nexon_sn: bool = True,
        login_mode: str = "auto",
    ) -> AndroidToySession:
        if enter_toy:
            self.enter_toy()
        login_type = self.resolve_login_type(login_mode)
        if preflight_nexon_sn and login_type == LOGIN_TYPE_NXCOM:
            self.get_nexon_sn_by_nx_login(user_id, password, cf_token=cf_token)
        self.login_with_nx(
            user_id,
            password,
            login_type=login_type,
            cf_token=cf_token,
            cf_alt_token=cf_alt_token,
        )
        if get_user_info and self._has_credential():
            self.get_user_info()
        return self.session

    def resolve_login_type(self, login_mode: str = "auto") -> int:
        normalized = (login_mode or "auto").strip().lower()
        if normalized == "nxcom":
            return LOGIN_TYPE_NXCOM
        if normalized == "arena":
            return LOGIN_TYPE_NXARENA
        memberships = set(self.available_login_types)
        if LOGIN_TYPE_NXARENA in memberships and LOGIN_TYPE_NXCOM not in memberships:
            return LOGIN_TYPE_NXARENA
        if LOGIN_TYPE_NXCOM in memberships:
            return LOGIN_TYPE_NXCOM
        if LOGIN_TYPE_NXARENA in memberships:
            return LOGIN_TYPE_NXARENA
        return LOGIN_TYPE_NXCOM

    def _post_bolt(
        self,
        path: str,
        body: Mapping[str, Any],
        *,
        encrypt_type: str,
        decrypt_type: str,
        credential: tuple[str, str, int | None],
    ) -> dict[str, Any]:
        plain = json_compact(dict(body)).encode("utf-8")
        encrypted = toy_encrypt(encrypt_type, plain, credential[2])
        return self._post_bolt_bytes(path, encrypted, decrypt_type=decrypt_type, credential=credential, encrypt_type=encrypt_type)

    def _post_bolt_bytes(
        self,
        path: str,
        body: bytes,
        *,
        decrypt_type: str,
        credential: tuple[str, str, int | None],
        encrypt_type: str = "COMMON",
    ) -> dict[str, Any]:
        guid, np_token, np_sn = credential
        headers = self._bolt_headers(guid=guid, np_token=np_token, np_sn=np_sn or 0, encrypt_type=encrypt_type)
        return self._post_raw(urljoin(self.config.bolt_url.rstrip("/") + "/", path.lstrip("/")), body, headers, decrypt_type, np_sn)

    def _post_gw_bolt(self, path: str, body: Mapping[str, Any], *, headers: Mapping[str, str] | None = None) -> dict[str, Any]:
        merged = {
            "Accept": "application/json",
            "acceptLanguage": self.device.locale,
            "os": self.device.os,
            "uuid": self.device.uuid,
            "uuid2": self.device.uuid2,
            "acceptCountry": self.device.country,
        }
        merged.update(headers or {})
        return self._post_raw(
            urljoin(self.config.gw_bolt_url.rstrip("/") + "/", path.lstrip("/")),
            json_compact(dict(body)).encode("utf-8"),
            merged,
            "NONE",
            None,
        )

    def _post_raw(
        self,
        url: str,
        body: bytes,
        headers: Mapping[str, str],
        decrypt_type: str,
        np_sn: int | None,
    ) -> dict[str, Any]:
        import requests

        if self.http is None:
            self.http = requests.Session()
        merged_headers = dict(headers)
        merged_headers.update(self._decorator_headers())
        merged_headers.update(self.extra_headers)
        merged_headers = _latin1_headers(merged_headers)
        record = {
            "url": url,
            "headers": dict(merged_headers),
            "body_len": len(body),
            "decrypt_type": decrypt_type,
        }
        self.last_requests.append(record)
        response = self.http.post(
            url,
            headers=merged_headers,
            data=body,
            timeout=self.timeout,
            proxies=self.proxies or None,
        )
        raw = response.content
        record["status_code"] = response.status_code
        record["response_len"] = len(raw)
        decoded = ""
        if raw:
            try:
                decoded = toy_decrypt(decrypt_type, raw, np_sn).decode("utf-8")
            except Exception as exc:
                record["decrypt_error"] = f"{type(exc).__name__}: {exc}"
                try:
                    decoded = raw.decode("utf-8")
                except UnicodeDecodeError:
                    if response.status_code >= 400:
                        response.raise_for_status()
                    raise
        record["response_text"] = decoded[:2000]
        if response.status_code >= 400:
            try:
                record["error_json"] = json.loads(decoded)
            except Exception:
                record["error_text"] = decoded[:1000]
            response.raise_for_status()
        if not decoded:
            return {"errorCode": 0, "errorText": "Success", "errorDetail": ""}
        try:
            return json.loads(decoded)
        except json.JSONDecodeError as exc:
            raise ToySdkAndroidError(f"TOYSDK response is not JSON from {url}: {decoded[:1000]}") from exc

    def _bolt_headers(self, *, guid: str, np_token: str, np_sn: int, encrypt_type: str) -> dict[str, str]:
        npparams = {
            "sdkVer": self.config.sdk_version,
            "os": self.device.os,
            "svcID": self.config.service_id,
            "npToken": np_token,
            "appVersionNumber": self.config.app_version_code,
            "appId": self.config.package_name,
            "timeZone": current_timezone_offset_hours(),
            "adid": self.device.advertising_id,
            "mnc": self.device.mnc,
            "mcc": self.device.mcc,
            "model": self.device.device_model,
            "carrierName": self.device.carrier_name,
            "mk": self.config.store_type,
        }
        encrypted_npparams = toy_encrypt(encrypt_type, json_compact(npparams).encode("utf-8"), np_sn)
        gaid = hmac_sha256_hex(NXCOM_CRYPTO_KEY, self.device.advertising_id) if self.device.advertising_id else ""
        return {
            "npparams": encrypted_npparams.hex().upper(),
            "npsn": str(np_sn),
            "x-toy-service-id": self.config.service_id,
            "acceptLanguage": self.device.locale,
            "acceptCountry": self.device.country,
            "initialCountry": self.device.initial_country or self.device.country,
            "deviceCountry": self.device.device_country or self.device.country,
            "uuid": self.device.uuid,
            "uuid2": self.device.uuid2,
            "charset": "utf-8",
            "x-game-server-code": self.config.game_server_code,
            "osVersion": self.device.os_version,
            "gaid": gaid,
            "appset-scope": str(self.device.app_set_scope),
            "appset-id": self.device.app_set_id,
        }

    def _decorator_headers(self) -> dict[str, str]:
        return {
            "gid": self.config.service_id,
            "guid": self.session.guid,
            "gsid": "",
            "gcid": "",
            "world_id": "",
            "channel_id": "",
        }

    def _credential(self, *, require: bool = False) -> tuple[str, str, int | None]:
        guid = self.session.guid or (str(self.session.np_sn) if self.session.np_sn is not None else "")
        np_token = self.session.np_token
        np_sn = self.session.np_sn
        if require and (not guid or np_sn is None):
            raise ToySdkAndroidError("TOYSDK authenticated credential is required")
        return guid, np_token, np_sn

    def _has_credential(self) -> bool:
        guid, _np_token, np_sn = self._credential()
        return bool(guid) and np_sn is not None

    def _optional_body(self, *, email: str = "", cf_token: str = "", cf_alt_token: str = "") -> dict[str, Any]:
        body = {
            "email": email or None,
            "device": self.device.device_model,
            "name": "",
            "carrierName": self.device.carrier_name,
            "fbBizToken": None,
            "refreshToken": None,
            "encryptedMemberSN": None,
            "memberSN": 0,
            "platformUserId": None,
            "platformType": None,
            "securityState": 0,
            "toySecurityToken": None,
        }
        if cf_token:
            body["cfToken"] = cf_token
        if cf_alt_token:
            body["cfAltToken"] = cf_alt_token
        return body

    def _raise_for_sign_in_challenge(self, result: Mapping[str, Any]) -> None:
        code = result_error_code(result)
        if code in (1209, 2701):
            raise ToySdkAndroidTurnstileRequired(result)

    def _raise_for_api_error(self, result: Mapping[str, Any], *, stage: str) -> None:
        if not result_is_success(result):
            raise ToySdkAndroidApiError(result, stage=stage)

    def _nx_password_body(self, body: Mapping[str, Any], user_id: str, password: str) -> bytes:
        mutable = dict(body)
        if is_email(user_id):
            mutable["passwd"] = hmac_sha256_hex(NXCOM_CRYPTO_KEY, password)
            return json_compact(mutable).encode("utf-8")
        mutable["passwd"] = "PASSWORD"
        return json_compact(mutable).encode("utf-8").replace(
            b"PASSWORD",
            escape_password_for_java_json(password),
            1,
        )

    def _session_from_login(self, result: Mapping[str, Any], *, existing: AndroidToySession) -> AndroidToySession:
        body = find_first(result, "result")
        if not isinstance(body, Mapping):
            body = result
        raw_guid = str(find_first(body, "guid") or existing.guid or "")
        np_sn = as_int(find_first(body, "npSN", "npsn")) or as_int(raw_guid) or existing.np_sn
        guid = raw_guid or str(np_sn or "")
        um_key = str(find_first(body, "umKey", "um_key") or existing.um_key or "")
        member_type = str(find_first(body, "memberType", "primaryPlatformType", "nexonPlatformType") or existing.member_type or "")
        member_id = str(find_first(body, "memberId", "primaryPlatformUserId", "nexonPlatformUserId") or existing.member_id or "")
        if um_key and ":" in um_key and (not member_type or not member_id):
            inferred_type, inferred_id = um_key.split(":", 1)
            member_type = member_type or inferred_type
            member_id = member_id or inferred_id
        return AndroidToySession(
            np_sn=np_sn,
            guid=guid,
            np_token=str(find_first(body, "npToken", "nptoken") or existing.np_token or ""),
            npa_code=str(find_first(body, "npaCode", "npacode") or existing.npa_code or ""),
            session_token=str(find_first(body, "sessionToken", "session_token") or existing.session_token or ""),
            um_key=um_key,
            member_id=member_id,
            member_type=member_type,
            ngsm_token=str(find_first(body, "ngsmToken", "ngsm_token") or existing.ngsm_token or ""),
            raw_login=dict(result),
            raw_user_info=existing.raw_user_info,
        )

    def _session_from_user_info(self, result: Mapping[str, Any], *, existing: AndroidToySession) -> AndroidToySession:
        body = find_first(result, "result")
        if not isinstance(body, Mapping):
            body = result
        np_sn = as_int(find_first(body, "npSN", "npsn", "npsnString")) or existing.np_sn
        return AndroidToySession(
            np_sn=np_sn,
            guid=str(find_first(body, "guid") or existing.guid or np_sn or ""),
            np_token=str(find_first(body, "npToken", "nptoken") or existing.np_token or ""),
            npa_code=str(find_first(body, "npaCode", "npacode") or existing.npa_code or ""),
            session_token=existing.session_token,
            um_key=existing.um_key,
            member_id=existing.member_id,
            member_type=existing.member_type,
            ngsm_token=str(find_first(body, "ngsmToken", "ngsm_token") or existing.ngsm_token or ""),
            raw_login=existing.raw_login,
            raw_user_info=dict(result),
        )


def is_email(value: str) -> bool:
    return bool(EMAIL_RE.match(value or ""))


def _latin1_headers(headers: Mapping[str, Any]) -> dict[str, str]:

    normalized: dict[str, str] = {}
    for key, value in headers.items():
        normalized[str(key)] = str(value).encode("latin-1", errors="ignore").decode("latin-1")
    return normalized


def current_timezone_offset_hours() -> str:
    import datetime as _dt

    offset = _dt.datetime.now().astimezone().utcoffset()
    if offset is None:
        return "0"
    return str(int(offset.total_seconds() // 3600))


def android_session_to_dict(session: AndroidToySession) -> dict[str, Any]:
    return asdict(session)

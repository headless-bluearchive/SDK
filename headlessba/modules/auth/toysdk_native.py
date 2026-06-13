"""ctypes wrapper for the TOYSDK gamescale.core.dll auth exports."""

from __future__ import annotations

import ctypes
import json
import os
import threading
import uuid
import time
import webbrowser
from collections import deque
from pathlib import Path
from typing import Any, Callable, Mapping

from headlessba.config.paths import DEFAULT_BLUEARCHIVE_CORE_PACKET_DIR
from headlessba.modules.auth.toysdk_models import NativeCallbackResult, ToySdkLoginResult, ToySdkTicketResult


DEFAULT_GAME_ROOT = DEFAULT_BLUEARCHIVE_CORE_PACKET_DIR
DEFAULT_PLUGIN_DIR = DEFAULT_GAME_ROOT / "BlueArchive_Data" / "Plugins" / "x86_64"
DEFAULT_NATIVE_DLL = DEFAULT_PLUGIN_DIR / "gamescale.core.dll"
DEFAULT_TOY_UA = "UnityEngine/2021.3.56f2 TOYSDK-PC/1.3.132 GSSDK-Windows/1.3.132"

CALLBACK = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.c_char_p)
CALLBACK_ID = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p)


class ToySdkNativeError(RuntimeError):
    pass


class _Waiter:
    def __init__(self) -> None:
        self.event = threading.Event()
        self.result: NativeCallbackResult | None = None
        self.callback = CALLBACK(self._on_callback)
        self.callback_id = CALLBACK_ID(self._on_callback_id)

    def _decode_payload(self, payload: bytes | None) -> str:
        if not payload:
            return ""
        return payload.decode("utf-8", errors="replace")

    def _finish(self, handle: int | None, callback_id: int | None, payload: bytes | None) -> None:
        text = self._decode_payload(payload)
        try:
            parsed = json.loads(text) if text else None
        except json.JSONDecodeError:
            parsed = None
        self.result = NativeCallbackResult(
            payload=text,
            parsed=parsed,
            handle=handle,
            callback_id=callback_id,
        )
        self.event.set()

    def _on_callback(self, handle: int, payload: bytes | None) -> None:
        self._finish(int(handle) if handle else None, None, payload)

    def _on_callback_id(self, handle: int, callback_id: int, payload: bytes | None) -> None:
        self._finish(int(handle) if handle else None, int(callback_id), payload)

    def wait(self, timeout: float, label: str) -> NativeCallbackResult:
        if not self.event.wait(timeout):
            raise TimeoutError(f"timeout waiting for TOYSDK callback: {label}")
        if self.result is None:
            raise ToySdkNativeError(f"TOYSDK callback finished without result: {label}")
        return self.result


class _CallbackQueue:
    def __init__(self) -> None:
        self.event = threading.Event()
        self.results: deque[NativeCallbackResult] = deque()
        self.callback = CALLBACK(self._on_callback)
        self.callback_id = CALLBACK_ID(self._on_callback_id)
        self._lock = threading.Lock()

    def _decode_payload(self, payload: bytes | None) -> str:
        if not payload:
            return ""
        return payload.decode("utf-8", errors="replace")

    def _push(self, handle: int | None, callback_id: int | None, payload: bytes | None) -> None:
        text = self._decode_payload(payload)
        try:
            parsed = json.loads(text) if text else None
        except json.JSONDecodeError:
            parsed = None
        result = NativeCallbackResult(payload=text, parsed=parsed, handle=handle, callback_id=callback_id)
        with self._lock:
            self.results.append(result)
            self.event.set()

    def _on_callback(self, handle: int, payload: bytes | None) -> None:
        self._push(int(handle) if handle else None, None, payload)

    def _on_callback_id(self, handle: int, callback_id: int, payload: bytes | None) -> None:
        self._push(int(handle) if handle else None, int(callback_id), payload)

    def wait_next(self, timeout: float, label: str) -> NativeCallbackResult:
        deadline = time.monotonic() + timeout
        while True:
            with self._lock:
                if self.results:
                    result = self.results.popleft()
                    if not self.results:
                        self.event.clear()
                    return result
                self.event.clear()
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not self.event.wait(remaining):
                raise TimeoutError(f"timeout waiting for TOYSDK callback: {label}")

    def wait_until_key(self, key: str, timeout: float, label: str) -> NativeCallbackResult:
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"timeout waiting for TOYSDK callback key={key}: {label}")
            result = self.wait_next(remaining, label)
            if _find_first(result.parsed, key) is not None:
                return result


def _cstr(value: str | bytes | None) -> bytes:
    if value is None:
        return b""
    if isinstance(value, bytes):
        return value
    return value.encode("utf-8")


def _find_first(obj: Any, *names: str) -> Any:
    wanted = {name.lower() for name in names}
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            if str(key).lower() in wanted:
                return value
        for value in obj.values():
            found = _find_first(value, *names)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = _find_first(item, *names)
            if found is not None:
                return found
    return None


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_ticket_result(callback: NativeCallbackResult) -> ToySdkTicketResult:
    ticket = _as_str(_find_first(callback.parsed, "ticket", "insignTicket", "linkTicket"))
    if not ticket:
        raise ToySdkNativeError(f"TOYSDK ticket result missing ticket; raw={callback.payload[:1000]}")
    return ToySdkTicketResult(ticket=ticket, callback=callback)


def parse_login_result(callback: NativeCallbackResult) -> ToySdkLoginResult:
    parsed = callback.parsed
    um_key = _as_str(_find_first(parsed, "umKey", "um_key"))
    member_type = _as_str(_find_first(parsed, "memberType", "member_type"))
    member_id = _as_str(_find_first(parsed, "memberId", "member_id"))
    if um_key and ":" in um_key:
        inferred_type, inferred_id = um_key.split(":", 1)
        member_type = member_type or inferred_type
        member_id = member_id or inferred_id
    return ToySdkLoginResult(
        np_sn=_as_int(_find_first(parsed, "npSN", "npsn")),
        np_token=_as_str(_find_first(parsed, "npToken", "nptoken")),
        npa_code=_as_str(_find_first(parsed, "npaCode", "npacode", "npa_code")),
        session_token=_as_str(_find_first(parsed, "sessionToken", "session_token")),
        guid=_as_str(_find_first(parsed, "guid")),
        member_id=member_id,
        member_type=member_type,
        um_key=um_key,
        game_token=_as_str(_find_first(parsed, "gameToken", "game_token")),
        callback=callback,
    )


def merge_login_results(*results: ToySdkLoginResult | None) -> ToySdkLoginResult:
    """Merge partial TOYSDK auth callbacks into one game-login result."""

    present = [result for result in results if result is not None]
    if not present:
        raise ToySdkNativeError("cannot merge empty TOYSDK login results")

    def first_int(name: str) -> int | None:
        for result in reversed(present):
            value = getattr(result, name)
            if value is not None:
                return int(value)
        return None

    def first_str(name: str) -> str:
        for result in reversed(present):
            value = getattr(result, name)
            if value:
                return str(value)
        return ""

    callback = next((result.callback for result in reversed(present) if result.callback is not None), None)
    return ToySdkLoginResult(
        np_sn=first_int("np_sn"),
        np_token=first_str("np_token"),
        npa_code=first_str("npa_code"),
        session_token=first_str("session_token"),
        guid=first_str("guid"),
        member_id=first_str("member_id"),
        member_type=first_str("member_type"),
        um_key=first_str("um_key"),
        game_token=first_str("game_token"),
        callback=callback,
    )


def _compact_json(value: Any) -> str:
    if value is None:
        value = []
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _token_type_for_source(source: str) -> str:
    if source == "ticket":
        return "x-ias-ticket"
    if source == "game-token":
        return "x-ias-game-token"
    raise ValueError("token source must be one of: game-token, ticket")


def _login_terms_json(login: ToySdkLoginResult) -> tuple[str, str]:
    parsed = login.callback.parsed if login.callback else None
    terms = _find_first(parsed, "terms")
    terms_agree = _find_first(parsed, "termsAgree", "terms_agree")
    all_terms = _find_first(parsed, "all_terms", "allTerms")

    terms_list = terms if isinstance(terms, list) and terms else terms_agree
    if not isinstance(terms_list, list):
        terms_list = []
    if not isinstance(all_terms, list):
        all_terms = terms_list
    return _compact_json(terms_list), _compact_json(all_terms)


def _login_agreed_term_ids_json(login: ToySdkLoginResult) -> str:
    parsed = login.callback.parsed if login.callback else None
    terms = _find_first(parsed, "terms")
    terms_agree = _find_first(parsed, "termsAgree", "terms_agree")
    terms_list = terms if isinstance(terms, list) and terms else terms_agree
    if not isinstance(terms_list, list):
        return "[]"

    ids: list[int] = []
    for term in terms_list:
        if isinstance(term, Mapping):
            raw_id = _find_first(term, "termID", "termId", "termsID", "termsId", "id")
            raw_agree = _find_first(term, "isAgree", "is_agree")
            try:
                term_id = int(raw_id)
            except (TypeError, ValueError):
                continue
            try:
                is_agree = 1 if raw_agree is None else int(raw_agree)
            except (TypeError, ValueError):
                is_agree = 0
            if is_agree == 1:
                ids.append(term_id)
            continue
        try:
            ids.append(int(term))
        except (TypeError, ValueError):
            continue
    return _compact_json(ids)


def _normalize_agree_mode(agree_mode: str, agree_terms: bool) -> str:
    if agree_terms and agree_mode == "none":
        return "game-token-all"
    if agree_mode not in {"none", "ticket", "game-token-all"}:
        raise ValueError("agree_mode must be one of: none, ticket, game-token-all")
    return agree_mode


class ToySdkNative:
    """Small synchronous facade over gamescale.core.dll callback APIs."""

    def __init__(
        self,
        *,
        dll_path: str | Path = DEFAULT_NATIVE_DLL,
        game_root: str | Path = DEFAULT_GAME_ROOT,
        env: str = "live",
        instance_id: str | None = None,
        debug_stage_value: int = 0,
        use_logger: bool = False,
        country: str = "TW",
        locale: str = "zh-TW",
        os_name: str = "Windows",
        oe: str = "PC",
        values: Mapping[str, str] | None = None,
    ) -> None:
        self.dll_path = Path(dll_path).resolve()
        self.game_root = Path(game_root).resolve()
        self.env = env
        self.instance_id = instance_id or str(uuid.uuid4())
        self.debug_stage_value = int(debug_stage_value)
        self.use_logger = bool(use_logger)
        self.country = country
        self.locale = locale
        self.os_name = os_name
        self.oe = oe
        self.values = dict(values or {})
        self._dll: Any = None
        self._inface: int | None = None
        self._game_auth: int | None = None
        self._toy_service: int | None = None
        self._dll_dirs: list[Any] = []
        self._waiters: list[_Waiter] = []
        self._queues: list[_CallbackQueue] = []
        self._old_cwd: str | None = None
        self.last_partial_login: ToySdkLoginResult | None = None
        self.last_game_token_callback: NativeCallbackResult | None = None
        self.last_agree_terms_callback: NativeCallbackResult | None = None
        self.last_sign_in_with_ticket_login: ToySdkLoginResult | None = None
        self.last_sign_in_with_ticket_callback: NativeCallbackResult | None = None
        self.last_sign_in_with_web_token_callback: NativeCallbackResult | None = None
        self.last_toy_sdk_keys_callback: NativeCallbackResult | None = None
        self.last_toy_trusted_device_callback: NativeCallbackResult | None = None

    def __enter__(self) -> "ToySdkNative":
        self.open()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def open(self) -> None:
        if self._dll is not None:
            return
        if not self.dll_path.exists():
            raise FileNotFoundError(f"gamescale.core.dll not found: {self.dll_path}")
        if hasattr(os, "add_dll_directory"):
            for path in (self.dll_path.parent, self.game_root):
                if path.exists():
                    self._dll_dirs.append(os.add_dll_directory(str(path)))
        self._old_cwd = os.getcwd()
        os.chdir(str(self.game_root))
        self._dll = ctypes.WinDLL(str(self.dll_path))
        self._bind_exports()
        self._create_handles()
        self._apply_base_values()

    def close(self) -> None:
        if self._dll is not None:
            if self._toy_service:
                try:
                    self._dll.DestroyToyService(ctypes.c_void_p(self._toy_service))
                except Exception:
                    pass
                self._toy_service = None
            if self._game_auth:
                try:
                    self._dll.DestroyGameAuth(ctypes.c_void_p(self._game_auth))
                except Exception:
                    pass
                self._game_auth = None
            if self._inface:
                try:
                    self._dll.DestroyInface(ctypes.c_void_p(self._inface))
                except Exception:
                    pass
                self._inface = None
        self._dll = None
        for handle in self._dll_dirs:
            try:
                handle.close()
            except Exception:
                pass
        self._dll_dirs = []
        if self._old_cwd:
            os.chdir(self._old_cwd)
            self._old_cwd = None

    def initialize(
        self,
        *,
        launch_platform_type: int = 3,
        request_key: int = 1,
        timeout: float = 30.0,
    ) -> tuple[NativeCallbackResult, NativeCallbackResult]:
        self._require_handles()
        inface_waiter = self._new_waiter()
        self._dll.InfaceInitialize(ctypes.c_void_p(self._inface), int(request_key), inface_waiter.callback_id)
        inface_result = inface_waiter.wait(timeout, "InfaceInitialize")

        game_waiter = self._new_waiter()
        self._dll.GameAuthInsignInitialize(
            ctypes.c_void_p(self._game_auth),
            int(launch_platform_type),
            int(request_key + 1),
            game_waiter.callback_id,
        )
        game_result = game_waiter.wait(timeout, "GameAuthInsignInitialize")
        return inface_result, game_result

    def set_value(self, key: str, value: str) -> None:
        self._require_handles()
        self._dll.InfaceSetValue(ctypes.c_void_p(self._inface), _cstr(key), _cstr(value))

    def get_ticket_with_web_token(self, web_token: str, *, timeout: float = 60.0) -> ToySdkTicketResult:
        self._require_handles()
        waiter = self._new_waiter()
        self._dll.GameAuthInsignGetTicketWithWebToken(
            ctypes.c_void_p(self._game_auth),
            _cstr(web_token),
            waiter.callback,
        )
        return parse_ticket_result(waiter.wait(timeout, "GameAuthInsignGetTicketWithWebToken"))

    def open_port_for_insign(self, *, port: int = 12121, timeout: float = 60.0) -> tuple[NativeCallbackResult, _CallbackQueue]:
        self._require_handles()
        queue = self._new_queue()
        self._dll.GameAuthInsignOpenPortForInsign(
            ctypes.c_void_p(self._game_auth),
            int(port),
            queue.callback,
        )
        return queue.wait_next(timeout, "GameAuthInsignOpenPortForInsign"), queue

    def close_port_for_insign(self) -> None:
        self._require_handles()
        self._dll.GameAuthInsignClosePortForInsign(ctypes.c_void_p(self._game_auth))

    def get_sdk_keys(
        self,
        *,
        request_key: int = 9001,
        timeout: float = 30.0,
    ) -> NativeCallbackResult:
        self._require_toy_service()
        waiter = self._new_waiter()
        self._dll.ToyServiceGetSdkKeys(
            ctypes.c_void_p(self._toy_service),
            int(request_key),
            waiter.callback_id,
        )
        callback = waiter.wait(timeout, "ToyServiceGetSdkKeys")
        self.last_toy_sdk_keys_callback = callback
        return callback

    def trusted_device_get_registered_status(
        self,
        token: str,
        *,
        guid: str = "",
        toy_version: str = "1.3.132",
        request_key: int = 9002,
        timeout: float = 30.0,
    ) -> tuple[dict[str, str], NativeCallbackResult]:
        self._require_toy_service()
        if guid:
            self.set_value("guid", guid)
        payload = {
            "token": token,
            "toy_version": toy_version,
        }
        waiter = self._new_waiter()
        self._dll.ToyServiceTrustedDeviceGetRegisteredStatus(
            ctypes.c_void_p(self._toy_service),
            int(request_key),
            _cstr(_compact_json(payload)),
            waiter.callback_id,
        )
        callback = waiter.wait(timeout, "ToyServiceTrustedDeviceGetRegisteredStatus")
        self.last_toy_trusted_device_callback = callback
        return payload, callback

    def login_with_native_web(
        self,
        *,
        gid: str = "2079",
        port: int = 12121,
        launch_platform_type: int = 3,
        signin_base_url: str = "https://signin.nexon.com/signin?type=ingame",
        store_type: str = "steam",
        package_name: str = "",
        security_token: str = "",
        timeout: float = 120.0,
        open_browser: bool = True,
        browser_opener: Callable[[str], Any] | None = None,
        browser_cleanup: Callable[[Any], None] | None = None,
        stage_callback: Callable[[str, Any], None] | None = None,
        after_web_callback_delay: float = 0.5,
        agree_terms: bool = False,
        agree_mode: str = "ticket",
        sign_in_with_ticket: bool = False,
        sign_in_with_web_token: bool = False,
    ) -> tuple[ToySdkTicketResult, ToySdkLoginResult, str, NativeCallbackResult]:
        agree_mode = _normalize_agree_mode(agree_mode, agree_terms)
        self.initialize(launch_platform_type=launch_platform_type, timeout=timeout)
        open_result, queue = self.open_port_for_insign(port=port, timeout=timeout)
        if stage_callback is not None:
            stage_callback("native_open_port_result", open_result)
        result = _find_first(open_result.parsed, "result") or open_result.parsed
        resolved_port = _as_int(_find_first(result, "port")) or port
        hsid = _as_str(_find_first(result, "hsid"))
        if not hsid:
            raise ToySdkNativeError(f"TOYSDK open-port result missing hsid; raw={open_result.payload[:1000]}")

        url = (
            f"{signin_base_url}&port={resolved_port}&hsid={hsid}&gid={gid}"
            f"&locale={self.locale}&country={self.country}"
        )
        browser_handle: Any = None
        try:
            if browser_opener is not None:
                browser_handle = browser_opener(url)
            elif open_browser:
                webbrowser.open(url)

            web_callback = queue.wait_until_key("web_token", timeout, "GameAuthInsignOpenPortForInsign web_token")
            if stage_callback is not None:
                stage_callback("native_web_callback", web_callback)
            if after_web_callback_delay > 0:
                time.sleep(after_web_callback_delay)

            web_token = _as_str(_find_first(web_callback.parsed, "web_token", "webToken"))
            if not web_token:
                raise ToySdkNativeError(f"TOYSDK native web callback missing web_token; raw={web_callback.payload[:1000]}")
            ticket = self.get_ticket_with_web_token(web_token, timeout=timeout)
            if stage_callback is not None:
                stage_callback("toy_ticket_result", ticket)
            partial_login = self.login_with_ticket(
                ticket.ticket,
                store_type=store_type,
                package_name=package_name,
                security_token=security_token,
                timeout=timeout,
            )
            self.last_partial_login = partial_login
            if stage_callback is not None:
                stage_callback("toy_partial_login_result", partial_login)
            guid = partial_login.guid or str(partial_login.np_sn or "")
            base_login = ToySdkLoginResult(
                np_sn=partial_login.np_sn,
                np_token=partial_login.np_token,
                npa_code=partial_login.npa_code,
                session_token=partial_login.session_token,
                guid=partial_login.guid,
                member_id=partial_login.member_id,
                member_type=partial_login.member_type,
                game_token="",
                callback=partial_login.callback,
            )

            sign_in_ticket_login: ToySdkLoginResult | None = None
            if sign_in_with_ticket:
                sign_in_ticket_login = self.sign_in_with_ticket(
                    ticket.ticket,
                    store_type=store_type,
                    package_name=package_name,
                    security_token=security_token,
                    timeout=timeout,
                )
                if stage_callback is not None:
                    stage_callback("toy_sign_in_with_ticket_result", sign_in_ticket_login)

            agree_login: ToySdkLoginResult | None = None
            terms_source = sign_in_ticket_login or partial_login
            terms_list_json, all_terms_json = _login_terms_json(terms_source)
            if agree_mode == "ticket":
                agree_callback = self.agree_terms_with_ticket(
                    ticket.ticket,
                    terms_list_json=_login_agreed_term_ids_json(terms_source),
                    timeout=timeout,
                )
                if stage_callback is not None:
                    stage_callback("toy_agree_terms_result", agree_callback)
                agree_parsed = parse_login_result(agree_callback)
                agree_login = ToySdkLoginResult(
                    np_sn=agree_parsed.np_sn or partial_login.np_sn,
                    np_token=agree_parsed.np_token,
                    npa_code=agree_parsed.npa_code or partial_login.npa_code,
                    session_token=agree_parsed.session_token or partial_login.session_token,
                    guid=agree_parsed.guid or guid,
                    member_id=agree_parsed.member_id or partial_login.member_id,
                    member_type=agree_parsed.member_type or partial_login.member_type,
                    game_token=agree_parsed.game_token,
                    callback=agree_parsed.callback,
                )

            game_token, game_token_callback = self.get_game_token(ticket.ticket, timeout=timeout)
            if stage_callback is not None:
                stage_callback("toy_game_token_result", game_token_callback)
            game_token_login = ToySdkLoginResult(
                np_sn=None,
                np_token="",
                npa_code="",
                session_token="",
                guid=guid,
                game_token=game_token,
                callback=game_token_callback,
            )
            if agree_mode == "game-token-all" and guid and game_token:
                agree_callback = self.agree_terms_with_game_token_and_all_terms(
                    guid,
                    game_token,
                    terms_list_json=terms_list_json,
                    all_terms_json=all_terms_json,
                    timeout=timeout,
                )
                if stage_callback is not None:
                    stage_callback("toy_agree_terms_result", agree_callback)
                agree_parsed = parse_login_result(agree_callback)
                agree_login = ToySdkLoginResult(
                    np_sn=agree_parsed.np_sn,
                    np_token=agree_parsed.np_token,
                    npa_code=agree_parsed.npa_code,
                    session_token=agree_parsed.session_token,
                    guid=agree_parsed.guid or guid,
                    member_id=agree_parsed.member_id,
                    member_type=agree_parsed.member_type,
                    game_token=agree_parsed.game_token or game_token,
                    callback=agree_parsed.callback,
                )

            final_login: ToySdkLoginResult | None = None
            if sign_in_with_web_token:
                final_login = self.sign_in_with_web_token(
                    web_token,
                    guid=guid,
                    game_token=game_token,
                    store_type=store_type,
                    package_name=package_name,
                    security_token=security_token,
                    timeout=timeout,
                )
                if stage_callback is not None:
                    stage_callback("toy_sign_in_with_web_token_result", final_login)
            return (
                ticket,
                merge_login_results(base_login, sign_in_ticket_login, agree_login, game_token_login, final_login),
                url,
                web_callback,
            )
        finally:
            try:
                self.close_port_for_insign()
            except Exception:
                pass
            if browser_handle is not None and browser_cleanup is not None:
                browser_cleanup(browser_handle)

    def login_with_ticket(
        self,
        ticket: str,
        *,
        store_type: str = "steam",
        package_name: str = "",
        security_token: str = "",
        timeout: float = 60.0,
    ) -> ToySdkLoginResult:
        self._require_handles()
        waiter = self._new_waiter()
        self._dll.GameAuthInsignLogin(
            ctypes.c_void_p(self._game_auth),
            _cstr(ticket),
            _cstr(store_type),
            _cstr(package_name),
            _cstr(security_token),
            waiter.callback,
        )
        return parse_login_result(waiter.wait(timeout, "GameAuthInsignLogin"))

    def get_token(self, ticket: str, *, timeout: float = 60.0) -> NativeCallbackResult:
        self._require_handles()
        waiter = self._new_waiter()
        self._dll.GameAuthInsignGetToken(ctypes.c_void_p(self._game_auth), _cstr(ticket), waiter.callback)
        return waiter.wait(timeout, "GameAuthInsignGetToken")

    def get_game_token(self, ticket: str, *, timeout: float = 60.0) -> tuple[str, NativeCallbackResult]:
        callback = self.get_token(ticket, timeout=timeout)
        game_token = _as_str(_find_first(callback.parsed, "gameToken", "game_token", "token", "accessToken"))
        if not game_token and isinstance(callback.parsed, Mapping):
            result = callback.parsed.get("result")
            if isinstance(result, str):
                game_token = result
        if not game_token:
            raise ToySdkNativeError(f"TOYSDK get-token result missing gameToken; raw={callback.payload[:1000]}")
        self.last_game_token_callback = callback
        return game_token, callback

    def get_game_token_by_scheduler(
        self,
        ticket: str,
        *,
        request_key: int = 2001,
        timeout: float = 60.0,
    ) -> tuple[str, NativeCallbackResult]:
        self._require_handles()
        waiter = self._new_waiter()
        self._dll.GameAuthInsignGetGameTokenByScheduler(
            ctypes.c_void_p(self._game_auth),
            int(request_key),
            _cstr(ticket),
            waiter.callback_id,
        )
        callback = waiter.wait(timeout, "GameAuthInsignGetGameTokenByScheduler")
        game_token = _as_str(_find_first(callback.parsed, "gameToken", "game_token", "token", "accessToken"))
        if not game_token and isinstance(callback.parsed, Mapping):
            result = callback.parsed.get("result")
            if isinstance(result, str):
                game_token = result
        if not game_token:
            raise ToySdkNativeError(f"TOYSDK scheduler-token result missing gameToken; raw={callback.payload[:1000]}")
        return game_token, callback

    def get_ticket_with_npp(self, npp: str, *, timeout: float = 60.0) -> ToySdkTicketResult:
        self._require_handles()
        waiter = self._new_waiter()
        self._dll.GameAuthInsignGetTicketWithNPP(
            ctypes.c_void_p(self._game_auth),
            _cstr(npp),
            waiter.callback,
        )
        return parse_ticket_result(waiter.wait(timeout, "GameAuthInsignGetTicketWithNPP"))

    def web_ticket_by_game_token(
        self,
        game_token: str,
        *,
        request_key: int = 3001,
        timeout: float = 60.0,
    ) -> NativeCallbackResult:
        self._require_handles()
        waiter = self._new_waiter()
        self._dll.GameAuthInsignWebTicketByGameToken(
            ctypes.c_void_p(self._game_auth),
            int(request_key),
            _cstr(game_token),
            waiter.callback_id,
        )
        return waiter.wait(timeout, "GameAuthInsignWebTicketByGameToken")

    def web_ticket_by_game_token_with_version(
        self,
        game_token: str,
        *,
        api_version: int = 1,
        request_key: int = 3002,
        timeout: float = 60.0,
    ) -> NativeCallbackResult:
        self._require_handles()
        waiter = self._new_waiter()
        self._dll.GameAuthInsignWebTicketByGameTokenWithVersion(
            ctypes.c_void_p(self._game_auth),
            int(request_key),
            _cstr(game_token),
            int(api_version),
            waiter.callback_id,
        )
        return waiter.wait(timeout, "GameAuthInsignWebTicketByGameTokenWithVersion")

    def account_link_state_nonce(
        self,
        *,
        request_key: int = 4001,
        timeout: float = 60.0,
    ) -> NativeCallbackResult:
        self._require_handles()
        waiter = self._new_waiter()
        self._dll.GameAuthAccountLinkStateNonce(
            ctypes.c_void_p(self._game_auth),
            int(request_key),
            waiter.callback_id,
        )
        return waiter.wait(timeout, "GameAuthAccountLinkStateNonce")

    def account_link_fetch_linked_account(
        self,
        token: str,
        *,
        token_type: str = "x-ias-game-token",
        trace_id: str | None = None,
        request_key: int = 4002,
        timeout: float = 60.0,
    ) -> tuple[dict[str, str], NativeCallbackResult]:
        self._require_handles()
        payload = {
            "trace_id": trace_id or str(uuid.uuid4()),
            "token_type": token_type,
            "token": token,
        }
        waiter = self._new_waiter()
        self._dll.GameAuthAccountLinkFetchLinkedAccount(
            ctypes.c_void_p(self._game_auth),
            int(request_key),
            _cstr(_compact_json(payload)),
            waiter.callback_id,
        )
        return payload, waiter.wait(timeout, "GameAuthAccountLinkFetchLinkedAccount")

    def account_link_update_primary_link(
        self,
        token: str,
        *,
        platform_type: str,
        platform_user_id: str,
        platform_guid: str,
        token_type: str = "x-ias-game-token",
        trace_id: str | None = None,
        request_key: int = 4003,
        timeout: float = 60.0,
    ) -> tuple[dict[str, str], NativeCallbackResult]:
        self._require_handles()
        payload = {
            "trace_id": trace_id or str(uuid.uuid4()),
            "token_type": token_type,
            "token": token,
            "primary_platform_type": platform_type,
            "primary_platform_user_id": platform_user_id,
            "primary_platform_guid": platform_guid,
            "guid": platform_guid,
        }
        waiter = self._new_waiter()
        self._dll.GameAuthAccountLinkUpdatePrimaryLink(
            ctypes.c_void_p(self._game_auth),
            int(request_key),
            _cstr(_compact_json(payload)),
            waiter.callback_id,
        )
        return payload, waiter.wait(timeout, "GameAuthAccountLinkUpdatePrimaryLink")

    def agree_terms_with_ticket(
        self,
        ticket: str,
        *,
        terms_list_json: str = "[]",
        iiv_key: str = "",
        timeout: float = 60.0,
    ) -> NativeCallbackResult:
        self._require_handles()
        waiter = self._new_waiter()
        self._dll.GameAuthInsignAgreeTermsWithTicket(
            ctypes.c_void_p(self._game_auth),
            _cstr(ticket),
            _cstr(terms_list_json),
            _cstr(iiv_key),
            waiter.callback,
        )
        callback = waiter.wait(timeout, "GameAuthInsignAgreeTermsWithTicket")
        self.last_agree_terms_callback = callback
        return callback

    def agree_terms_with_game_token(
        self,
        game_token: str,
        *,
        terms_list_json: str = "[]",
        iiv_key: str = "",
        timeout: float = 60.0,
    ) -> NativeCallbackResult:
        self._require_handles()
        waiter = self._new_waiter()
        self._dll.GameAuthInsignAgreeTermsWithGameToken(
            ctypes.c_void_p(self._game_auth),
            _cstr(game_token),
            _cstr(terms_list_json),
            _cstr(iiv_key),
            waiter.callback,
        )
        callback = waiter.wait(timeout, "GameAuthInsignAgreeTermsWithGameToken")
        self.last_agree_terms_callback = callback
        return callback

    def agree_terms_with_game_token_and_all_terms(
        self,
        guid: str,
        game_token: str,
        *,
        terms_list_json: str = "[]",
        all_terms_json: str = "[]",
        iiv_key: str = "",
        timeout: float = 60.0,
    ) -> NativeCallbackResult:
        self._require_handles()
        waiter = self._new_waiter()
        self._dll.GameAuthInsignAgreeTermsWithGameTokenAndAllTerms(
            ctypes.c_void_p(self._game_auth),
            _cstr(guid),
            _cstr(game_token),
            _cstr(terms_list_json),
            _cstr(all_terms_json),
            _cstr(iiv_key),
            waiter.callback,
        )
        callback = waiter.wait(timeout, "GameAuthInsignAgreeTermsWithGameTokenAndAllTerms")
        self.last_agree_terms_callback = callback
        return callback

    def sign_in_with_web_token(
        self,
        web_token: str,
        *,
        guid: str,
        game_token: str,
        store_type: str = "steam",
        package_name: str = "",
        security_token: str = "",
        timeout: float = 60.0,
    ) -> ToySdkLoginResult:
        self._require_handles()
        waiter = self._new_waiter()
        self._dll.GameAuthInsignSignInWithWebToken(
            ctypes.c_void_p(self._game_auth),
            _cstr(web_token),
            _cstr(guid),
            _cstr(game_token),
            _cstr(store_type),
            _cstr(package_name),
            _cstr(security_token),
            waiter.callback,
        )
        callback = waiter.wait(timeout, "GameAuthInsignSignInWithWebToken")
        self.last_sign_in_with_web_token_callback = callback
        login = parse_login_result(callback)
        return ToySdkLoginResult(
            np_sn=login.np_sn,
            np_token=login.np_token,
            npa_code=login.npa_code,
            session_token=login.session_token,
            guid=login.guid or guid,
            member_id=login.member_id,
            member_type=login.member_type,
            game_token=login.game_token or game_token,
            callback=login.callback,
        )

    def sign_in_with_ticket(
        self,
        ticket: str,
        *,
        store_type: str = "steam",
        package_name: str = "",
        security_token: str = "",
        request_key: int = 1001,
        timeout: float = 60.0,
    ) -> ToySdkLoginResult:
        self._require_handles()
        waiter = self._new_waiter()
        payload = _compact_json(
            {
                "ticket": ticket,
                "store_type": store_type,
                "package_name": package_name,
                "securityToken": security_token,
            }
        )
        self._dll.GameAuthInsignSignInWithTicket(
            ctypes.c_void_p(self._game_auth),
            int(request_key),
            _cstr(payload),
            waiter.callback_id,
        )
        callback = waiter.wait(timeout, "GameAuthInsignSignInWithTicket")
        self.last_sign_in_with_ticket_callback = callback
        login = parse_login_result(callback)
        self.last_sign_in_with_ticket_login = login
        return login

    def login_with_web_token(
        self,
        web_token: str,
        *,
        launch_platform_type: int = 3,
        store_type: str = "steam",
        package_name: str = "",
        security_token: str = "",
        timeout: float = 60.0,
        stage_callback: Callable[[str, Any], None] | None = None,
        agree_terms: bool = False,
        agree_mode: str = "ticket",
        sign_in_with_ticket: bool = False,
        sign_in_with_web_token: bool = False,
    ) -> tuple[ToySdkTicketResult, ToySdkLoginResult]:
        agree_mode = _normalize_agree_mode(agree_mode, agree_terms)
        init_results = self.initialize(launch_platform_type=launch_platform_type, timeout=timeout)
        if stage_callback is not None:
            stage_callback("toy_initialize_result", init_results)
        ticket = self.get_ticket_with_web_token(web_token, timeout=timeout)
        if stage_callback is not None:
            stage_callback("toy_ticket_result", ticket)
        partial_login = self.login_with_ticket(
            ticket.ticket,
            store_type=store_type,
            package_name=package_name,
            security_token=security_token,
            timeout=timeout,
        )
        self.last_partial_login = partial_login
        if stage_callback is not None:
            stage_callback("toy_partial_login_result", partial_login)
        guid = partial_login.guid or str(partial_login.np_sn or "")
        base_login = ToySdkLoginResult(
            np_sn=partial_login.np_sn,
            np_token=partial_login.np_token,
            npa_code=partial_login.npa_code,
            session_token=partial_login.session_token,
            guid=partial_login.guid,
            member_id=partial_login.member_id,
            member_type=partial_login.member_type,
            game_token="",
            callback=partial_login.callback,
        )

        sign_in_ticket_login: ToySdkLoginResult | None = None
        if sign_in_with_ticket:
            sign_in_ticket_login = self.sign_in_with_ticket(
                ticket.ticket,
                store_type=store_type,
                package_name=package_name,
                security_token=security_token,
                timeout=timeout,
            )
            if stage_callback is not None:
                stage_callback("toy_sign_in_with_ticket_result", sign_in_ticket_login)

        agree_login: ToySdkLoginResult | None = None
        terms_source = sign_in_ticket_login or partial_login
        terms_list_json, all_terms_json = _login_terms_json(terms_source)
        if agree_mode == "ticket":
            agree_callback = self.agree_terms_with_ticket(
                ticket.ticket,
                terms_list_json=_login_agreed_term_ids_json(terms_source),
                timeout=timeout,
            )
            if stage_callback is not None:
                stage_callback("toy_agree_terms_result", agree_callback)
            agree_parsed = parse_login_result(agree_callback)
            agree_login = ToySdkLoginResult(
                np_sn=agree_parsed.np_sn or partial_login.np_sn,
                np_token=agree_parsed.np_token,
                npa_code=agree_parsed.npa_code or partial_login.npa_code,
                session_token=agree_parsed.session_token or partial_login.session_token,
                guid=agree_parsed.guid or guid,
                member_id=agree_parsed.member_id or partial_login.member_id,
                member_type=agree_parsed.member_type or partial_login.member_type,
                game_token=agree_parsed.game_token,
                callback=agree_parsed.callback,
            )

        game_token, game_token_callback = self.get_game_token(ticket.ticket, timeout=timeout)
        if stage_callback is not None:
            stage_callback("toy_game_token_result", game_token_callback)
        game_token_login = ToySdkLoginResult(
            np_sn=None,
            np_token="",
            npa_code="",
            session_token="",
            guid=guid,
            game_token=game_token,
            callback=game_token_callback,
        )
        if agree_mode == "game-token-all" and guid and game_token:
            agree_callback = self.agree_terms_with_game_token_and_all_terms(
                guid,
                game_token,
                terms_list_json=terms_list_json,
                all_terms_json=all_terms_json,
                timeout=timeout,
            )
            if stage_callback is not None:
                stage_callback("toy_agree_terms_result", agree_callback)
            agree_parsed = parse_login_result(agree_callback)
            agree_login = ToySdkLoginResult(
                np_sn=agree_parsed.np_sn,
                np_token=agree_parsed.np_token,
                npa_code=agree_parsed.npa_code,
                session_token=agree_parsed.session_token,
                guid=agree_parsed.guid or guid,
                member_id=agree_parsed.member_id,
                member_type=agree_parsed.member_type,
                game_token=agree_parsed.game_token or game_token,
                callback=agree_parsed.callback,
            )

        final_login: ToySdkLoginResult | None = None
        if sign_in_with_web_token:
            final_login = self.sign_in_with_web_token(
                web_token,
                guid=guid,
                game_token=game_token,
                store_type=store_type,
                package_name=package_name,
                security_token=security_token,
                timeout=timeout,
            )
            if stage_callback is not None:
                stage_callback("toy_sign_in_with_web_token_result", final_login)
        return ticket, merge_login_results(base_login, sign_in_ticket_login, agree_login, game_token_login, final_login)

    def _bind_exports(self) -> None:
        d = self._dll
        d.CreateInface.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
        d.CreateInface.restype = ctypes.c_void_p
        d.DestroyInface.argtypes = [ctypes.c_void_p]
        d.DestroyInface.restype = None
        d.CreateGameAuth.argtypes = [ctypes.c_void_p]
        d.CreateGameAuth.restype = ctypes.c_void_p
        d.DestroyGameAuth.argtypes = [ctypes.c_void_p]
        d.DestroyGameAuth.restype = None
        d.CreateToyService.argtypes = [ctypes.c_void_p]
        d.CreateToyService.restype = ctypes.c_void_p
        d.DestroyToyService.argtypes = [ctypes.c_void_p]
        d.DestroyToyService.restype = None

        d.InfaceInitialize.argtypes = [ctypes.c_void_p, ctypes.c_int, CALLBACK_ID]
        d.InfaceInitialize.restype = None
        d.InfaceSetCountry.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        d.InfaceSetLocale.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        d.InfaceSetOS.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        d.InfaceSetOE.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        d.InfaceSetValue.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]

        d.GameAuthInsignInitialize.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, CALLBACK_ID]
        d.GameAuthInsignInitialize.restype = None
        d.GameAuthInsignGetTicketWithWebToken.argtypes = [ctypes.c_void_p, ctypes.c_char_p, CALLBACK]
        d.GameAuthInsignGetTicketWithWebToken.restype = None
        d.GameAuthInsignOpenPortForInsign.argtypes = [ctypes.c_void_p, ctypes.c_int, CALLBACK]
        d.GameAuthInsignOpenPortForInsign.restype = None
        d.GameAuthInsignClosePortForInsign.argtypes = [ctypes.c_void_p]
        d.GameAuthInsignClosePortForInsign.restype = None
        d.GameAuthInsignLogin.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            CALLBACK,
        ]
        d.GameAuthInsignLogin.restype = None
        d.GameAuthInsignGetToken.argtypes = [ctypes.c_void_p, ctypes.c_char_p, CALLBACK]
        d.GameAuthInsignGetToken.restype = None
        d.GameAuthInsignGetGameTokenByScheduler.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_char_p,
            CALLBACK_ID,
        ]
        d.GameAuthInsignGetGameTokenByScheduler.restype = None
        d.GameAuthInsignGetTicketWithNPP.argtypes = [ctypes.c_void_p, ctypes.c_char_p, CALLBACK]
        d.GameAuthInsignGetTicketWithNPP.restype = None
        d.GameAuthInsignWebTicketByGameToken.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_char_p,
            CALLBACK_ID,
        ]
        d.GameAuthInsignWebTicketByGameToken.restype = None
        d.GameAuthInsignWebTicketByGameTokenWithVersion.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            CALLBACK_ID,
        ]
        d.GameAuthInsignWebTicketByGameTokenWithVersion.restype = None
        d.GameAuthInsignSignInWithTicket.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_char_p,
            CALLBACK_ID,
        ]
        d.GameAuthInsignSignInWithTicket.restype = None
        d.GameAuthInsignAgreeTermsWithTicket.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            CALLBACK,
        ]
        d.GameAuthInsignAgreeTermsWithTicket.restype = None
        d.GameAuthInsignAgreeTermsWithGameToken.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            CALLBACK,
        ]
        d.GameAuthInsignAgreeTermsWithGameToken.restype = None
        d.GameAuthInsignAgreeTermsWithGameTokenAndAllTerms.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            CALLBACK,
        ]
        d.GameAuthInsignAgreeTermsWithGameTokenAndAllTerms.restype = None
        d.GameAuthInsignSignInWithWebToken.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            CALLBACK,
        ]
        d.GameAuthInsignSignInWithWebToken.restype = None
        d.GameAuthAccountLinkFetchLinkedAccount.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_char_p,
            CALLBACK_ID,
        ]
        d.GameAuthAccountLinkFetchLinkedAccount.restype = None
        d.GameAuthAccountLinkUpdatePrimaryLink.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_char_p,
            CALLBACK_ID,
        ]
        d.GameAuthAccountLinkUpdatePrimaryLink.restype = None
        d.GameAuthAccountLinkStateNonce.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            CALLBACK_ID,
        ]
        d.GameAuthAccountLinkStateNonce.restype = None
        d.ToyServiceGetSdkKeys.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            CALLBACK_ID,
        ]
        d.ToyServiceGetSdkKeys.restype = None
        d.ToyServiceTrustedDeviceGetRegisteredStatus.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_char_p,
            CALLBACK_ID,
        ]
        d.ToyServiceTrustedDeviceGetRegisteredStatus.restype = None

    def _create_handles(self) -> None:
        self._inface = self._dll.CreateInface(
            _cstr(self.env),
            _cstr(self.instance_id),
            self.debug_stage_value,
            1 if self.use_logger else 0,
        )
        if not self._inface:
            raise ToySdkNativeError("CreateInface returned null")
        self._game_auth = self._dll.CreateGameAuth(ctypes.c_void_p(self._inface))
        if not self._game_auth:
            raise ToySdkNativeError("CreateGameAuth returned null")

    def _apply_base_values(self) -> None:
        self._require_handles()
        d = self._dll
        handle = ctypes.c_void_p(self._inface)
        d.InfaceSetCountry(handle, _cstr(self.country))
        d.InfaceSetLocale(handle, _cstr(self.locale))
        d.InfaceSetOS(handle, _cstr(self.os_name))
        d.InfaceSetOE(handle, _cstr(self.oe))

        defaults = {
            "gid": "2079",
            "serviceId": "2079",
            "clientId": "2079",
            "clientPlatform": "PC",
            "sdkVersion": "1.3.132",
            "userAgent": DEFAULT_TOY_UA,
        }
        defaults.update({key: value for key, value in self.values.items() if value is not None})
        for key, value in defaults.items():
            if value != "":
                d.InfaceSetValue(handle, _cstr(str(key)), _cstr(str(value)))

    def _new_waiter(self) -> _Waiter:
        waiter = _Waiter()
        self._waiters.append(waiter)
        return waiter

    def _new_queue(self) -> _CallbackQueue:
        queue = _CallbackQueue()
        self._queues.append(queue)
        return queue

    def _require_handles(self) -> None:
        if self._dll is None or not self._inface or not self._game_auth:
            raise ToySdkNativeError("TOYSDK native wrapper is not open")

    def _require_toy_service(self) -> None:
        self._require_handles()
        if self._toy_service:
            return
        self._toy_service = self._dll.CreateToyService(ctypes.c_void_p(self._inface))
        if not self._toy_service:
            raise ToySdkNativeError("CreateToyService returned null")

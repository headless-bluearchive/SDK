"""Compare BA login artifacts from different login entry paths."""

from __future__ import annotations

import base64
import binascii
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from modules.auth.nexon_login import NexonGameCredentials, build_credentials
from modules.auth.toysdk_models import ToySdkLoginResult


REQUEST_STAGES = (
    "01_queuing_get_ticket",
    "02_account_check_nexon",
    "03_account_auth",
    "04_account_login_sync",
)
RESPONSE_STAGES = (
    "02_account_check_nexon",
    "03_account_auth",
    "04_account_login_sync",
)

IAS_WEB_TOKEN_RE = re.compile(r"^ias:wt:")
IAS_GAME_TOKEN_RE = re.compile(r"^ias:gt:")
IAS_TICKET_RE = re.compile(r"^ias:t:")
HEX_128_RE = re.compile(r"^[0-9a-fA-F]{128}$")


@dataclass
class LoginArtifactSource:
    label: str
    root: Path
    source_path: Path
    inferred_kind: str
    toy_login: ToySdkLoginResult | None = None
    credentials: NexonGameCredentials | None = None
    toy_login_path: Path | None = None
    selected_web_token: dict[str, Any] | None = None
    session_meta: dict[str, Any] | None = None
    connection_info: dict[str, Any] | None = None
    main_login_flow: dict[str, Any] | None = None
    request_jsons: dict[str, dict[str, Any]] = field(default_factory=dict)
    response_jsons: dict[str, dict[str, Any]] = field(default_factory=dict)
    built_records: dict[str, dict[str, Any]] = field(default_factory=dict)


def load_login_artifact_source(path: str | Path, *, label: str = "") -> LoginArtifactSource:
    source_path = Path(path).resolve()
    root = source_path if source_path.is_dir() else source_path.parent
    inferred_kind = infer_source_kind(root)
    resolved_label = label or (source_path.stem if source_path.is_file() else source_path.name)

    toy_login_path = _resolve_toy_login_path(source_path, root)
    toy_login = _load_toy_login(toy_login_path) if toy_login_path else None
    credentials = None
    if toy_login is not None:
        try:
            credentials = build_credentials(
                toy_login,
                allow_session_token_as_ngsm=True,
                allow_empty_ngsm_token=True,
            )
        except Exception:
            credentials = None

    main_login_flow = _read_json_if_exists(root / "main_login_flow.json")
    source = LoginArtifactSource(
        label=resolved_label,
        root=root,
        source_path=source_path,
        inferred_kind=inferred_kind,
        toy_login=toy_login,
        credentials=credentials,
        toy_login_path=toy_login_path,
        selected_web_token=_read_json_if_exists(root / "selected_web_token.json"),
        session_meta=_read_json_if_exists(root / "session.json"),
        connection_info=_read_json_if_exists(root / "connection_info.json"),
        main_login_flow=main_login_flow,
    )

    flow_steps = _flow_steps_by_name(main_login_flow)

    for stage in REQUEST_STAGES:
        request_path = root / f"{stage}.request.json"
        built_path = root / f"{stage}.built.json"
        request_json = _read_json_if_exists(request_path)
        built_json = _read_json_if_exists(built_path)
        if isinstance(request_json, dict):
            source.request_jsons[stage] = request_json
        elif isinstance(built_json, dict) and isinstance(built_json.get("request_json"), dict):
            source.request_jsons[stage] = built_json["request_json"]
        elif isinstance(flow_steps.get(stage, {}).get("request_json"), dict):
            source.request_jsons[stage] = flow_steps[stage]["request_json"]
        if isinstance(built_json, dict):
            source.built_records[stage] = built_json

    for stage in RESPONSE_STAGES:
        response_json = _read_json_if_exists(root / f"{stage}.response.json")
        if isinstance(response_json, dict):
            source.response_jsons[stage] = response_json

    return source


def compare_login_artifact_sources(
    left: LoginArtifactSource,
    right: LoginArtifactSource,
    *,
    strict_token_values: bool = False,
    strict_environment: bool = False,
) -> dict[str, Any]:
    left_snapshot = source_snapshot(
        left,
        strict_token_values=strict_token_values,
        strict_environment=strict_environment,
    )
    right_snapshot = source_snapshot(
        right,
        strict_token_values=strict_token_values,
        strict_environment=strict_environment,
    )

    identity_cmp = _compare_group(
        left_snapshot["identity"],
        right_snapshot["identity"],
    )
    token_cmp = _compare_group(
        left_snapshot["token_surface"],
        right_snapshot["token_surface"],
    )
    credential_cmp = _compare_group(
        left_snapshot["credentials"],
        right_snapshot["credentials"],
    )

    request_report: dict[str, Any] = {}
    comparable_request_core: list[bool] = []
    comparable_request_env: list[bool] = []
    for stage in REQUEST_STAGES:
        left_request = left.request_jsons.get(stage)
        right_request = right.request_jsons.get(stage)
        if left_request is None or right_request is None:
            request_report[stage] = {
                "available": False,
                "left_present": left_request is not None,
                "right_present": right_request is not None,
            }
            continue
        normalized_left = normalize_request_stage(
            stage,
            left_request,
            strict_token_values=strict_token_values,
            strict_environment=strict_environment,
        )
        normalized_right = normalize_request_stage(
            stage,
            right_request,
            strict_token_values=strict_token_values,
            strict_environment=strict_environment,
        )
        compared = _compare_normalized(normalized_left, normalized_right)
        request_report[stage] = {
            "available": True,
            **compared,
        }
        comparable_request_core.append(compared["core_equal"])
        if compared["environment_equal"] is not None:
            comparable_request_env.append(compared["environment_equal"])

    response_report: dict[str, Any] = {}
    comparable_response_core: list[bool] = []
    for stage in RESPONSE_STAGES:
        left_response = left.response_jsons.get(stage)
        right_response = right.response_jsons.get(stage)
        if left_response is None or right_response is None:
            response_report[stage] = {
                "available": False,
                "left_present": left_response is not None,
                "right_present": right_response is not None,
            }
            continue
        normalized_left = normalize_response_stage(
            stage,
            left_response,
            strict_token_values=strict_token_values,
        )
        normalized_right = normalize_response_stage(
            stage,
            right_response,
            strict_token_values=strict_token_values,
        )
        compared = _compare_normalized(normalized_left, normalized_right)
        response_report[stage] = {
            "available": True,
            **compared,
        }
        comparable_response_core.append(compared["core_equal"])

    identity_match = identity_cmp["equal"] if left.toy_login is not None and right.toy_login is not None else None
    token_surface_match = (
        token_cmp["equal"]
        if (left.toy_login is not None or left.selected_web_token is not None)
        and (right.toy_login is not None or right.selected_web_token is not None)
        else None
    )
    credential_match = credential_cmp["equal"] if left.credentials is not None and right.credentials is not None else None

    request_core_match = all(comparable_request_core) if comparable_request_core else None
    request_environment_match = all(comparable_request_env) if comparable_request_env else None
    response_core_match = all(comparable_response_core) if comparable_response_core else None

    game_surface_components = [value for value in (request_core_match, response_core_match) if value is not None]
    game_surface_core_match = all(game_surface_components) if game_surface_components else None

    return {
        "summary": {
            "same_account_identity": identity_match,
            "pre_game_token_surface_match": token_surface_match,
            "derived_credentials_match": credential_match,
            "game_request_core_match": request_core_match,
            "game_request_environment_match": request_environment_match,
            "game_response_core_match": response_core_match,
            "game_surface_core_match": game_surface_core_match,
            "converges_in_game": (
                identity_match and game_surface_core_match
                if identity_match is not None and game_surface_core_match is not None
                else None
            ),
        },
        "left": left_snapshot,
        "right": right_snapshot,
        "identity_comparison": identity_cmp,
        "token_surface_comparison": token_cmp,
        "credential_comparison": credential_cmp,
        "request_comparison": request_report,
        "response_comparison": response_report,
    }


def source_snapshot(
    source: LoginArtifactSource,
    *,
    strict_token_values: bool = False,
    strict_environment: bool = False,
) -> dict[str, Any]:
    login = source.toy_login
    credentials = source.credentials
    session_meta = source.session_meta or {}
    web_token = ""
    if isinstance(source.selected_web_token, Mapping):
        web_token = str(source.selected_web_token.get("web_token") or "")

    return {
        "label": source.label,
        "root": str(source.root),
        "source_path": str(source.source_path),
        "inferred_kind": source.inferred_kind,
        "toy_login_path": str(source.toy_login_path) if source.toy_login_path else "",
        "available_request_stages": sorted(source.request_jsons),
        "available_response_stages": sorted(source.response_jsons),
        "identity": {
            "npSN": _normalize_numeric(login.np_sn if login else None),
            "guid": _normalize_numeric(login.guid if login else ""),
            "memberId": str(login.member_id if login else ""),
            "memberType": str(login.member_type if login else ""),
            "umKey": str(login.um_key if login else ""),
            "npaCode": str(login.npa_code if login else ""),
        },
        "token_surface": {
            "webToken": token_shape(web_token, strict_value=strict_token_values),
            "npToken": token_shape(login.np_token if login else "", strict_value=strict_token_values),
            "gameToken": token_shape(login.game_token if login else "", strict_value=strict_token_values),
            "sessionToken": token_shape(login.session_token if login else "", strict_value=strict_token_values),
            "ngsmToken": token_shape(login.ngsm_token if login else "", strict_value=strict_token_values),
        },
        "credentials": {
            "npSN": _normalize_numeric(credentials.np_sn if credentials else None),
            "npaCode": str(credentials.npa_code if credentials else ""),
            "npToken": token_shape(credentials.np_token if credentials else "", strict_value=strict_token_values),
            "ngsmToken": token_shape(credentials.ngsm_token if credentials else "", strict_value=strict_token_values),
        },
        "runtime": {
            "country": str(session_meta.get("country") or ""),
            "locale": str(session_meta.get("locale") or ""),
            "gid": str(session_meta.get("gid") or ""),
            "userAgent": str(session_meta.get("user_agent") or ""),
            "strict_environment": strict_environment,
        },
    }


def normalize_request_stage(
    stage: str,
    request: Mapping[str, Any],
    *,
    strict_token_values: bool = False,
    strict_environment: bool = False,
) -> dict[str, dict[str, Any]]:
    session_key = request.get("SessionKey")
    session = session_key if isinstance(session_key, Mapping) else {}
    if stage == "01_queuing_get_ticket":
        return {
            "core": {
                "Protocol": int(request.get("Protocol", 0)),
                "ClientVersion": str(request.get("ClientVersion") or ""),
                "MakeStandby": bool(request.get("MakeStandby", False)),
                "Npacode": str(request.get("Npacode") or ""),
                "NpSN": _normalize_numeric(request.get("NpSN")),
                "NpToken": token_shape(str(request.get("NpToken") or ""), strict_value=strict_token_values),
                "NgsmToken": token_shape(str(request.get("NgsmToken") or ""), strict_value=strict_token_values),
                "OSType": str(request.get("OSType") or ""),
                "PassCheck": bool(request.get("PassCheck", False)),
                "PassCheckNexon": bool(request.get("PassCheckNexon", False)),
            },
            "environment": {},
            "dynamic": {
                "HashPresent": "Hash" in request,
                "AccessIPPresent": bool(str(request.get("AccessIP") or "")),
                "WaitingTicketPresent": bool(str(request.get("WaitingTicket") or "")),
            },
        }

    if stage == "02_account_check_nexon":
        return {
            "core": {
                "Protocol": int(request.get("Protocol", 0)),
                "HasNpSN": "NpSN" in request,
                "NpSN": _normalize_numeric(request.get("NpSN")),
                "HasNpToken": "NpToken" in request,
                "NpToken": token_shape(str(request.get("NpToken") or ""), strict_value=strict_token_values),
                "PassCheckNexonServer": (
                    None if "PassCheckNexonServer" not in request else bool(request.get("PassCheckNexonServer"))
                ),
            },
            "environment": {},
            "dynamic": {
                "HashPresent": "Hash" in request,
                "EnterTicket": value_shape(str(request.get("EnterTicket") or "")),
                "ClientGeneratedKey": value_shape(str(request.get("ClientGeneratedKey") or "")),
                "ClientGeneratedIV": value_shape(str(request.get("ClientGeneratedIV") or "")),
            },
        }

    if stage == "03_account_auth":
        environment: dict[str, Any] = {
            "DeviceModel": str(request.get("DeviceModel") or ""),
            "OSVersion": str(request.get("OSVersion") or ""),
            "DeviceSystemMemorySize": request.get("DeviceSystemMemorySize"),
            "IMEI": request.get("IMEI"),
        }
        if strict_environment:
            environment.update(
                {
                    "DeviceUniqueId": str(request.get("DeviceUniqueId") or ""),
                    "DevId": str(request.get("DevId") or ""),
                    "AdvertisementId": str(request.get("AdvertisementId") or ""),
                    "Idfv": str(request.get("Idfv") or ""),
                }
            )
        else:
            environment.update(
                {
                    "DeviceUniqueIdPresent": bool(str(request.get("DeviceUniqueId") or "")),
                    "DevIdPresent": bool(str(request.get("DevId") or "")),
                    "AdvertisementIdPresent": bool(str(request.get("AdvertisementId") or "")),
                    "IdfvPresent": bool(str(request.get("Idfv") or "")),
                }
            )
        return {
            "core": {
                "Protocol": int(request.get("Protocol", 0)),
                "AccountId": _normalize_numeric(request.get("AccountId")),
                "SessionKey.AccountServerId": _normalize_numeric(session.get("AccountServerId")),
                "Resendable": bool(request.get("Resendable", False)),
                "IsTest": bool(request.get("IsTest", False)),
                "CountryCode": str(request.get("CountryCode") or ""),
                "DeviceLocaleCode": str(request.get("DeviceLocaleCode") or ""),
                "GameOptionLanguage": str(request.get("GameOptionLanguage") or ""),
                "MarketId": str(request.get("MarketId") or ""),
                "OSType": str(request.get("OSType") or ""),
                "IsTeenVersion": bool(request.get("IsTeenVersion", False)),
            },
            "environment": environment,
            "dynamic": {
                "HashPresent": "Hash" in request,
                "AccessIPPresent": bool(str(request.get("AccessIP") or "")),
                "SessionKey.MxToken": token_shape(str(session.get("MxToken") or ""), strict_value=strict_token_values),
            },
        }

    if stage == "04_account_login_sync":
        return {
            "core": {
                "Protocol": int(request.get("Protocol", 0)),
                "AccountId": _normalize_numeric(request.get("AccountId")),
                "SessionKey.AccountServerId": _normalize_numeric(session.get("AccountServerId")),
                "Resendable": bool(request.get("Resendable", False)),
                "IsTest": bool(request.get("IsTest", False)),
                "Fields": _sorted_field_names(request),
            },
            "environment": {},
            "dynamic": {
                "HashPresent": "Hash" in request,
                "SessionKey.MxToken": token_shape(str(session.get("MxToken") or ""), strict_value=strict_token_values),
            },
        }

    raise KeyError(f"unsupported request stage {stage!r}")


def normalize_response_stage(
    stage: str,
    response: Mapping[str, Any],
    *,
    strict_token_values: bool = False,
) -> dict[str, dict[str, Any]]:
    parsed = response.get("parsed")
    payload = parsed if isinstance(parsed, Mapping) else {}
    session_key = payload.get("SessionKey")
    session = session_key if isinstance(session_key, Mapping) else {}

    if stage == "02_account_check_nexon":
        return {
            "core": {
                "Protocol": payload.get("Protocol"),
                "ResultState": payload.get("ResultState"),
                "ErrorCode": payload.get("ErrorCode"),
                "AccountId": _normalize_numeric(payload.get("AccountId")),
                "SessionKey.AccountServerId": _normalize_numeric(session.get("AccountServerId")),
            },
            "environment": {},
            "dynamic": {
                "EncryptedKey": value_shape(str(payload.get("EncryptedKey") or "")),
                "EncryptedIV": value_shape(str(payload.get("EncryptedIV") or "")),
                "SessionKey.MxToken": token_shape(str(session.get("MxToken") or ""), strict_value=strict_token_values),
            },
        }

    if stage in {"03_account_auth", "04_account_login_sync"}:
        stable = {
            "Protocol": payload.get("Protocol"),
            "ErrorCode": payload.get("ErrorCode"),
            "AccountId": _normalize_numeric(_find_first(payload, "AccountId", "accountId")),
            "SessionKey.AccountServerId": _normalize_numeric(session.get("AccountServerId")),
        }
        for key in ("ResultState", "Nickname", "NickName", "Name"):
            if key in payload:
                stable[key] = payload.get(key)
        return {
            "core": stable,
            "environment": {},
            "dynamic": {
                "SessionKey.MxToken": token_shape(str(session.get("MxToken") or ""), strict_value=strict_token_values),
            },
        }

    raise KeyError(f"unsupported response stage {stage!r}")


def token_kind(value: str) -> str:
    text = str(value or "")
    if not text:
        return "empty"
    if IAS_WEB_TOKEN_RE.match(text):
        return "ias-web-token"
    if IAS_GAME_TOKEN_RE.match(text):
        return "ias-game-token"
    if IAS_TICKET_RE.match(text):
        return "ias-ticket"
    if text.startswith("TOU"):
        return "toysdk-token"
    if HEX_128_RE.match(text):
        return "hex128"
    return "other"


def token_shape(value: str, *, strict_value: bool = False) -> dict[str, Any]:
    text = str(value or "")
    shape: dict[str, Any] = {
        "present": bool(text),
        "kind": token_kind(text),
        "length": len(text),
    }
    if text:
        shape["masked"] = _mask_text(text)
    if strict_value:
        shape["value"] = text
    return shape


def value_shape(value: str) -> dict[str, Any]:
    text = str(value or "")
    return {
        "present": bool(text),
        "length": len(text),
        "decoded_length": _safe_base64_decoded_length(text),
        "masked": _mask_text(text) if text else "",
    }


def infer_source_kind(root: Path) -> str:
    if (root / "toy_android_requests.json").exists():
        return "android-http-toysdk"
    if (root / "toy_initialize_result.json").exists() or (root / "toy_game_token_result.json").exists():
        return "native-toysdk"
    if (root / "selected_web_token.json").exists():
        return "web-callback"
    return "generic-artifact-dir"


def write_report(path: str | Path, report: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def _resolve_toy_login_path(source_path: Path, root: Path) -> Path | None:
    if source_path.is_file():
        data = _read_json_if_exists(source_path)
        if isinstance(data, Mapping) and any(key in data for key in ("npSN", "npToken", "npaCode")):
            return source_path
    for name in ("toy_login_summary.json", "toy_login_result.json"):
        candidate = root / name
        if candidate.exists():
            return candidate
    return None


def _load_toy_login(path: Path) -> ToySdkLoginResult:
    data = json.loads(path.read_text(encoding="utf-8"))
    ngsm_token = str(data.get("ngsmToken") or data.get("ngsm_token") or "")
    if not ngsm_token:
        ngsm_token = _load_adjacent_bridge_ngsm_token(path.parent)
    return ToySdkLoginResult(
        np_sn=_to_int(data.get("npSN") or data.get("np_sn")),
        np_token=str(data.get("npToken") or data.get("np_token") or ""),
        npa_code=str(data.get("npaCode") or data.get("npa_code") or ""),
        session_token=str(data.get("sessionToken") or data.get("session_token") or ""),
        guid=str(data.get("guid") or ""),
        member_id=str(data.get("memberId") or data.get("member_id") or ""),
        member_type=str(data.get("memberType") or data.get("member_type") or ""),
        um_key=str(data.get("umKey") or data.get("um_key") or ""),
        game_token=str(data.get("gameToken") or data.get("game_token") or ""),
        ngsm_token=ngsm_token,
        callback=None,
    )


def _compare_normalized(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    core = _compare_group(left.get("core", {}), right.get("core", {}))
    environment = _compare_group(left.get("environment", {}), right.get("environment", {}))
    dynamic = _compare_group(left.get("dynamic", {}), right.get("dynamic", {}))
    return {
        "core_equal": core["equal"],
        "environment_equal": environment["equal"] if environment["left"] or environment["right"] else None,
        "dynamic_equal": dynamic["equal"] if dynamic["left"] or dynamic["right"] else None,
        "core": core,
        "environment": environment,
        "dynamic": dynamic,
    }


def _compare_group(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    left_flat = _flatten_mapping(left)
    right_flat = _flatten_mapping(right)
    all_keys = sorted(set(left_flat) | set(right_flat))
    diffs = []
    for key in all_keys:
        if left_flat.get(key) != right_flat.get(key):
            diffs.append(
                {
                    "path": key,
                    "left": left_flat.get(key),
                    "right": right_flat.get(key),
                }
            )
    return {
        "equal": not diffs,
        "left": left,
        "right": right,
        "diffs": diffs,
    }


def _flatten_mapping(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, Mapping):
        flat: dict[str, Any] = {}
        for key, item in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            flat.update(_flatten_mapping(item, child_prefix))
        return flat
    return {prefix: value}


def _find_first(obj: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in obj:
            return obj[key]
    return None


def _normalize_numeric(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    return text


def _sorted_field_names(request: Mapping[str, Any]) -> list[str]:
    return sorted(str(key) for key in request if key not in {"Hash"})


def _safe_base64_decoded_length(text: str) -> int | None:
    if not text:
        return None
    try:
        padded = text + ("=" * ((4 - (len(text) % 4)) % 4))
        return len(base64.b64decode(padded, validate=False))
    except (binascii.Error, ValueError):
        return None


def _mask_text(text: str, *, head: int = 10, tail: int = 6) -> str:
    if len(text) <= head + tail + 3:
        return text
    return f"{text[:head]}...{text[-tail:]}"


def _flow_steps_by_name(flow: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not isinstance(flow, Mapping):
        return {}
    steps = flow.get("steps")
    if not isinstance(steps, list):
        return {}
    resolved: dict[str, dict[str, Any]] = {}
    for step in steps:
        if not isinstance(step, dict):
            continue
        name = str(step.get("name") or "")
        if name:
            resolved[name] = step
    return resolved


def _load_adjacent_bridge_ngsm_token(directory: Path) -> str:
    for name in ("ngsx_bridge_result.json", "ngsm_bridge_result.json"):
        candidate = directory / name
        if not candidate.exists():
            continue
        data = _read_json_if_exists(candidate)
        if isinstance(data, dict):
            token = _ngsm_token_from_bridge_result(data)
            if token:
                return token
    return ""


def _ngsm_token_from_bridge_result(data: Mapping[str, Any]) -> str:
    direct = str(data.get("ngsmToken") or "")
    if direct:
        return direct
    ngsm_result = data.get("ngsmResult")
    if isinstance(ngsm_result, Mapping):
        token = str(ngsm_result.get("ngsmToken") or "")
        if token:
            return token
    events = data.get("events")
    if isinstance(events, list):
        for event in reversed(events):
            if not isinstance(event, Mapping):
                continue
            if str(event.get("event") or "") != "ngsm-token":
                continue
            token = str(event.get("ngsmToken") or "")
            if token:
                return token
    return ""


def _read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _to_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(str(value), 10)
    except ValueError:
        return None

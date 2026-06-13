"""Android runtime profile discovery for Blue Archive replay.

The collector writes a package-scoped runtime pull with this shape:

```
analysis_reports/android_runtime_pull/ba_YYYYmmdd_HHMMSS/
  external_selected/
  private_selected/shared_prefs/
```

This module keeps parsing local and read-only.  It extracts values that the
Android client already persisted and turns them into stable inputs for the
TOYSDK and main-game Account_Auth replay layers.
"""

from __future__ import annotations

import base64
import json
import re
from dataclasses import asdict, dataclass, field
from html import unescape
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote

from modules.runtime.runtime_config import RuntimeConnectionInfo, discover_connection_info, read_json_if_exists


DEFAULT_ANDROID_RUNTIME_PULL_DIR = Path(__file__).resolve().parents[1] / "analysis_reports" / "android_runtime_pull"


@dataclass(frozen=True)
class AndroidRuntimeProfile:
    source_root: str
    external_dir: str
    shared_prefs_dir: str
    region: str = ""
    server: str = ""
    api_url: str = ""
    gateway_url: str = ""
    gateway_endpoint: str = ""
    connection_source: str = ""
    country: str = ""
    locale: str = ""
    initial_country: str = ""
    user_country: str = ""
    install_country_name: str = ""
    service_client_id: str = ""
    service_client_id_raw: str = ""
    service_title: str = ""
    app_id: str = ""
    client_version: str = ""
    app_version_code: int | None = None
    build_sdk_api_version: int | None = None
    user_agent: str = ""
    device_model: str = ""
    android_os_version: str = ""
    advertising_id: str = ""
    uuid: str = ""
    uuid2: str = ""
    mid: str = ""
    idfv: str = ""
    save_uid: str = ""
    platform_store_uuid: str = ""
    language: str = ""
    voice_language: str = ""
    last_login_type: int | None = None
    use_ngsx: int | None = None
    use_ngsm: int | None = None
    use_gb_krpc: bool | None = None
    use_gb_npsn: bool | None = None
    login_ui_type: str = ""
    nk_member_access_code: str = ""
    terms_api_ver: int | None = None
    policy_api_ver: int | None = None
    mcc: str = ""
    mnc: str = ""
    carrier_name: str = ""
    device_unique_id: str = ""
    device_unique_id_candidates: tuple[str, ...] = field(default_factory=tuple)
    npa_common_path: str = ""
    nx_analytics_path: str = ""
    player_prefs_path: str = ""
    np_account_gcm_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def find_latest_android_runtime_pull(root: str | Path = DEFAULT_ANDROID_RUNTIME_PULL_DIR) -> Path | None:
    base = Path(root).expanduser()
    if not base.exists():
        return None
    if _looks_like_runtime_root(base):
        return base.resolve()
    candidates = [path for path in base.glob("ba_*") if _looks_like_runtime_root(path)]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime).resolve()


def load_android_runtime_profile(root_dir: str | Path | None = None) -> AndroidRuntimeProfile:
    root = resolve_android_runtime_root(root_dir)
    external_dir = root / "external_selected"
    shared_prefs_dir = root / "private_selected" / "shared_prefs"

    connection = _discover_connection(external_dir)
    local_config = read_json_if_exists(external_dir / "LocalConfig.json")
    device_option = read_json_if_exists(external_dir / "DeviceOption")

    npa_path = first_existing(shared_prefs_dir.glob("NPACommon*.xml"))
    analytics_path = first_existing(shared_prefs_dir.glob("NxAnalytics*.xml"))
    player_prefs_path = first_existing(shared_prefs_dir.glob("com.nexon.bluearchive.v2.playerprefs.xml"))
    np_account_gcm_path = first_existing(shared_prefs_dir.glob("NPAccountGCMPref*.xml"))
    platform_store_path = first_existing(shared_prefs_dir.glob("com.nexon.platform.store.internal.preferences.APP_SETTINGS.xml"))

    npa = read_shared_prefs_xml(npa_path) if npa_path else {}
    analytics = read_shared_prefs_xml(analytics_path) if analytics_path else {}
    player_prefs = read_shared_prefs_xml(player_prefs_path) if player_prefs_path else {}
    np_account_gcm = read_shared_prefs_xml(np_account_gcm_path) if np_account_gcm_path else {}
    platform_store = read_shared_prefs_xml(platform_store_path) if platform_store_path else {}

    string_table = local_config.get("StringTable") if isinstance(local_config.get("StringTable"), dict) else {}
    user_agent = as_str(npa.get("userAgent"))
    parsed_ua = parse_android_toy_user_agent(user_agent)
    service_client_id_raw = as_str(npa.get("serviceClientId"))
    service_client_id = decode_base64_ascii(service_client_id_raw) or service_client_id_raw
    save_uid = unquote(as_str(player_prefs.get("SaveUID")))
    uuid_value = as_str(npa.get("uuid"))
    uuid2 = as_str(npa.get("uuid2"))
    mid = as_str(analytics.get("mid"))
    candidates = dedupe_nonempty((uuid_value, save_uid, uuid2, mid))

    return AndroidRuntimeProfile(
        source_root=str(root),
        external_dir=str(external_dir),
        shared_prefs_dir=str(shared_prefs_dir),
        region=connection.region or as_str(string_table.get("LastRegion")),
        server=connection.server or as_str(string_table.get("LastServer")),
        api_url=connection.api_url,
        gateway_url=connection.gateway_url,
        gateway_endpoint=connection.gateway_endpoint,
        connection_source=connection.source,
        country=as_str(npa.get("country")),
        locale=as_str(npa.get("locale")),
        initial_country=as_str(npa.get("initialCountry")),
        user_country=as_str(npa.get("userCountry")),
        install_country_name=as_str(analytics.get("installcountryname")),
        service_client_id=service_client_id,
        service_client_id_raw=service_client_id_raw,
        service_title=as_str(npa.get("serviceTitle")),
        app_id=as_str(npa.get("appId")),
        client_version=parsed_ua.get("client_version", ""),
        app_version_code=as_int(npa.get("appVersionCode")) or as_int(np_account_gcm.get("appVersion")),
        build_sdk_api_version=as_int(npa.get("build_sdk_api_version")),
        user_agent=user_agent,
        device_model=parsed_ua.get("device_model", ""),
        android_os_version=parsed_ua.get("android_os_version", ""),
        advertising_id=as_str(npa.get("advertisingId")) or as_str(analytics.get("adid")),
        uuid=uuid_value,
        uuid2=uuid2,
        mid=mid,
        idfv=as_str(analytics.get("idfv")),
        save_uid=save_uid,
        platform_store_uuid=as_str(platform_store.get("com.nexon.platform.store.internal.uuid")),
        language=as_str(device_option.get("Language")),
        voice_language=as_str(device_option.get("VoiceLanguage")),
        last_login_type=as_int(npa.get("lastLoginType")),
        use_ngsx=as_int(npa.get("useNgsx")),
        use_ngsm=as_int(npa.get("useNgsm")),
        use_gb_krpc=as_bool_or_none(npa.get("useGbKrpc")),
        use_gb_npsn=as_bool_or_none(npa.get("useGbNpsn")),
        login_ui_type=as_str(npa.get("loginUIType")),
        nk_member_access_code=as_str(npa.get("nkMemberAccessCode")),
        terms_api_ver=as_int(npa.get("termsApiVer")),
        policy_api_ver=as_int(npa.get("policyApiVer")),
        mcc=as_str(npa.get("mcc")),
        mnc=as_str(npa.get("mnc")),
        carrier_name=as_str(npa.get("carrierName")),
        device_unique_id=candidates[0] if candidates else "",
        device_unique_id_candidates=tuple(candidates),
        npa_common_path=str(npa_path or ""),
        nx_analytics_path=str(analytics_path or ""),
        player_prefs_path=str(player_prefs_path or ""),
        np_account_gcm_path=str(np_account_gcm_path or ""),
    )


def select_android_runtime_device_id(profile: AndroidRuntimeProfile, source: str = "auto") -> str:
    normalized = (source or "auto").strip().lower()
    candidates = {
        "uuid": profile.uuid,
        "save-uid": profile.save_uid,
        "uuid2": profile.uuid2,
        "mid": profile.mid,
        "idfv": profile.idfv,
        "platform-store-uuid": profile.platform_store_uuid,
        "none": "",
    }
    if normalized == "auto":
        return (
            profile.uuid
            or profile.uuid2
            or profile.save_uid
            or profile.mid
            or profile.idfv
            or profile.platform_store_uuid
        )
    try:
        return candidates[normalized]
    except KeyError as exc:
        raise ValueError(f"unknown android device id source: {source}") from exc


def resolve_android_runtime_root(root_dir: str | Path | None = None) -> Path:
    if root_dir:
        root = Path(root_dir).expanduser()
        if root.exists() and _looks_like_runtime_root(root):
            return root.resolve()
        if root.exists():
            latest = find_latest_android_runtime_pull(root)
            if latest is not None:
                return latest
        raise FileNotFoundError(f"Android runtime pull directory not found or incomplete: {root}")
    latest = find_latest_android_runtime_pull()
    if latest is None:
        raise FileNotFoundError(f"no Android runtime pull found under {DEFAULT_ANDROID_RUNTIME_PULL_DIR}")
    return latest


def read_shared_prefs_xml(path: str | Path) -> dict[str, Any]:
    import xml.etree.ElementTree as ET

    p = Path(path)
    if not p.exists():
        return {}
    root = ET.parse(p).getroot()
    values: dict[str, Any] = {}
    for child in root:
        name = child.attrib.get("name")
        if not name:
            continue
        tag = child.tag.lower()
        raw = child.attrib.get("value")
        if tag == "string":
            values[name] = unescape(child.text or "")
        elif tag == "boolean":
            values[name] = (raw or "").strip().lower() == "true"
        elif tag in ("int", "long"):
            values[name] = as_int(raw)
        elif tag == "float":
            values[name] = as_float(raw)
        elif tag == "set":
            values[name] = [unescape(item.text or "") for item in child if item.tag.lower() == "string"]
        else:
            values[name] = unescape(raw if raw is not None else (child.text or ""))
    return values


def parse_android_toy_user_agent(value: str) -> dict[str, str]:
    if not value:
        return {}
    parsed: dict[str, str] = {}
    version_match = re.match(r"[^/]+/([^\s]+)", value)
    if version_match:
        parsed["client_version"] = version_match.group(1).strip()
    match = re.search(r"\(([^;)]+);\s*([^;)]+)", value)
    if not match:
        return parsed
    parsed["device_model"] = match.group(1).strip()
    parsed["android_os_version"] = match.group(2).strip()
    return parsed


def _discover_connection(external_dir: Path) -> RuntimeConnectionInfo:
    return discover_connection_info(local_low_dir=external_dir)


def _looks_like_runtime_root(path: Path) -> bool:
    return (path / "external_selected").is_dir() and (path / "private_selected.tgz").exists() or (
        (path / "external_selected").is_dir() and (path / "private_selected").is_dir()
    )


def first_existing(paths: Iterable[Path]) -> Path | None:
    for path in sorted(paths):
        if path.exists():
            return path
    return None


def decode_base64_ascii(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    padded = text + "=" * (-len(text) % 4)
    try:
        decoded = base64.b64decode(padded, validate=False).decode("ascii")
    except Exception:
        return ""
    if not decoded or any(ord(ch) < 32 or ord(ch) > 126 for ch in decoded):
        return ""
    return decoded


def as_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_bool_or_none(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in ("true", "1", "yes"):
        return True
    if text in ("false", "0", "no"):
        return False
    return None


def dedupe_nonempty(values: Iterable[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out

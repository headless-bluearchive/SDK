"""Generate synthetic runtime profiles for replay experiments."""

from __future__ import annotations

import base64
import json
import random
import uuid
from dataclasses import asdict, dataclass
from html import escape
from pathlib import Path
from typing import Any

from modules.runtime.android_runtime_profile import AndroidRuntimeProfile, find_latest_android_runtime_pull, load_android_runtime_profile
from modules.runtime.region_config import profile_for
from modules.runtime.runtime_config import discover_pc_runtime_profile


@dataclass(frozen=True)
class GeneratedRuntimeProfile:
    kind: str
    path: str
    seed: str
    summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def generate_android_runtime_profile(
    output_dir: str | Path,
    *,
    seed: str = "",
    base_runtime_dir: str | Path | None = None,
    region: str = "",
    country: str = "",
    locale: str = "",
    client_version: str = "",
    app_version_code: int | None = None,
    device_model: str = "",
    android_os_version: str = "",
    density: str = "",
    resolution: str = "",
    service_id: str = "2079",
    client_id: str = "",
    package_name: str = "",
    language: str = "",
    voice_language: str = "",
) -> GeneratedRuntimeProfile:
    rng, resolved_seed = _rng(seed)
    base_profile = _load_android_base_profile(base_runtime_dir)
    resolved_region = region or (base_profile.region if base_profile else "")
    resolved_country = country or (base_profile.user_country or base_profile.country if base_profile else "")
    resolved_locale = locale or (base_profile.locale if base_profile else "")
    server = profile_for(resolved_region, country=resolved_country, locale=resolved_locale, gid=service_id)

    resolved_model = device_model or (base_profile.device_model if base_profile else "")
    resolved_android = android_os_version or (base_profile.android_os_version if base_profile else "")
    resolved_client_version = client_version or (base_profile.client_version if base_profile else "")
    resolved_app_version = app_version_code
    if resolved_app_version is None and base_profile is not None:
        resolved_app_version = base_profile.app_version_code
    resolved_client_id = client_id or (base_profile.service_client_id if base_profile else "")
    resolved_package = package_name or (base_profile.app_id if base_profile else "")
    resolved_language = language or (base_profile.language if base_profile else "")
    resolved_voice_language = voice_language or (base_profile.voice_language if base_profile else "")
    resolved_density, resolved_resolution = _android_ua_display_parts(
        base_profile.user_agent if base_profile else "",
        density=density,
        resolution=resolution,
    )

    missing = []
    if not resolved_model:
        missing.append("device_model")
    if not resolved_android:
        missing.append("android_os_version")
    if not resolved_client_version:
        missing.append("client_version")
    if resolved_app_version is None:
        missing.append("app_version_code")
    if not resolved_client_id:
        missing.append("client_id")
    if not resolved_package:
        missing.append("package_name")
    if not resolved_density:
        missing.append("density")
    if not resolved_resolution:
        missing.append("resolution")
    if missing:
        raise ValueError(
            "Android profile generation needs a real base runtime profile or explicit fields; "
            f"missing {', '.join(missing)}. Pass --base-android-runtime-dir or provide the missing arguments."
        )
    resolved_language = resolved_language or "En"
    resolved_voice_language = resolved_voice_language or "JP"

    root = Path(output_dir).expanduser().resolve()
    external = root / "external_selected"
    prefs = root / "private_selected" / "shared_prefs"
    external.mkdir(parents=True, exist_ok=True)
    prefs.mkdir(parents=True, exist_ok=True)

    android_uuid = _uuid4(rng)
    android_uuid2 = _hex(rng, 16)
    adid = _uuid4(rng)
    mid = _uuid4(rng)
    idfv = _uuid4(rng)
    platform_store_uuid = _uuid4(rng)
    save_uid = _save_uid(rng)
    country_value = (resolved_country or server.default_country).upper()
    locale_value = resolved_locale or server.default_locale
    sdk_api = _sdk_from_android_version(resolved_android)
    if sdk_api is None and base_profile is not None:
        sdk_api = base_profile.build_sdk_api_version
    sdk_api = sdk_api or 0
    user_agent = (
        f"{resolved_package}/{resolved_client_version} "
        f"({resolved_model}; {resolved_android}; Density/{resolved_density}; {resolved_resolution})"
    )

    _write_json(external / "LocalConfig.json", {"StringTable": {"LastRegion": server.region, "LastServer": "live"}})
    _write_json(external / "DeviceOption", {"Language": resolved_language, "VoiceLanguage": resolved_voice_language})
    (external / "Hosts").write_bytes(
        b"\x00".join(
            [
                server.gateway_url.rstrip("/").encode("ascii"),
                server.api_url.rstrip("/").encode("ascii"),
                server.gateway_endpoint.rstrip("/").encode("ascii"),
            ]
        )
        + b"\x00"
    )

    service_client_id_raw = base64.b64encode(str(resolved_client_id).encode("ascii")).decode("ascii").rstrip("=")
    _write_prefs(
        prefs / f"NPACommon.{service_id}.xml",
        {
            "country": ("string", country_value),
            "initialCountry": ("string", country_value),
            "userCountry": ("string", country_value),
            "locale": ("string", locale_value),
            "serviceClientId": ("string", service_client_id_raw),
            "serviceTitle": ("string", "Blue Archive"),
            "appId": ("string", resolved_package),
            "appVersionCode": ("int", int(resolved_app_version)),
            "build_sdk_api_version": ("int", int(sdk_api)),
            "userAgent": ("string", user_agent),
            "advertisingId": ("string", adid),
            "uuid": ("string", android_uuid),
            "uuid2": ("string", android_uuid2),
            "lastLoginType": ("int", 107),
            "useNgsx": ("int", 1),
            "useNgsm": ("int", 0),
            "useGbKrpc": ("boolean", True),
            "useGbNpsn": ("boolean", True),
            "loginUIType": ("string", "1"),
            "nkMemberAccessCode": ("string", _digits(rng, 10)),
            "termsApiVer": ("int", 2),
            "policyApiVer": ("int", 2),
            "mcc": ("string", ""),
            "mnc": ("string", ""),
            "carrierName": ("string", ""),
        },
    )
    _write_prefs(
        prefs / "NxAnalyticsPreference.xml",
        {
            "adid": ("string", adid),
            "installcountryname": ("string", country_value),
            "mid": ("string", mid),
            "idfv": ("string", idfv),
        },
    )
    _write_prefs(prefs / "NPAccountGCMPref.xml", {"appVersion": ("int", int(resolved_app_version))})
    _write_prefs(prefs / "com.nexon.bluearchive.v2.playerprefs.xml", {"SaveUID": ("string", save_uid)})
    _write_prefs(
        prefs / "com.nexon.platform.store.internal.preferences.APP_SETTINGS.xml",
        {"com.nexon.platform.store.internal.uuid": ("string", platform_store_uuid)},
    )

    summary = {
        "kind": "android-runtime-pull",
        "region": server.region,
        "api_url": server.api_url,
        "gateway_url": server.gateway_url,
        "gateway_endpoint": server.gateway_endpoint,
        "base_runtime_dir": base_profile.source_root if base_profile else "",
        "country": country_value,
        "locale": locale_value,
        "client_version": resolved_client_version,
        "app_version_code": int(resolved_app_version),
        "device_model": resolved_model,
        "android_os_version": resolved_android,
        "uuid": android_uuid,
        "uuid2": android_uuid2,
        "advertising_id": adid,
        "idfv": idfv,
        "mid": mid,
        "platform_store_uuid": platform_store_uuid,
        "main_args": [
            "--android-runtime-dir",
            str(root),
            "--region",
            server.region,
        ],
    }
    _write_json(root / "generated_runtime_profile.json", summary)
    (root / "main_args.txt").write_text(" ".join(_quote_arg(item) for item in summary["main_args"]), encoding="utf-8")
    return GeneratedRuntimeProfile(kind="android", path=str(root), seed=resolved_seed, summary=summary)


def generate_pc_steam_runtime_profile(
    output_path: str | Path,
    *,
    seed: str = "",
    region: str = "tw",
    country: str = "TW",
    locale: str = "zh-TW",
    cid: str = "",
    device_model: str = "",
    os_version: str = "",
    system_memory_mb: int | None = None,
) -> GeneratedRuntimeProfile:
    rng, resolved_seed = _rng(seed)
    server = profile_for(region, country=country, locale=locale, gid="2079")
    local_profile = discover_pc_runtime_profile()
    resolved_cid = cid or _pc_cid(rng)
    cid_pool = [resolved_cid]
    while len(cid_pool) < 3:
        candidate = _pc_cid(rng)
        if candidate not in cid_pool:
            cid_pool.append(candidate)
    computer_name = local_profile.computer_name
    resolved_model = device_model or local_profile.device_model
    resolved_os = os_version or local_profile.os_version
    resolved_memory = int(system_memory_mb or local_profile.system_memory_mb or 0)

    out = Path(output_path).expanduser().resolve()
    if out.suffix.lower() != ".json":
        out.mkdir(parents=True, exist_ok=True)
        profile_path = out / "steam_runtime_profile.json"
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        profile_path = out

    data = {
        "profile_kind": "pc-steam-runtime",
        "seed": resolved_seed,
        "region": server.region,
        "country": country,
        "locale": locale,
        "api_url": server.api_url,
        "gateway_url": server.gateway_url,
        "gateway_endpoint": server.gateway_endpoint,
        "pcRuntimeProfile": {
            "computer_name": computer_name,
            "device_model": resolved_model,
            "os_version": resolved_os,
            "system_memory_mb": resolved_memory or None,
            "source": f"generated-from-{local_profile.source}",
        },
        "launcherState": {
            "config_path": str(profile_path),
            "nxi_dirs": [],
            "cid": resolved_cid,
            "cid_pool": cid_pool,
            "token_infos": [],
        },
        "main_args": [
            "--main-game-profile",
            "pc-steam",
            "--pc-runtime-profile-json",
            str(profile_path),
            "--region",
            server.region,
        ],
    }
    _write_json(profile_path, data)
    (profile_path.with_suffix(".args.txt")).write_text(
        " ".join(_quote_arg(item) for item in data["main_args"]),
        encoding="utf-8",
    )
    return GeneratedRuntimeProfile(kind="pc-steam", path=str(profile_path), seed=resolved_seed, summary=data)


def _load_android_base_profile(base_runtime_dir: str | Path | None) -> AndroidRuntimeProfile | None:
    if base_runtime_dir:
        return load_android_runtime_profile(base_runtime_dir)
    latest = find_latest_android_runtime_pull()
    if latest is None:
        return None
    return load_android_runtime_profile(latest)


def _android_ua_display_parts(user_agent: str, *, density: str, resolution: str) -> tuple[str, str]:
    resolved_density = density
    resolved_resolution = resolution
    if user_agent and ("Density/" in user_agent or ";" in user_agent):
        for part in user_agent.strip().strip(")").split(";"):
            text = part.strip()
            if text.startswith("Density/") and not resolved_density:
                resolved_density = text.split("/", 1)[1].strip()
            elif "x" in text and text.replace("x", "").isdigit() and not resolved_resolution:
                resolved_resolution = text
    return resolved_density, resolved_resolution


def _rng(seed: str) -> tuple[random.Random, str]:
    resolved = seed or uuid.uuid4().hex
    return random.Random(resolved), resolved


def _uuid4(rng: random.Random) -> str:
    return str(uuid.UUID(int=rng.getrandbits(128), version=4))


def _hex(rng: random.Random, length: int) -> str:
    return "".join(rng.choice("0123456789abcdef") for _ in range(length))


def _digits(rng: random.Random, length: int) -> str:
    return "".join(rng.choice("0123456789") for _ in range(length))


def _save_uid(rng: random.Random) -> str:
    value = _digits(rng, 8)
    return f"{value[:2]} {value[2:5]} {value[5:]}"


def _pc_cid(rng: random.Random) -> str:
    return "2079" + _digits(rng, 13)


def _sdk_from_android_version(value: str) -> int | None:
    match = None
    for part in value.split():
        if part.isdigit():
            match = int(part)
            break
    if match is None:
        return None
    return {12: 32, 13: 33, 14: 34, 15: 35}.get(match)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_prefs(path: Path, values: dict[str, tuple[str, Any]]) -> None:
    lines = ["<?xml version='1.0' encoding='utf-8' standalone='yes' ?>", "<map>"]
    for name, (kind, value) in values.items():
        escaped_name = escape(str(name), quote=True)
        if kind == "string":
            lines.append(f'  <string name="{escaped_name}">{escape(str(value), quote=False)}</string>')
        elif kind == "boolean":
            lines.append(f'  <boolean name="{escaped_name}" value="{str(bool(value)).lower()}" />')
        elif kind in ("int", "long", "float"):
            lines.append(f'  <{kind} name="{escaped_name}" value="{value}" />')
        else:
            raise ValueError(f"unsupported shared_prefs value kind: {kind}")
    lines.append("</map>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _quote_arg(value: str) -> str:
    if not value or any(ch.isspace() for ch in value) or '"' in value:
        return '"' + value.replace('"', '\\"') + '"'
    return value

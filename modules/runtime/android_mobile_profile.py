from __future__ import annotations

import json
import random
import uuid
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any
import requests

from config.game import DEFAULTS
from config.paths import DEFAULT_REPORT_DIR
from core.error import NetworkError, RuntimeProfileError
from modules.runtime.ngsm_token import NGSM_FINGERPRINT_VERSION, with_ngsm_fingerprint_defaults
from utils.proxy import requests_proxy_map

DEFAULT_ANDROID_MOBILE_PROFILE_PATH = (
    DEFAULT_REPORT_DIR.parent / "runtime_profiles" / "android_mobile_profile.json"
)
DEFAULT_GALAXY_STORE_APP_ID = DEFAULTS.galaxy_store_package_name
GALAXY_STORE_DETAIL_URL = "https://galaxystore.samsung.com/api/detail/{app_id}"

FALLBACK_DEVICES = [
    {"device_model": "SM-S918B", "os_version": "Android 14", "memory_mb": 12288, "density": "3.0", "resolution": "3088x1440"},
    {"device_model": "SM-S916B", "os_version": "Android 14", "memory_mb": 8192, "density": "2.75", "resolution": "2340x1080"},
    {"device_model": "SM-S911B", "os_version": "Android 14", "memory_mb": 8192, "density": "2.625", "resolution": "2340x1080"},
    {"device_model": "SM-G998B", "os_version": "Android 13", "memory_mb": 12288, "density": "3.0", "resolution": "3200x1440"},
    {"device_model": "SM-G996B", "os_version": "Android 13", "memory_mb": 8192, "density": "2.75", "resolution": "2400x1080"},
    {"device_model": "SM-A546E", "os_version": "Android 14", "memory_mb": 8192, "density": "2.75", "resolution": "2340x1080"},
    {"device_model": "Pixel 7", "os_version": "Android 14", "memory_mb": 8192, "density": "2.625", "resolution": "2400x1080"},
    {"device_model": "PGT-AN00", "os_version": "Android 12", "memory_mb": 8192, "density": "1.75", "resolution": "1920x1080"},
]

COUNTRY_NETWORKS = {
    "TW": [
        {"mcc": 466, "mnc": 92, "carrier_name": "Chunghwa Telecom"},
        {"mcc": 466, "mnc": 1, "carrier_name": "FarEasTone"},
        {"mcc": 466, "mnc": 97, "carrier_name": "Taiwan Mobile"},
    ],
    "HK": [
        {"mcc": 454, "mnc": 0, "carrier_name": "CSL"},
        {"mcc": 454, "mnc": 3, "carrier_name": "3 HK"},
        {"mcc": 454, "mnc": 12, "carrier_name": "CMHK"},
    ],
    "MO": [{"mcc": 455, "mnc": 0, "carrier_name": "SmarTone Macau"}],
    "TH": [{"mcc": 520, "mnc": 1, "carrier_name": "AIS"}, {"mcc": 520, "mnc": 5, "carrier_name": "dtac"}],
    "US": [{"mcc": 310, "mnc": 260, "carrier_name": "T-Mobile"}, {"mcc": 311, "mnc": 480, "carrier_name": "Verizon"}],
}


@dataclass(frozen=True)
class AndroidMobileProfile:
    profile_kind: str = "android-mobile-synthetic"
    seed: str = ""
    source: str = "fallback"
    country: str = DEFAULTS.country
    locale: str = DEFAULTS.locale
    initial_country: str = DEFAULTS.country
    device_country: str = DEFAULTS.country
    package_name: str = DEFAULTS.package_name
    store_type: str = DEFAULTS.store_type
    client_version: str = ""
    app_version_code: int | None = None
    device_model: str = "SM-S918B"
    os_version: str = "Android 14"
    system_memory_mb: int = 8192
    density: str = "3.0"
    resolution: str = "3088x1440"
    device_unique_id: str = ""
    advertisement_id: str = ""
    idfv: str = ""
    uuid: str = ""
    uuid2: str = ""
    mid: str = ""
    platform_store_uuid: str = ""
    save_uid: str = ""
    app_set_scope: int = 0
    app_set_id: str = ""
    mcc: int = 0
    mnc: int = 0
    carrier_name: str = ""
    mac: str = ""
    display_name: str = ""
    volume_serial: str = ""
    disk_serial: str = ""
    filetime: str = ""
    version: str = NGSM_FINGERPRINT_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_android_mobile_profile(path: str | Path) -> AndroidMobileProfile:
    profile_path = Path(path).expanduser()
    data = json.loads(profile_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeProfileError(f"Android mobile profile must be a JSON object: {profile_path}")
    allowed = AndroidMobileProfile.__dataclass_fields__
    values = {key: data.get(key) for key in allowed if key in data}
    return with_ngsm_fingerprint_defaults(AndroidMobileProfile(**values))


def generate_android_mobile_profile(
    *,
    country: str = DEFAULTS.country,
    locale: str = DEFAULTS.locale,
    seed: str = "",
) -> AndroidMobileProfile:
    rng, resolved_seed = _rng(seed)
    generated = _generate_with_randomandroidphone(country=country, rng=rng)
    if generated is None:
        generated = _generate_with_fallback(country=country, rng=rng)
    device = generated["device"]
    network = generated["network"]
    uuid_value = str(uuid.UUID(int=rng.getrandbits(128), version=4))
    uuid2 = f"{rng.getrandbits(64):016x}"
    mid = str(uuid.UUID(int=rng.getrandbits(128), version=4))
    idfv = str(uuid.UUID(int=rng.getrandbits(128), version=4))
    adid = str(uuid.UUID(int=rng.getrandbits(128), version=4))
    platform_store_uuid = str(uuid.UUID(int=rng.getrandbits(128), version=4))
    app_set_id = str(uuid.UUID(int=rng.getrandbits(128), version=4))
    profile = AndroidMobileProfile(
        seed=resolved_seed,
        source=generated["source"],
        country=country.upper() or "TW",
        locale=locale or "zh-TW",
        initial_country=country.upper() or "TW",
        device_country=country.upper() or "TW",
        device_model=str(device["device_model"]),
        os_version=str(device["os_version"]),
        system_memory_mb=int(device["memory_mb"]),
        density=str(device["density"]),
        resolution=str(device["resolution"]),
        device_unique_id=uuid_value,
        advertisement_id=adid,
        idfv=idfv,
        uuid=uuid_value,
        uuid2=uuid2,
        mid=mid,
        platform_store_uuid=platform_store_uuid,
        save_uid=_save_uid(rng),
        app_set_scope=0,
        app_set_id=app_set_id,
        mcc=int(network.get("mcc") or 0),
        mnc=int(network.get("mnc") or 0),
        carrier_name=str(network.get("carrier_name") or ""),
    )
    return with_ngsm_fingerprint_defaults(profile)


def fetch_galaxy_store_client_version(
    *,
    app_id: str = DEFAULT_GALAXY_STORE_APP_ID,
    timeout: float = 10.0,
    proxy: str | None = None,
) -> tuple[str, dict[str, Any]]:
    url = GALAXY_STORE_DETAIL_URL.format(app_id=app_id)
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json,text/plain,*/*"}
    session = requests.Session()
    session.trust_env = False
    try:
        response = session.get(url, headers=headers, timeout=timeout, proxies=requests_proxy_map(proxy) or None)
        response.raise_for_status()
        raw = response.content
    except requests.RequestException as exc:
        raise NetworkError(f"GalaxyStore client version fetch failed: {exc}") from exc
    data = json.loads(raw.decode("utf-8"))
    detail = data.get("DetailMain") if isinstance(data, dict) else None
    version = ""
    if isinstance(detail, dict):
        version = str(detail.get("contentBinaryVersion") or "").strip()
    if not version:
        raise RuntimeProfileError("GalaxyStore response did not contain DetailMain.contentBinaryVersion")
    return version, data


def app_version_code_from_client_version(version: str) -> int | None:
    text = (version or "").strip()
    if not text:
        return None
    tail = text.rsplit(".", 1)[-1]
    try:
        return int(tail)
    except ValueError:
        return None


def with_client_version(profile: AndroidMobileProfile, version: str) -> AndroidMobileProfile:
    if not version:
        return profile
    code = app_version_code_from_client_version(version)
    if profile.client_version == version and profile.app_version_code == code:
        return profile
    return replace(profile, client_version=version, app_version_code=code)


def _generate_with_randomandroidphone(*, country: str, rng: random.Random) -> dict[str, Any] | None:
    try:
        from randomandroidphone import RandomPhone
    except Exception:
        return None
    country_name = _randomandroidphone_country(country)
    phone_formats = _phone_formats(country)
    try:
        generator = RandomPhone(country=country_name, phone_format_without_country=phone_formats)
        if hasattr(generator, "df"):
            df = generator.df
            if "aa_form_factor" in df:
                df = df.loc[df.aa_form_factor.astype(str).str.lower().eq("phone")]
            if "aa_android_version" in df:
                df = df.loc[df.aa_android_version.astype(float) >= 12.0]
            if not df.empty:
                generator.df = df
        row = generator.get_phone_data(qty=1).iloc[0].to_dict()
    except Exception:
        return None
    device = {
        "device_model": str(row.get("aa_model_name") or row.get("aa_device") or "SM-S918B").replace("_", " "),
        "os_version": f"Android {row.get('aa_android_version') or 13}",
        "memory_mb": _normalize_memory_mb(row.get("aa_ram_totalmem")),
        "density": str(row.get("aa_screen_densities") or "3.0").split(";")[0],
        "resolution": _resolution(row.get("aa_width"), row.get("aa_height")),
    }
    network = {
        "mcc": _to_int(row.get("aa_mcc")) or 0,
        "mnc": _to_int(row.get("aa_mnc")) or 0,
        "carrier_name": str(row.get("aa_network") or ""),
    }
    if not network["mcc"]:
        network = dict(rng.choice(COUNTRY_NETWORKS.get(country.upper(), COUNTRY_NETWORKS["TW"])))
    return {"source": "randomandroidphone", "device": device, "network": network}


def _generate_with_fallback(*, country: str, rng: random.Random) -> dict[str, Any]:
    return {
        "source": "fallback-device-pool",
        "device": dict(rng.choice(FALLBACK_DEVICES)),
        "network": dict(rng.choice(COUNTRY_NETWORKS.get(country.upper(), COUNTRY_NETWORKS["TW"]))),
    }


def _randomandroidphone_country(country: str) -> str:
    return {
        "TW": "Taiwan",
        "HK": "Hong Kong",
        "MO": "Macau",
        "TH": "Thailand",
        "US": "United States",
    }.get(country.upper(), country or "Taiwan")


def _phone_formats(country: str) -> tuple[tuple[int, ...], ...]:
    normalized = country.upper()
    if normalized == "TW":
        return ((9,), tuple(range(1000, 10000)), tuple(range(1000, 10000)))
    if normalized == "HK":
        return ((5, 6, 9), tuple(range(1000, 10000)), tuple(range(100, 1000)))
    if normalized == "TH":
        return ((6, 8, 9), tuple(range(1000, 10000)), tuple(range(1000, 10000)))
    return ((9,), tuple(range(1000, 10000)), tuple(range(1000, 10000)))


def _rng(seed: str) -> tuple[random.Random, str]:
    resolved = seed or uuid.uuid4().hex
    return random.Random(resolved), resolved


def _save_uid(rng: random.Random) -> str:
    return f"{rng.randrange(10, 99)} {rng.randrange(100, 999)} {rng.randrange(100, 999)}"


def _resolution(width: Any, height: Any) -> str:
    w = _to_int(width) or 2400
    h = _to_int(height) or 1080
    return f"{max(w, h)}x{min(w, h)}"


def _normalize_memory_mb(value: Any) -> int:
    raw = _to_int(value)
    if raw is None:
        return 8192
    if raw < 64:
        return max(raw * 1024, 4096)
    if raw < 2048:
        return 4096
    return max(raw, 4096)


def _to_int(value: Any) -> int | None:
    try:
        return int(float(str(value).strip()))
    except Exception:
        return None

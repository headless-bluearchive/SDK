
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from urllib.parse import urljoin

from config.game import DEFAULTS
from core.error import ConfigurationError

DEFAULT_GID = DEFAULTS.service_id


@dataclass(frozen=True)
class ServerProfile:
    region: str
    display_name: str
    api_url: str
    gateway_url: str
    nxsid: str
    default_country: str
    default_locale: str
    gid: str = DEFAULT_GID

    @property
    def gateway_endpoint(self) -> str:
        return urljoin(self.gateway_url.rstrip("/") + "/", "gateway")

    def to_dict(self) -> dict[str, str]:
        data = asdict(self)
        data["gateway_endpoint"] = self.gateway_endpoint
        return data


SERVER_PROFILES: dict[str, ServerProfile] = {
    "kr": ServerProfile(
        region="kr",
        display_name="Korea",
        api_url="https://nxm-kr-bagl.nexon.com:5000/api/",
        gateway_url="https://nxm-kr-bagl.nexon.com:5100/api/",
        nxsid="live-kr",
        default_country="KR",
        default_locale="ko-KR",
    ),
    "tw": ServerProfile(
        region="tw",
        display_name="Taiwan/Hong Kong/Macau",
        api_url="https://nxm-tw-bagl.nexon.com:5000/api/",
        gateway_url="https://nxm-tw-bagl.nexon.com:5100/api/",
        nxsid="live-tw",
        default_country="TW",
        default_locale="zh-TW",
    ),
    "asia": ServerProfile(
        region="asia",
        display_name="Asia",
        api_url="https://nxm-th-bagl.nexon.com:5000/api/",
        gateway_url="https://nxm-th-bagl.nexon.com:5100/api/",
        nxsid="live-asia",
        default_country="TH",
        default_locale="th-TH",
    ),
    "na": ServerProfile(
        region="na",
        display_name="North America",
        api_url="https://nxm-or-bagl.nexon.com:5000/api/",
        gateway_url="https://nxm-or-bagl.nexon.com:5100/api/",
        nxsid="live-na",
        default_country="US",
        default_locale="en-US",
    ),
    "global": ServerProfile(
        region="global",
        display_name="Global/Europe",
        api_url="https://nxm-eu-bagl.nexon.com:5000/api/",
        gateway_url="https://nxm-eu-bagl.nexon.com:5100/api/",
        nxsid="live-global",
        default_country="GB",
        default_locale="en-GB",
    ),
}


REGION_ALIASES = {
    "korea": "kr",
    "kr": "kr",
    "kor": "kr",
    "tw": "tw",
    "taiwan": "tw",
    "hk": "tw",
    "hongkong": "tw",
    "hong_kong": "tw",
    "mo": "tw",
    "macau": "tw",
    "asia": "asia",
    "as": "asia",
    "th": "asia",
    "thai": "asia",
    "thailand": "asia",
    "sg": "asia",
    "singapore": "asia",
    "id": "asia",
    "indonesia": "asia",
    "vn": "asia",
    "vietnam": "asia",
    "na": "na",
    "northamerica": "na",
    "north_america": "na",
    "us": "na",
    "usa": "na",
    "ca": "na",
    "canada": "na",
    "global": "global",
    "gl": "global",
    "eu": "global",
    "europe": "global",
    "gb": "global",
    "uk": "global",
}


COUNTRY_DEFAULTS = {
    "KR": ("kr", "ko-KR"),
    "TW": ("tw", "zh-TW"),
    "HK": ("tw", "zh-HK"),
    "MO": ("tw", "zh-MO"),
    "TH": ("asia", "th-TH"),
    "SG": ("asia", "en-SG"),
    "ID": ("asia", "id-ID"),
    "VN": ("asia", "vi-VN"),
    "US": ("na", "en-US"),
    "CA": ("na", "en-US"),
    "GB": ("global", "en-GB"),
    "AU": ("global", "en-AU"),
    "DE": ("global", "de-DE"),
    "FR": ("global", "fr-FR"),
    "IT": ("global", "it-IT"),
    "ES": ("global", "es-ES"),
}


def normalize_region(region: str) -> str:
    key = (region or "").strip().lower().replace("-", "_").replace(" ", "_")
    if not key:
        return ""
    compact = key.replace("_", "")
    return REGION_ALIASES.get(key) or REGION_ALIASES.get(compact) or key


def profile_for(region: str = "", *, country: str = "", locale: str = "", gid: str = DEFAULT_GID) -> ServerProfile:
    resolved_region = normalize_region(region)
    country_code = (country or "").strip().upper()
    default_locale = ""
    if not resolved_region and country_code:
        resolved_region, default_locale = COUNTRY_DEFAULTS.get(country_code, ("global", "en-US"))
    if not resolved_region:
        resolved_region = "tw"
    try:
        profile = SERVER_PROFILES[resolved_region]
    except KeyError as exc:
        raise ConfigurationError(f"unknown server region {region!r}; expected one of {', '.join(SERVER_PROFILES)}") from exc

    return replace(
        profile,
        default_country=country_code or profile.default_country,
        default_locale=locale or default_locale or profile.default_locale,
        gid=str(gid or DEFAULT_GID),
    )


def list_profiles() -> list[ServerProfile]:
    return [SERVER_PROFILES[name] for name in ("kr", "tw", "asia", "na", "global")]

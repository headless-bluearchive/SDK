
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urljoin

from config.game import DEFAULTS
from modules.runtime.region_config import normalize_region, profile_for


DEFAULT_CLIENT_VERSION = DEFAULTS.client_version

COUNTRY_REGION_HINTS = {
    "TW": "tw",
    "HK": "tw",
    "MO": "tw",
    "TH": "th",
    "GB": "eu",
    "DE": "eu",
    "FR": "eu",
    "IT": "eu",
    "ES": "eu",
    "NL": "eu",
    "PL": "eu",
}


@dataclass(frozen=True)
class RuntimeConnectionInfo:
    region: str
    server: str
    api_url: str
    gateway_url: str
    gateway_endpoint: str
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def discover_connection_info(
    *,
    country: str = "TW",
    region: str = "",
    server: str = "",
) -> RuntimeConnectionInfo:
    resolved_region = normalize_region(region) if region else region_from_country(country)
    resolved_server = (server or "live").strip().lower()
    profile = profile_for(resolved_region, country=country)

    return RuntimeConnectionInfo(
        region=profile.region,
        server=resolved_server,
        api_url=profile.api_url,
        gateway_url=profile.gateway_url,
        gateway_endpoint=urljoin(profile.gateway_url, "gateway"),
        source="static-server-profile",
    )


def region_from_country(country: str) -> str:
    code = (country or "").strip().upper()
    if not code:
        return "tw"
    return COUNTRY_REGION_HINTS.get(code, code.lower())

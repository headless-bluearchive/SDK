"""Runtime game configuration discovery.

This module reads only Blue Archive runtime cache/config files and derives the
main-game API/Gateway base URLs used by the installed client.
"""

from __future__ import annotations

import base64
import binascii
import json
import platform
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin, urlparse, urlunparse

from headlessba.config.paths import DEFAULT_NXINFACE_CONFIG_PATH
from headlessba.modules.runtime.region_config import normalize_region, profile_for


DEFAULT_LOCAL_LOW_DIR = Path.home() / "AppData" / "LocalLow" / "Nexon Games" / "Blue Archive"
DEFAULT_CLIENT_VERSION = "1.79.364258"
CLIENT_VERSION_RE = re.compile(r"\b\d+\.\d+\.\d+\b")

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

URL_RE = re.compile(rb"https?://[A-Za-z0-9.-]+(?::[0-9]+)?(?:/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]*)?")

HOST_REGION_ALIASES = {
    "asia": ("asia", "th"),
    "na": ("na", "or"),
    "global": ("global", "eu"),
}


@dataclass(frozen=True)
class RuntimeConnectionInfo:
    local_low_dir: str
    local_config_path: str
    hosts_path: str
    region: str
    server: str
    api_url: str
    gateway_url: str
    gateway_endpoint: str
    source: str
    discovered_urls: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PcRuntimeProfile:
    computer_name: str
    device_model: str
    os_version: str
    system_memory_mb: int | None
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NxInfaceTokenInfo:
    key: str
    uid: str
    access_token_type: str
    access_token: str
    guid: str
    gid: str
    issuer: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NxInfaceConfigInfo:
    config_path: str
    nxi_dirs: tuple[str, ...]
    cid: str
    cid_pool: tuple[str, ...]
    token_infos: tuple[NxInfaceTokenInfo, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_path": self.config_path,
            "nxi_dirs": list(self.nxi_dirs),
            "cid": self.cid,
            "cid_pool": list(self.cid_pool),
            "token_infos": [item.to_dict() for item in self.token_infos],
        }


def discover_connection_info(
    *,
    country: str = "TW",
    region: str = "",
    server: str = "",
    local_low_dir: str | Path = DEFAULT_LOCAL_LOW_DIR,
) -> RuntimeConnectionInfo:
    """Discover current ApiUrl/GatewayUrl from runtime config and Hosts cache."""

    root = Path(local_low_dir).expanduser().resolve()
    local_config_path = root / "LocalConfig.json"
    hosts_path = root / "Hosts"

    local_config = read_json_if_exists(local_config_path)
    string_table = local_config.get("StringTable") if isinstance(local_config.get("StringTable"), dict) else {}
    explicit_region = bool(region)
    resolved_region = normalize_region(region) if region else (string_table.get("LastRegion") or region_from_country(country)).strip().lower()
    resolved_server = (server or string_table.get("LastServer") or "live").strip().lower()

    urls = extract_urls_from_hosts(hosts_path)
    api_url = select_service_url(urls, resolved_region, kind="api", allow_any=not explicit_region)
    gateway_url = select_service_url(urls, resolved_region, kind="gateway", allow_any=not explicit_region)
    source = "Hosts"
    if not gateway_url:
        profile = profile_for(resolved_region, country=country)
        api_url = profile.api_url
        gateway_url = profile.gateway_url
        source = "static-server-profile"

    return RuntimeConnectionInfo(
        local_low_dir=str(root),
        local_config_path=str(local_config_path),
        hosts_path=str(hosts_path),
        region=resolved_region,
        server=resolved_server,
        api_url=normalize_service_base(api_url) if api_url else "",
        gateway_url=normalize_service_base(gateway_url),
        gateway_endpoint=urljoin(normalize_service_base(gateway_url), "gateway"),
        source=source,
        discovered_urls=tuple(urls),
    )


def discover_pc_runtime_profile() -> PcRuntimeProfile:
    command = (
        "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
        "$cs = Get-CimInstance Win32_ComputerSystem; "
        "$os = Get-CimInstance Win32_OperatingSystem; "
        "$model = if ($cs.Manufacturer -and $cs.Model) "
        "{ ($cs.Manufacturer + ' ' + $cs.Model).Trim() } "
        "elseif ($cs.Model) { $cs.Model } else { $env:COMPUTERNAME }; "
        "$osv = if ($os.Caption -and $os.Version) "
        "{ ($os.Caption + ' (' + $os.Version + ')').Trim() } "
        "elseif ($os.Version) { $os.Version } else { '' }; "
        "[pscustomobject]@{"
        "computer_name=$env:COMPUTERNAME;"
        "device_model=$model;"
        "os_version=$osv;"
        "system_memory_mb=[int]($cs.TotalPhysicalMemory / 1MB)"
        "} | ConvertTo-Json -Compress"
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=5,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            parsed = json.loads(result.stdout)
            if isinstance(parsed, dict):
                return PcRuntimeProfile(
                    computer_name=str(parsed.get("computer_name") or platform.node() or ""),
                    device_model=str(parsed.get("device_model") or platform.node() or "Windows PC"),
                    os_version=str(parsed.get("os_version") or _fallback_windows_os_version()),
                    system_memory_mb=_maybe_int(parsed.get("system_memory_mb")),
                    source="powershell-cim",
                )
    except Exception:
        pass
    return PcRuntimeProfile(
        computer_name=platform.node() or "",
        device_model=platform.node() or "Windows PC",
        os_version=_fallback_windows_os_version(),
        system_memory_mb=None,
        source="platform-fallback",
    )


def discover_nxinface_config(path: str | Path = DEFAULT_NXINFACE_CONFIG_PATH) -> NxInfaceConfigInfo | None:
    config_path = Path(path).expanduser()
    if not config_path.exists():
        return None
    raw_text = config_path.read_text(encoding="utf-8", errors="ignore").replace("&", "")
    decoded = base64.b64decode(raw_text)
    parsed = json.loads(decoded.decode("utf-8"))
    if not isinstance(parsed, dict):
        return None
    token_infos: list[NxInfaceTokenInfo] = []
    for key, value in parsed.items():
        if not key.endswith(".utoken") or not isinstance(value, str):
            continue
        payload = _decode_jwt_payload(value)
        data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
        token_infos.append(
            NxInfaceTokenInfo(
                key=key,
                uid=str(data.get("uid") or ""),
                access_token_type=str(data.get("access_token_type") or ""),
                access_token=str(data.get("access_token") or ""),
                guid=str(data.get("guid") or ""),
                gid=str(data.get("gid") or ""),
                issuer=str(payload.get("iss") or ""),
            )
        )
    token_infos.sort(key=lambda item: item.key)
    cid_pool: list[str] = []
    for entry in parsed.get("2079.cid_pool") or []:
        if isinstance(entry, dict):
            value = str(entry.get("value") or "")
            if value:
                cid_pool.append(value)
    return NxInfaceConfigInfo(
        config_path=str(config_path.resolve()),
        nxi_dirs=tuple(str(item) for item in (parsed.get("NXI_DIRS") or []) if item),
        cid=str(parsed.get("cid") or ""),
        cid_pool=tuple(cid_pool),
        token_infos=tuple(token_infos),
    )


def discover_client_version(
    *,
    search_root: str | Path | None = None,
    fallback: str = DEFAULT_CLIENT_VERSION,
) -> str:
    """Return the current game client version from cached server_config JSON.

    The static config file name changes with patches, while its ``desc`` field
    carries the full version string used by Queuing_GetTicket.ClientVersion.
    """

    root = Path(search_root).resolve() if search_root else Path(__file__).resolve().parents[1]
    candidates = sorted(
        (root / "analysis_reports").glob("server_config_*_Live.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        version = read_client_version_from_server_config(path)
        if version:
            return version
    return fallback


def read_client_version_from_server_config(path: str | Path) -> str:
    data = read_json_if_exists(path)
    desc = str(data.get("desc") or data.get("Desc") or "")
    match = CLIENT_VERSION_RE.search(desc)
    return match.group(0) if match else ""


def read_json_if_exists(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def extract_urls_from_hosts(path: str | Path) -> list[str]:
    p = Path(path)
    if not p.exists():
        return []
    raw = p.read_bytes()
    urls: list[str] = []
    for match in URL_RE.findall(raw):
        text = match.decode("ascii", errors="ignore").rstrip("\x00")
        if text:
            urls.append(text)
    return dedupe_preserve_order(urls)


def select_service_url(urls: Iterable[str], region: str, *, kind: str, allow_any: bool = True) -> str:
    candidates = [url for url in urls if service_kind_matches(url, kind)]
    region_candidates = [url for url in candidates if url_matches_region(url, region)]
    chosen = region_candidates or (candidates if allow_any else [])
    if not chosen:
        return ""
    return sorted(chosen, key=service_url_rank)[0]


def service_kind_matches(url: str, kind: str) -> bool:
    parsed = urlparse(url)
    port = parsed.port
    path = parsed.path.lower()
    if kind == "gateway":
        return port == 5100 or "gateway" in path
    if kind == "api":
        return port == 5000 or ("/api" in path and port != 5100)
    raise ValueError("kind must be 'api' or 'gateway'")


def url_matches_region(url: str, region: str) -> bool:
    if not region:
        return True
    host = (urlparse(url).hostname or "").lower()
    needles = HOST_REGION_ALIASES.get(region.lower(), (region.lower(),))
    for needle in needles:
        if f"nxm-{needle}-" in host or f"-{needle}-" in host or host.startswith(f"{needle}-"):
            return True
    return False


def normalize_service_base(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    path = parsed.path or ""
    if not path or path == "/":
        path = "/api/"
    elif not path.endswith("/"):
        path += "/"
    return urlunparse(parsed._replace(path=path, params="", query="", fragment=""))


def service_url_rank(url: str) -> tuple[int, int, str]:
    parsed = urlparse(url)
    has_api_path = 0 if parsed.path.rstrip("/").endswith("/api") else 1
    https_rank = 0 if parsed.scheme == "https" else 1
    return (has_api_path, https_rank, url)


def region_from_country(country: str) -> str:
    code = (country or "").strip().upper()
    if not code:
        return "tw"
    return COUNTRY_REGION_HINTS.get(code, code.lower())


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _decode_jwt_payload(token: str) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        return {}
    try:
        payload = parts[1]
        padding = "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        parsed = json.loads(decoded.decode("utf-8"))
    except (binascii.Error, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _fallback_windows_os_version() -> str:
    system = platform.system() or "Windows"
    version = platform.version() or platform.release() or ""
    return f"{system} ({version})".strip()


def _maybe_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

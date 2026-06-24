from __future__ import annotations

import os
import re
from urllib.parse import urlparse, urlunparse

from core.error import ConfigurationError
from core.i18n import t


SUPPORTED_PROXY_SCHEMES = {"http", "https", "socks4", "socks4a", "socks5", "socks5h"}
LOOPBACK_BYPASS = ("localhost", "127.0.0.1", "::1")

SYSTEM_PROXY_SENTINELS = {"system", "auto", "system-proxy", "auto-detect", "detect"}
_SYSTEM_PROXY_CACHE: list[str | None] = []


def detect_system_proxy(*, refresh: bool = False) -> str | None:
    if _SYSTEM_PROXY_CACHE and not refresh:
        return _SYSTEM_PROXY_CACHE[0]
    resolved = _detect_static_proxy() or _detect_pac_proxy()
    _SYSTEM_PROXY_CACHE[:] = [resolved]
    return resolved


def _detect_static_proxy() -> str | None:
    import urllib.request

    proxies = urllib.request.getproxies()
    raw = proxies.get("https") or proxies.get("http") or proxies.get("all")
    if not raw:
        return None
    parsed = urlparse(raw if "://" in raw else "http://" + raw)
    if not parsed.hostname:
        return None
    port = f":{parsed.port}" if parsed.port else ""
    scheme = "socks5" if parsed.scheme.lower().startswith("socks") else "http"
    return f"{scheme}://{parsed.hostname}{port}"


def _windows_pac_url() -> str | None:
    try:
        import winreg
    except ImportError:
        return None
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "AutoConfigURL")
        return str(value).strip() or None
    except OSError:
        return None


def _detect_pac_proxy() -> str | None:
    pac_url = _windows_pac_url() or os.environ.get("HLBA_PAC_URL")
    if not pac_url:
        return None
    try:
        import urllib.request

        with urllib.request.urlopen(pac_url, timeout=5) as resp:
            script = resp.read().decode("utf-8", "replace")
    except Exception:
        return None
    match = re.search(r"\b(PROXY|HTTPS|SOCKS5|SOCKS)\s+([^\s\"';]+:\d+)", script, re.IGNORECASE)
    if not match:
        return None
    scheme = "socks5" if match.group(1).upper().startswith("SOCKS") else "http"
    return f"{scheme}://{match.group(2)}"


def normalize_proxy_url(proxy: str | None) -> str:

    text = (proxy or "").strip()
    if not text:
        return ""
    if text.lower() in SYSTEM_PROXY_SENTINELS:
        detected = detect_system_proxy()
        if not detected:
            raise ConfigurationError(t("proxy.system_not_found"))
        text = detected
    if "://" not in text:
        text = "http://" + text
    parsed = urlparse(text)
    scheme = parsed.scheme.lower()
    if scheme == "socks":
        scheme = "socks5"
    if scheme not in SUPPORTED_PROXY_SCHEMES:
        raise ConfigurationError(t(
            "proxy.unsupported_scheme",
            scheme=repr(parsed.scheme),
            options=", ".join(sorted(SUPPORTED_PROXY_SCHEMES | {"socks"})),
        ))
    if not parsed.netloc:
        raise ConfigurationError(t("proxy.invalid_url", proxy=repr(proxy)))
    return urlunparse(parsed._replace(scheme=scheme))


def requests_proxy_map(proxy: str | None) -> dict[str, str]:
    normalized = normalize_proxy_url(proxy)
    if not normalized:
        return {}
    return {"http": normalized, "https": normalized}


def apply_proxy_env(proxy: str | None) -> str:

    normalized = normalize_proxy_url(proxy)
    if not normalized:
        return ""
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        os.environ[name] = normalized
    _merge_no_proxy(LOOPBACK_BYPASS)
    return normalized


def redact_proxy_url(proxy: str | None) -> str:
    normalized = normalize_proxy_url(proxy)
    if not normalized:
        return ""
    parsed = urlparse(normalized)
    if "@" not in parsed.netloc:
        return normalized
    host = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    return urlunparse(parsed._replace(netloc=f"<redacted>@{host}{port}"))


def _merge_no_proxy(hosts: tuple[str, ...]) -> None:
    for name in ("NO_PROXY", "no_proxy"):
        existing = [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]
        lowered = {item.lower() for item in existing}
        for host in hosts:
            if host.lower() not in lowered:
                existing.append(host)
                lowered.add(host.lower())
        os.environ[name] = ",".join(existing)


from __future__ import annotations

import os
from urllib.parse import urlparse, urlunparse

from core.error import ConfigurationError


SUPPORTED_PROXY_SCHEMES = {"http", "https", "socks4", "socks4a", "socks5", "socks5h"}
LOOPBACK_BYPASS = ("localhost", "127.0.0.1", "::1")


def normalize_proxy_url(proxy: str | None) -> str:

    text = (proxy or "").strip()
    if not text:
        return ""
    if "://" not in text:
        text = "http://" + text
    parsed = urlparse(text)
    scheme = parsed.scheme.lower()
    if scheme == "socks":
        scheme = "socks5"
    if scheme not in SUPPORTED_PROXY_SCHEMES:
        raise ConfigurationError(
            f"unsupported proxy scheme {parsed.scheme!r}; "
            f"use one of: {', '.join(sorted(SUPPORTED_PROXY_SCHEMES | {'socks'}))}"
        )
    if not parsed.netloc:
        raise ConfigurationError(f"invalid proxy URL: {proxy!r}")
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

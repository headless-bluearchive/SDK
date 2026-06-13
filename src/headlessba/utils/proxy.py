"""Proxy configuration helpers shared by CLI, requests, and browser launchers."""

from __future__ import annotations

import os
from urllib.parse import urlparse, urlunparse


SUPPORTED_PROXY_SCHEMES = {"http", "https", "socks4", "socks4a", "socks5", "socks5h"}
LOOPBACK_BYPASS = ("localhost", "127.0.0.1", "::1")


def normalize_proxy_url(proxy: str | None) -> str:
    """Return a scheme-qualified proxy URL.

    Bare host:port values default to HTTP because both requests and Chromium
    require an explicit scheme. Use socks5://host:port for V2Ray SOCKS.
    """

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
        raise ValueError(
            f"unsupported proxy scheme {parsed.scheme!r}; "
            f"use one of: {', '.join(sorted(SUPPORTED_PROXY_SCHEMES | {'socks'}))}"
        )
    if not parsed.netloc:
        raise ValueError(f"invalid proxy URL: {proxy!r}")
    return urlunparse(parsed._replace(scheme=scheme))


def requests_proxy_map(proxy: str | None) -> dict[str, str]:
    normalized = normalize_proxy_url(proxy)
    if not normalized:
        return {}
    return {"http": normalized, "https": normalized}


def playwright_proxy_options(proxy: str | None) -> dict[str, str] | None:
    normalized = normalize_proxy_url(proxy)
    if not normalized:
        return None
    return {
        "server": normalized,
        "bypass": ",".join(LOOPBACK_BYPASS),
    }


def apply_proxy_env(proxy: str | None) -> str:
    """Set common proxy environment variables for subprocesses/native libraries."""

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

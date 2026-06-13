"""Nexon in-game web login token helpers."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from config.paths import DEFAULT_REPORT_DIR, DEFAULT_TOOLS_DIR, PROJECT_ROOT
from utils.proxy import normalize_proxy_url


DEFAULT_PLAYWRIGHT_LOG_DIR = DEFAULT_REPORT_DIR / "playwright_login"
DEFAULT_LATEST_TOKENS = DEFAULT_PLAYWRIGHT_LOG_DIR / "latest_tokens.json"
DEFAULT_PLAYWRIGHT_TOOL = DEFAULT_TOOLS_DIR / "nexon_playwright_login.py"


@dataclass(frozen=True)
class WebLoginTokens:
    web_token: str
    turnstile_token: str = ""
    hsid: str = ""
    npp: str = ""
    query: dict[str, str] | None = None
    callback_url: str = ""
    source_path: str = ""
    raw: dict[str, Any] | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any], *, source_path: str = "") -> "WebLoginTokens":
        query = data.get("query") if isinstance(data.get("query"), dict) else {}
        return cls(
            web_token=str(data.get("web_token") or query.get("web_token") or ""),
            turnstile_token=str(data.get("turnstile_token") or query.get("turnstile_token") or ""),
            hsid=str(data.get("hsid") or query.get("hsid") or ""),
            npp=str(data.get("npp") or query.get("npp") or ""),
            query={str(k): str(v) for k, v in query.items()},
            callback_url=str(data.get("callback_url") or ""),
            source_path=source_path,
            raw=data,
        )

    def require_web_token(self) -> str:
        if not self.web_token:
            raise ValueError(f"no web_token found in {self.source_path or 'token payload'}")
        return self.web_token


def load_latest_tokens(path: str | Path = DEFAULT_LATEST_TOKENS) -> WebLoginTokens:
    token_path = Path(path).resolve()
    data = json.loads(token_path.read_text(encoding="utf-8"))
    return WebLoginTokens.from_mapping(data, source_path=str(token_path))


def run_playwright_web_login(
    *,
    country: str = "TW",
    locale: str | None = None,
    proxy: str | None = None,
    close_on_callback: bool = True,
    no_redact: bool = True,
    log_dir: str | Path = DEFAULT_PLAYWRIGHT_LOG_DIR,
    extra_args: Sequence[str] = (),
) -> WebLoginTokens:
    """Launch the existing headed Playwright helper, then read latest_tokens.json."""

    tool = DEFAULT_PLAYWRIGHT_TOOL.resolve()
    if not tool.exists():
        raise FileNotFoundError(f"Playwright login helper not found: {tool}")

    resolved_log_dir = Path(log_dir).resolve()
    args = [sys.executable, str(tool), "--country", country, "--log-dir", str(resolved_log_dir)]
    if locale:
        args.extend(["--locale", locale])
    normalized_proxy = normalize_proxy_url(proxy)
    if normalized_proxy:
        args.extend(["--proxy", normalized_proxy])
    if close_on_callback:
        args.append("--close-on-callback")
    if no_redact:
        args.append("--no-redact")
    args.extend(extra_args)
    subprocess.run(args, cwd=str(PROJECT_ROOT), check=True)
    return load_latest_tokens(resolved_log_dir / "latest_tokens.json")


def start_playwright_url(
    url: str,
    *,
    country: str = "TW",
    locale: str | None = None,
    proxy: str | None = None,
    log_dir: str | Path = DEFAULT_PLAYWRIGHT_LOG_DIR,
    no_redact: bool = False,
    extra_args: Sequence[str] = (),
) -> subprocess.Popen[Any]:
    """Open an exact URL in the headed Playwright helper without owning callback port."""

    tool = DEFAULT_PLAYWRIGHT_TOOL.resolve()
    if not tool.exists():
        raise FileNotFoundError(f"Playwright login helper not found: {tool}")

    resolved_log_dir = Path(log_dir).resolve()
    args = [
        sys.executable,
        str(tool),
        "--country",
        country,
        "--open-url",
        url,
        "--no-callback-listener",
        "--log-dir",
        str(resolved_log_dir),
    ]
    if locale:
        args.extend(["--locale", locale])
    normalized_proxy = normalize_proxy_url(proxy)
    if normalized_proxy:
        args.extend(["--proxy", normalized_proxy])
    if no_redact:
        args.append("--no-redact")
    args.extend(extra_args)
    return subprocess.Popen(args, cwd=str(PROJECT_ROOT))


def run_playwright_url_tokens(
    url: str,
    *,
    country: str = "TW",
    locale: str | None = None,
    proxy: str | None = None,
    close_on_callback: bool = True,
    no_redact: bool = True,
    log_dir: str | Path = DEFAULT_PLAYWRIGHT_LOG_DIR,
    extra_args: Sequence[str] = (),
) -> WebLoginTokens:
    """Open an exact URL and return callback-like tokens captured by the helper."""

    tool = DEFAULT_PLAYWRIGHT_TOOL.resolve()
    if not tool.exists():
        raise FileNotFoundError(f"Playwright login helper not found: {tool}")

    resolved_log_dir = Path(log_dir).resolve()
    latest_tokens = resolved_log_dir / "latest_tokens.json"
    if latest_tokens.exists():
        latest_tokens.unlink()
    args = [
        sys.executable,
        str(tool),
        "--country",
        country,
        "--open-url",
        url,
        "--no-callback-listener",
        "--log-dir",
        str(resolved_log_dir),
    ]
    if locale:
        args.extend(["--locale", locale])
    normalized_proxy = normalize_proxy_url(proxy)
    if normalized_proxy:
        args.extend(["--proxy", normalized_proxy])
    if close_on_callback:
        args.append("--close-on-callback")
    if no_redact:
        args.append("--no-redact")
    args.extend(extra_args)
    subprocess.run(args, cwd=str(PROJECT_ROOT), check=True)
    return load_latest_tokens(resolved_log_dir / "latest_tokens.json")


def stop_process(process: subprocess.Popen[Any], *, timeout: float = 5.0) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()

#!/usr/bin/env python3
"""
Open the Nexon TOYSDK in-game sign-in URL with Playwright and capture traffic.

This is the headed/manual-login runner. It keeps a persistent browser profile so
subsequent runs can reuse cookies and local storage.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import threading
import time
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, parse_qsl, urlencode, urlparse, urlunparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from headlessba.utils.proxy import normalize_proxy_url, playwright_proxy_options, redact_proxy_url

from nexon_webview_login import (
    CallbackServer,
    DEFAULT_ENV,
    DEFAULT_GID,
    DEFAULT_LOG_DIR,
    DEFAULT_PORT,
    DEFAULT_UNITY_VERSION,
    JsonlLogger,
    build_signin_url,
    default_toy_headers,
    default_user_agent,
    host_matches,
    infer_locale,
    is_sensitive_name,
    make_hsid,
    normalize_country,
    parse_headers,
    redact_obj,
    redact_value,
    toysdk_encoded_user_agent,
    utc_now,
)


DEFAULT_PROFILE_DIR = DEFAULT_LOG_DIR / "playwright_profile"
MAX_BODY_CHARS = 64 * 1024
MAX_BODY_BYTES = 64 * 1024


def try_parse_body(body: str, content_type: str) -> Any:
    content_type = (content_type or "").lower()
    if not body:
        return ""
    if "application/json" in content_type:
        try:
            return json.loads(body)
        except Exception:
            return body
    if "application/x-www-form-urlencoded" in content_type:
        return parse_qs(body, keep_blank_values=True)
    return body


def body_preview(body: str | None) -> str | None:
    if body is None:
        return None
    if len(body) <= MAX_BODY_CHARS:
        return body
    return body[:MAX_BODY_CHARS] + f"\n...<truncated {len(body) - MAX_BODY_CHARS} chars>"


def query_first(query: dict[str, Any], name: str) -> str:
    value = query.get(name)
    if isinstance(value, list):
        return str(value[0]) if value else ""
    if value is None:
        return ""
    return str(value)


def flatten_query(query: dict[str, Any]) -> dict[str, str]:
    return {str(key): query_first(query, str(key)) for key in query}


def callback_tokens(event: dict[str, Any]) -> dict[str, Any]:
    query = event.get("query") if isinstance(event.get("query"), dict) else {}
    flat = flatten_query(query)
    return {
        "captured_at": utc_now(),
        "path": event.get("path", ""),
        "method": event.get("method", ""),
        "web_token": flat.get("web_token", ""),
        "turnstile_token": flat.get("turnstile_token", ""),
        "hsid": flat.get("hsid", ""),
        "npp": flat.get("npp", ""),
        "query": flat,
    }


def callback_tokens_from_url(url: str, *, method: str = "GET") -> dict[str, Any] | None:
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    if "web_token" not in query and "webtoken" not in query and "turnstile_token" not in query:
        return None
    return callback_tokens(
        {
            "path": parsed.path,
            "method": method,
            "query": query,
            "callback_url": url,
        }
    )


def write_json(path: Path, obj: dict[str, Any], *, redact: bool) -> None:
    data = redact_obj(obj, redact=True) if redact else obj
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def redact_url(url: str, *, redact: bool) -> str:
    if not redact:
        return url
    parsed = urlparse(url)
    if not parsed.query:
        return url
    changed = False
    pairs: list[tuple[str, str]] = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if is_sensitive_name(key):
            pairs.append((key, str(redact_value(value, redact=True))))
            changed = True
        else:
            pairs.append((key, value))
    if not changed:
        return url
    return urlunparse(parsed._replace(query=urlencode(pairs)))


def request_body_event(request: Any, *, redact_raw: bool) -> dict[str, Any]:
    """Return a JSON-safe body record without assuming UTF-8 request bodies."""
    try:
        body_bytes = request.post_data_buffer
    except Exception as exc:
        return {"post_data_error": repr(exc)}

    if body_bytes is None:
        return {"post_data": None}

    content_type = request.headers.get("content-type", "")
    lowered = content_type.lower()
    body_hash = hashlib.sha256(body_bytes).hexdigest()
    record: dict[str, Any] = {
        "post_data_len": len(body_bytes),
        "post_data_sha256": body_hash,
        "post_data_content_type": content_type,
    }

    looks_text = (
        "text/" in lowered
        or "json" in lowered
        or "xml" in lowered
        or "javascript" in lowered
        or "x-www-form-urlencoded" in lowered
    )
    if looks_text:
        text = body_bytes.decode("utf-8", errors="replace")
        if redact_raw:
            record["post_data"] = "<redacted; rerun with --no-redact for raw request body>"
        else:
            record["post_data"] = body_preview(text)
        record["post_data_parsed"] = try_parse_body(text, content_type)
        return record

    preview = body_bytes[:MAX_BODY_BYTES]
    if redact_raw:
        record["post_data_binary_base64"] = "<redacted; rerun with --no-redact for raw request body>"
    else:
        record["post_data_binary_base64"] = base64.b64encode(preview).decode("ascii")
        if len(body_bytes) > len(preview):
            record["post_data_truncated_bytes"] = len(body_bytes) - len(preview)
    return record


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Open Nexon TOYSDK login with Playwright and capture requests/responses.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--country", default="TW", help="Country code used in signin URL")
    parser.add_argument("--locale", help="Locale used in signin URL; inferred from --country if omitted")
    parser.add_argument("--gid", default=DEFAULT_GID, help="Nexon/TOY service id; BA sample uses 2079")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Local callback/httpHook port")
    parser.add_argument("--hsid", default=make_hsid(), help="httpHook session id; SDK uses UUID v4")
    parser.add_argument("--env", default=DEFAULT_ENV, help="signin env: live/pre/stage/dev")
    parser.add_argument("--base-url", help="Override signin base URL")
    parser.add_argument("--open-url", help="Open this exact URL instead of constructing a signin URL")
    parser.add_argument("--extra-query", action="append", default=[], help="Extra query item, e.g. key=value")
    parser.add_argument("--unity-version", default=DEFAULT_UNITY_VERSION, help="Unity version for default TOYSDK UA")
    parser.add_argument("--user-agent", help="Override browser User-Agent")
    parser.add_argument("--proxy", default="", help="Proxy server, e.g. socks5://127.0.0.1:60808 or http://127.0.0.1:60808")
    parser.add_argument("--header", action="append", default=[], help="Extra header to inject, format: 'Name: Value'")
    parser.add_argument("--header-domain", dest="header_domains", action="append", default=["nexon.com"], help="Host suffix for injected headers; use * for all")
    parser.add_argument("--no-default-toy-headers", action="store_true", help="Do not inject default x-toy-* headers")
    parser.add_argument("--no-redact", action="store_true", help="Write raw cookies/tokens/tickets/password-like fields to logs")
    parser.add_argument("--save-response-bodies", action="store_true", help="Save response body previews to responses.jsonl")
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR / "playwright_login", help="Directory for JSONL logs")
    parser.add_argument("--profile-dir", type=Path, default=DEFAULT_PROFILE_DIR, help="Persistent browser profile directory")
    parser.add_argument("--browser", choices=["chromium", "firefox", "webkit"], default="chromium", help="Playwright browser engine")
    parser.add_argument("--channel", help="Use installed branded browser channel, e.g. msedge, chrome")
    parser.add_argument("--headless", action="store_true", help="Run headless; not useful for manual login")
    parser.add_argument("--width", type=int, default=1280, help="Window width")
    parser.add_argument("--height", type=int, default=900, help="Window height")
    parser.add_argument("--listen-host", default="127.0.0.1", help="Callback bind host")
    parser.add_argument("--no-callback-listener", action="store_true", help="Do not bind the local callback port")
    parser.add_argument("--close-on-callback", action="store_true", help="Close browser after first callback request")
    parser.add_argument("--print-url-only", action="store_true", help="Only print constructed URL/session JSON; do not open browser")
    parser.add_argument("--install-help", action="store_true", help="Print Playwright install commands and exit")
    return parser


def print_install_help() -> None:
    print(
        "\n".join(
            [
                "Playwright Python install:",
                "  python -m pip install -r tools\\requirements-nexon-playwright.txt",
                "  python -m playwright install chromium",
                "",
                "If you want to use installed Microsoft Edge instead of Playwright Chromium:",
                "  python -m playwright install msedge",
                "  python tools\\nexon_playwright_login.py --channel msedge --country TW",
            ]
        )
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if args.install_help:
        print_install_help()
        return 0

    args.country = normalize_country(args.country)
    args.locale = infer_locale(args.country, args.locale)
    args.user_agent = args.user_agent or default_user_agent(args.unity_version)
    args.proxy = normalize_proxy_url(args.proxy)
    args.accept_language = f"{args.locale},{args.locale.split('-', 1)[0]};q=0.9,en-US;q=0.8,en;q=0.7"
    args.log_dir = args.log_dir.resolve()
    args.profile_dir = args.profile_dir.resolve()
    args.log_dir.mkdir(parents=True, exist_ok=True)
    args.profile_dir.mkdir(parents=True, exist_ok=True)

    signin_url = args.open_url or build_signin_url(
        env=args.env,
        base_url=args.base_url,
        port=args.port,
        hsid=args.hsid,
        gid=args.gid,
        locale=args.locale,
        country=args.country,
        extra_query=args.extra_query,
    )

    redact = not args.no_redact
    loggers = {
        "requests": JsonlLogger(args.log_dir / "requests.jsonl", redact=redact),
        "responses": JsonlLogger(args.log_dir / "responses.jsonl", redact=redact),
        "callbacks": JsonlLogger(args.log_dir / "callbacks.jsonl", redact=redact),
        "console": JsonlLogger(args.log_dir / "console.jsonl", redact=redact),
        "page": JsonlLogger(args.log_dir / "page.jsonl", redact=redact),
    }

    injected_headers: dict[str, str] = {}
    if not args.no_default_toy_headers:
        injected_headers.update(default_toy_headers(gid=args.gid, country=args.country, locale=args.locale))
    injected_headers.update(parse_headers(args.header))

    session = {
        "created_at": utc_now(),
        "signin_url": signin_url,
        "env": args.env,
        "country": args.country,
        "locale": args.locale,
        "gid": args.gid,
        "port": args.port,
        "hsid": args.hsid,
        "hsid_algorithm": "uuid.uuid4() / Inface generateUUID v4",
        "user_agent": args.user_agent,
        "toysdk_user_agent_base64": toysdk_encoded_user_agent(args.user_agent),
        "accept_language": args.accept_language,
        "proxy": redact_proxy_url(args.proxy) if args.proxy else "",
        "injected_headers": injected_headers,
        "header_domains": args.header_domains,
        "log_dir": str(args.log_dir),
        "profile_dir": str(args.profile_dir),
        "browser": args.browser,
        "channel": args.channel,
        "latest_callback_json": str(args.log_dir / "latest_callback.json"),
        "latest_tokens_json": str(args.log_dir / "latest_tokens.json"),
    }
    (args.log_dir / "session.json").write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(session, ensure_ascii=False, indent=2))
    if args.print_url_only:
        return 0

    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        print(f"[!] playwright import failed: {exc!r}")
        print_install_help()
        return 2

    import queue

    callback_queue: "queue.Queue[dict[str, Any]]"
    callback_queue = queue.Queue()
    callback_server: CallbackServer | None = None
    if not args.no_callback_listener:
        callback_server = CallbackServer(
            host=args.listen_host,
            port=args.port,
            logger=loggers["callbacks"],
            callback_queue=callback_queue,
        )
        callback_server.start()
    close_requested = threading.Event()

    def redact_event(event: dict[str, Any]) -> dict[str, Any]:
        return redact_obj(event, redact=True) if redact else event

    try:
        with sync_playwright() as p:
            browser_type = getattr(p, args.browser)
            launch_args = [
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
            ]
            launch_kwargs: dict[str, Any] = {
                "user_data_dir": str(args.profile_dir),
                "channel": args.channel,
                "headless": args.headless,
                "viewport": {"width": args.width, "height": args.height},
                "user_agent": args.user_agent,
                "locale": args.locale,
                "extra_http_headers": {"Accept-Language": args.accept_language},
                "args": launch_args,
            }
            proxy_options = playwright_proxy_options(args.proxy)
            if proxy_options:
                launch_kwargs["proxy"] = proxy_options
            context = browser_type.launch_persistent_context(**launch_kwargs)

            def route_handler(route: Any, request: Any) -> None:
                try:
                    parsed = urlparse(request.url)
                    headers = dict(request.headers)
                    applied: dict[str, str] = {}
                    if host_matches(parsed.hostname or "", args.header_domains):
                        for name, value in injected_headers.items():
                            headers[name.lower()] = value
                            applied[name] = value
                    route.continue_(headers=headers)
                    if applied:
                        loggers["requests"].write(
                            {
                                "event": "headers_injected",
                                "url": redact_url(request.url, redact=redact),
                                "headers": applied,
                            }
                        )
                except Exception as exc:
                    loggers["requests"].write(
                        {
                            "event": "route_error",
                            "url": redact_url(getattr(request, "url", ""), redact=redact),
                            "error": repr(exc),
                        }
                    )
                    try:
                        route.continue_()
                    except Exception as continue_exc:
                        loggers["requests"].write(
                            {
                                "event": "route_continue_error",
                                "url": redact_url(getattr(request, "url", ""), redact=redact),
                                "error": repr(continue_exc),
                            }
                        )

            context.route("**/*", route_handler)

            def on_request(request: Any) -> None:
                try:
                    event = {
                        "event": "request",
                        "method": request.method,
                        "url": redact_url(request.url, redact=redact),
                        "resource_type": request.resource_type,
                        "headers": dict(request.headers),
                    }
                    event.update(request_body_event(request, redact_raw=redact))
                    loggers["requests"].write(event)
                    tokens = callback_tokens_from_url(request.url, method=request.method)
                    if tokens is not None:
                        write_json(args.log_dir / "latest_tokens.json", tokens, redact=redact)
                        write_json(
                            args.log_dir / "latest_callback.json",
                            {
                                "event": "callback_request_observed",
                                "method": request.method,
                                "path": urlparse(request.url).path,
                                "query": parse_qs(urlparse(request.url).query, keep_blank_values=True),
                                "url": request.url,
                            },
                            redact=redact,
                        )
                        if args.close_on_callback:
                            close_requested.set()
                except Exception as exc:
                    loggers["requests"].write(
                        {
                            "event": "request_capture_error",
                            "url": redact_url(getattr(request, "url", ""), redact=redact),
                            "error": repr(exc),
                        }
                    )

            def on_response(response: Any) -> None:
                try:
                    event: dict[str, Any] = {
                        "event": "response",
                        "url": redact_url(response.url, redact=redact),
                        "status": response.status,
                        "status_text": response.status_text,
                        "headers": dict(response.headers),
                    }
                    if args.save_response_bodies:
                        try:
                            body = response.body()
                            event["body_len"] = len(body)
                            event["body_sha256"] = hashlib.sha256(body).hexdigest()
                            content_type = response.headers.get("content-type", "")
                            lowered = content_type.lower()
                            if (
                                "text/" in lowered
                                or "json" in lowered
                                or "xml" in lowered
                                or "javascript" in lowered
                                or "x-www-form-urlencoded" in lowered
                            ):
                                text = body.decode("utf-8", errors="replace")
                                if redact:
                                    event["body"] = "<redacted; rerun with --no-redact for raw response body>"
                                else:
                                    event["body"] = body_preview(text)
                                event["body_parsed"] = try_parse_body(text, content_type)
                            else:
                                preview = body[:MAX_BODY_BYTES]
                                if redact:
                                    event["body_binary_base64"] = "<redacted; rerun with --no-redact for raw response body>"
                                else:
                                    event["body_binary_base64"] = base64.b64encode(preview).decode("ascii")
                                    if len(body) > len(preview):
                                        event["body_truncated_bytes"] = len(body) - len(preview)
                        except Exception as exc:
                            event["body_error"] = repr(exc)
                    loggers["responses"].write(event)
                except Exception as exc:
                    loggers["responses"].write(
                        {
                            "event": "response_capture_error",
                            "url": redact_url(getattr(response, "url", ""), redact=redact),
                            "error": repr(exc),
                        }
                    )

            def on_console(message: Any) -> None:
                try:
                    loggers["console"].write(
                        {
                            "event": "console",
                            "type": message.type,
                            "text": message.text,
                            "location": message.location,
                        }
                    )
                except Exception as exc:
                    loggers["console"].write({"event": "console_capture_error", "error": repr(exc)})

            def on_request_failed(request: Any) -> None:
                try:
                    failure = request.failure or ""
                    loggers["requests"].write(
                        {
                            "event": "request_failed",
                            "method": request.method,
                            "url": redact_url(request.url, redact=redact),
                            "resource_type": request.resource_type,
                            "failure": failure,
                        }
                    )
                except Exception as exc:
                    loggers["requests"].write({"event": "request_failed_capture_error", "error": repr(exc)})

            def on_page(page: Any) -> None:
                page.on("request", on_request)
                page.on("requestfailed", on_request_failed)
                page.on("response", on_response)
                page.on("console", on_console)
                page.on("close", lambda: close_requested.set())
                loggers["page"].write({"event": "page_created", "url": page.url})

            context.on("page", on_page)
            page = context.pages[0] if context.pages else context.new_page()
            on_page(page)

            if callback_server is not None:
                print(f"[*] Callback listener: http://{args.listen_host}:{args.port}/")
            else:
                print("[*] Callback listener: disabled")
            print(f"[*] Opening browser: {signin_url}")
            if args.proxy:
                print(f"[*] Proxy: {redact_proxy_url(args.proxy)}")
            print(f"[*] Logs: {args.log_dir}")
            print(f"[*] Persistent profile: {args.profile_dir}")
            page.goto(signin_url, wait_until="domcontentloaded", timeout=60000)

            def consume_callback(event: dict[str, Any]) -> None:
                tokens = callback_tokens(event)
                write_json(args.log_dir / "latest_callback.json", event, redact=redact)
                write_json(args.log_dir / "latest_tokens.json", tokens, redact=redact)
                token_preview = redact_value(tokens.get("web_token"), redact=redact)
                turnstile_preview = redact_value(tokens.get("turnstile_token"), redact=redact)
                hsid_preview = redact_value(tokens.get("hsid"), redact=redact)
                print(
                    f"[+] Callback captured: {tokens.get('path')} "
                    f"web_token={token_preview} turnstile_token={turnstile_preview} hsid={hsid_preview}"
                )
                print(f"    Saved: {args.log_dir / 'latest_tokens.json'}")

            while not close_requested.is_set():
                saw_callback = False
                while True:
                    try:
                        consume_callback(callback_queue.get_nowait())
                        saw_callback = True
                    except queue.Empty:
                        break
                if saw_callback and args.close_on_callback:
                    break
                try:
                    page.wait_for_timeout(500)
                except PlaywrightError:
                    break
                time.sleep(0.05)

            context.close()
            return 0
    except PlaywrightError as exc:
        text = str(exc)
        print(f"[!] Playwright failed: {text}")
        if "Executable doesn't exist" in text or "playwright install" in text.lower():
            print_install_help()
        return 4
    except PlaywrightTimeoutError as exc:
        print(f"[!] Playwright timeout: {exc}")
        return 5
    finally:
        if callback_server is not None:
            callback_server.stop()


if __name__ == "__main__":
    raise SystemExit(main())

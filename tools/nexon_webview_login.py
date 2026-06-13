#!/usr/bin/env python3
"""
Open the Nexon TOYSDK in-game sign-in URL in a Python WebView and record traffic.

This intentionally uses Qt WebEngine, not Playwright/WebDriver.
"""

from __future__ import annotations

import argparse
import base64
import datetime as _dt
import json
import os
import queue
import socket
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from headlessba.utils.proxy import normalize_proxy_url, redact_proxy_url

DEFAULT_LOG_DIR = ROOT / "analysis_reports" / "nexon_webview_login"
DEFAULT_UNITY_VERSION = "2021.3.56f2"
DEFAULT_GID = "2079"
DEFAULT_PORT = 12121
DEFAULT_ENV = "live"

SIGNIN_BASE_URLS = {
    "live": "https://signin.nexon.com/signin?type=ingame",
    "live01": "https://signin.nexon.com/signin?type=ingame",
    "custom": "https://signin.nexon.com/signin?type=ingame",
    "pre": "https://pre-signin.nexon.com/signin?type=ingame",
    "stage": "https://test-signin.nexon.com/signin?type=ingame",
    "stage02": "https://test-signin.nexon.com/signin?type=ingame",
    "test": "https://test-signin.nexon.com/signin?type=ingame",
    "dev": "https://dev-signin.nexon.com/signin?type=ingame",
    "development": "https://dev-signin.nexon.com/signin?type=ingame",
}

COUNTRY_LOCALE = {
    "TW": "zh-TW",
    "HK": "zh-HK",
    "MO": "zh-MO",
    "KR": "ko-KR",
    "JP": "ja-JP",
    "TH": "th-TH",
    "US": "en-US",
    "CA": "en-US",
    "GB": "en-GB",
    "AU": "en-AU",
    "SG": "en-SG",
    "ID": "id-ID",
    "VN": "vi-VN",
    "CN": "zh-CN",
}

SENSITIVE_KEYWORDS = (
    "authorization",
    "cookie",
    "set-cookie",
    "token",
    "ticket",
    "password",
    "passwd",
    "secret",
    "web_token",
    "np_token",
    "nptoken",
    "npacode",
    "session",
    "sid",
)


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="milliseconds")


def make_hsid() -> str:
    # Inface SDK generateUUID/v4 behavior: lower-case UUID v4 with hyphens.
    return str(uuid.uuid4())


def default_user_agent(unity_version: str) -> str:
    return (
        f"UnityEngine/{unity_version} "
        "TOYSDK-PC/1.3.132 GSSDK-Windows/1.3.132"
    )


def toysdk_encoded_user_agent(user_agent: str) -> str:
    return base64.b64encode(user_agent.encode("utf-8")).decode("ascii")


def normalize_country(country: str) -> str:
    country = (country or "TW").strip().upper()
    if not country:
        return "TW"
    return country


def infer_locale(country: str, explicit_locale: str | None) -> str:
    if explicit_locale:
        return explicit_locale.strip()
    return COUNTRY_LOCALE.get(normalize_country(country), "en-US")


def build_signin_url(
    *,
    env: str,
    base_url: str | None,
    port: int,
    hsid: str,
    gid: str,
    locale: str,
    country: str,
    extra_query: list[str],
) -> str:
    base = base_url or SIGNIN_BASE_URLS.get(env.lower())
    if not base:
        raise SystemExit(f"Unknown env {env!r}. Use --base-url or one of: {', '.join(sorted(SIGNIN_BASE_URLS))}")

    # Match NXPAuthInsign concat order:
    # base + &port= + &hsid= + &gid= + &locale= + &country=
    parts = [
        base,
        f"&port={port}",
        f"&hsid={quote(hsid, safe='')}",
        f"&gid={quote(str(gid), safe='')}",
        f"&locale={quote(locale, safe='')}",
        f"&country={quote(country, safe='')}",
    ]
    for item in extra_query:
        if not item:
            continue
        if item.startswith("&"):
            parts.append(item)
        elif "=" in item:
            key, value = item.split("=", 1)
            parts.append(f"&{quote(key, safe='')}={quote(value, safe='')}")
        else:
            parts.append(f"&{quote(item, safe='')}=")
    return "".join(parts)


def is_sensitive_name(name: str) -> bool:
    lowered = name.lower()
    return any(word in lowered for word in SENSITIVE_KEYWORDS)


def redact_value(value: Any, *, redact: bool) -> Any:
    if not redact:
        return value
    if value is None:
        return None
    text = str(value)
    if len(text) <= 10:
        return "<redacted>"
    return f"{text[:4]}...{text[-4:]}"


def redact_obj(obj: Any, *, redact: bool) -> Any:
    if not redact:
        return obj
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, value in obj.items():
            if is_sensitive_name(str(key)):
                out[str(key)] = redact_value(value, redact=True)
            else:
                out[str(key)] = redact_obj(value, redact=True)
        return out
    if isinstance(obj, list):
        return [redact_obj(item, redact=True) for item in obj]
    return obj


class JsonlLogger:
    def __init__(self, path: Path, *, redact: bool) -> None:
        self.path = path
        self.redact = redact
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event: dict[str, Any]) -> None:
        event = dict(event)
        event.setdefault("ts", utc_now())
        if self.redact:
            event = redact_obj(event, redact=True)
        line = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
        with self._lock:
            with self.path.open("a", encoding="utf-8") as fp:
                fp.write(line + "\n")


def parse_headers(header_items: list[str]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for item in header_items:
        if ":" not in item:
            raise SystemExit(f"Invalid --header {item!r}; expected 'Name: Value'")
        name, value = item.split(":", 1)
        name = name.strip()
        value = value.strip()
        if not name:
            raise SystemExit(f"Invalid --header {item!r}; empty header name")
        headers[name] = value
    return headers


def default_toy_headers(*, gid: str, country: str, locale: str) -> dict[str, str]:
    language = locale.replace("_", "-").split("-", 1)[0].lower() or "en"
    return {
        "x-toy-service-id": str(gid),
        "x-toy-gid": str(gid),
        "x-toy-country": country,
        "x-toy-locale": locale,
        "x-toy-language": language,
        "x-toy-os": "Windows",
        "x-toy-model": "PC",
    }


def host_matches(host: str, domains: list[str]) -> bool:
    host = host.lower()
    for domain in domains:
        domain = domain.strip().lower()
        if not domain:
            continue
        if domain == "*":
            return True
        if host == domain or host.endswith("." + domain.lstrip(".")):
            return True
    return False


class CallbackServer:
    def __init__(
        self,
        *,
        host: str,
        port: int,
        logger: JsonlLogger,
        callback_queue: "queue.Queue[dict[str, Any]]",
    ) -> None:
        self.host = host
        self.port = port
        self.logger = logger
        self.callback_queue = callback_queue
        self.httpd: ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None

    def start(self) -> None:
        outer = self

        class Handler(BaseHTTPRequestHandler):
            server_version = "TOYSDKCallbackCapture/1.0"

            def log_message(self, fmt: str, *args: Any) -> None:
                return

            def _cors(self) -> None:
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "*")
                self.send_header("Access-Control-Max-Age", "86400")

            def do_OPTIONS(self) -> None:  # noqa: N802
                self.send_response(204)
                self._cors()
                self.end_headers()

            def do_GET(self) -> None:  # noqa: N802
                self._capture()

            def do_POST(self) -> None:  # noqa: N802
                self._capture()

            def _capture(self) -> None:
                parsed = urlparse(self.path)
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length) if length else b""
                body_text = body[:65536].decode("utf-8", errors="replace") if body else ""
                event = {
                    "event": "callback",
                    "method": self.command,
                    "client": self.client_address[0],
                    "path": parsed.path,
                    "query": parse_qs(parsed.query, keep_blank_values=True),
                    "headers": dict(self.headers.items()),
                    "body": body_text,
                }
                outer.logger.write(event)
                outer.callback_queue.put(event)

                response = {
                    "status": True,
                    "result": "captured",
                    "message": "callback captured by nexon_webview_login.py",
                }
                data = json.dumps(response, separators=(",", ":")).encode("utf-8")
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.httpd = ThreadingHTTPServer((self.host, self.port), Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, name="callback-server", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
        if self.thread:
            self.thread.join(timeout=2)


class CdpNetworkLogger:
    def __init__(self, *, port: int, logger: JsonlLogger, stop_event: threading.Event) -> None:
        self.port = port
        self.logger = logger
        self.stop_event = stop_event
        self.thread: threading.Thread | None = None
        self._next_id = 1
        self._pending: dict[int, str] = {}

    def start(self) -> None:
        self.thread = threading.Thread(target=self._run, name="cdp-network-logger", daemon=True)
        self.thread.start()

    def _run(self) -> None:
        try:
            import websocket  # type: ignore
        except Exception as exc:
            self.logger.write({"event": "cdp_error", "error": f"websocket-client import failed: {exc!r}"})
            return

        ws_url = self._wait_for_page_ws()
        if not ws_url:
            self.logger.write({"event": "cdp_error", "error": "timed out waiting for /json target"})
            return

        try:
            ws = websocket.create_connection(ws_url, timeout=5)
            ws.settimeout(1)
        except Exception as exc:
            self.logger.write({"event": "cdp_error", "error": f"connect failed: {exc!r}", "ws_url": ws_url})
            return

        try:
            self._send(ws, "Network.enable", {})
            self._send(ws, "Page.enable", {})
            while not self.stop_event.is_set():
                try:
                    raw = ws.recv()
                except Exception:
                    continue
                try:
                    msg = json.loads(raw)
                except Exception:
                    self.logger.write({"event": "cdp_raw", "raw": raw})
                    continue

                if "method" in msg and str(msg["method"]).startswith("Network."):
                    self.logger.write({"event": "cdp", "message": msg})
                    if msg["method"] == "Network.loadingFinished":
                        request_id = msg.get("params", {}).get("requestId")
                        if request_id:
                            cmd_id = self._send(ws, "Network.getResponseBody", {"requestId": request_id})
                            self._pending[cmd_id] = f"Network.getResponseBody:{request_id}"
                elif "id" in msg and msg.get("id") in self._pending:
                    label = self._pending.pop(msg["id"])
                    self.logger.write({"event": "cdp_response", "label": label, "message": msg})
        finally:
            try:
                ws.close()
            except Exception:
                pass

    def _send(self, ws: Any, method: str, params: dict[str, Any]) -> int:
        cmd_id = self._next_id
        self._next_id += 1
        ws.send(json.dumps({"id": cmd_id, "method": method, "params": params}, separators=(",", ":")))
        return cmd_id

    def _wait_for_page_ws(self) -> str | None:
        deadline = time.time() + 30
        while time.time() < deadline and not self.stop_event.is_set():
            try:
                with urlopen(f"http://127.0.0.1:{self.port}/json", timeout=1) as resp:
                    targets = json.loads(resp.read().decode("utf-8", errors="replace"))
                for target in targets:
                    if target.get("type") == "page" and target.get("webSocketDebuggerUrl"):
                        return target["webSocketDebuggerUrl"]
            except Exception:
                time.sleep(0.5)
        return None


def run_qt_webview(args: argparse.Namespace, *, url: str, loggers: dict[str, JsonlLogger], headers: dict[str, str]) -> int:
    if args.remote_debugging_port:
        os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = str(args.remote_debugging_port)
    if args.proxy:
        flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
        proxy_flags = f"--proxy-server={args.proxy} --proxy-bypass-list=<-loopback>"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = f"{flags} {proxy_flags}".strip()

    try:
        from PyQt5.QtCore import QByteArray, QTimer, QUrl
        from PyQt5.QtWidgets import QApplication, QLineEdit, QMainWindow, QToolBar, QAction
        from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
        from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile, QWebEngineView
    except Exception as exc:
        print("[!] PyQt5 QtWebEngine is not available.", file=sys.stderr)
        print(f"    import error: {exc!r}", file=sys.stderr)
        print("    install: python -m pip install -r tools\\requirements-nexon-webview.txt", file=sys.stderr)
        return 2

    request_logger = loggers["requests"]
    navigation_logger = loggers["navigation"]
    callback_queue: "queue.Queue[dict[str, Any]]" = args.callback_queue

    class RequestInterceptor(QWebEngineUrlRequestInterceptor):
        def interceptRequest(self, info: Any) -> None:  # noqa: N802
            request_url = info.requestUrl().toString()
            parsed = urlparse(request_url)
            injected: dict[str, str] = {}
            if host_matches(parsed.hostname or "", args.header_domains):
                for name, value in headers.items():
                    info.setHttpHeader(QByteArray(name.encode("ascii")), QByteArray(value.encode("utf-8")))
                    injected[name] = value

            header_map: dict[str, str] = {}
            try:
                for key, value in info.httpHeaders().items():
                    header_map[bytes(key).decode("latin1")] = bytes(value).decode("latin1", errors="replace")
            except Exception:
                header_map = {}

            request_logger.write(
                {
                    "event": "request",
                    "method": bytes(info.requestMethod()).decode("ascii", errors="replace"),
                    "url": request_url,
                    "first_party_url": info.firstPartyUrl().toString(),
                    "resource_type": int(info.resourceType()),
                    "headers": header_map,
                    "injected_headers": injected,
                }
            )

    class LoggingPage(QWebEnginePage):
        def javaScriptConsoleMessage(self, level: Any, message: str, line: int, source: str) -> None:  # noqa: N802
            loggers["console"].write(
                {
                    "event": "console",
                    "level": int(level),
                    "message": message,
                    "line": line,
                    "source": source,
                }
            )
            super().javaScriptConsoleMessage(level, message, line, source)

    class BrowserWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("Nexon TOYSDK WebView Capture")
            self.resize(args.width, args.height)

            self.profile = QWebEngineProfile("nexon-toysdk-capture", self)
            self.profile.setHttpUserAgent(args.user_agent)
            if hasattr(self.profile, "setHttpAcceptLanguage"):
                self.profile.setHttpAcceptLanguage(args.accept_language)
            self.profile.setCachePath(str(args.log_dir / "web_cache"))
            self.profile.setPersistentStoragePath(str(args.log_dir / "web_storage"))
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
            self.profile.setRequestInterceptor(RequestInterceptor(self.profile))

            self.view = QWebEngineView(self)
            self.page = LoggingPage(self.profile, self.view)
            self.view.setPage(self.page)
            self.setCentralWidget(self.view)

            toolbar = QToolBar("Navigation", self)
            self.addToolBar(toolbar)
            toolbar.addAction(QAction("Back", self, triggered=self.view.back))
            toolbar.addAction(QAction("Forward", self, triggered=self.view.forward))
            toolbar.addAction(QAction("Reload", self, triggered=self.view.reload))

            self.address = QLineEdit(self)
            self.address.returnPressed.connect(self._navigate_from_bar)
            toolbar.addWidget(self.address)

            self.view.urlChanged.connect(self._url_changed)
            self.view.loadStarted.connect(lambda: navigation_logger.write({"event": "load_started", "url": self.view.url().toString()}))
            self.view.loadFinished.connect(lambda ok: navigation_logger.write({"event": "load_finished", "ok": bool(ok), "url": self.view.url().toString()}))

            self.view.load(QUrl(url))

        def _navigate_from_bar(self) -> None:
            text = self.address.text().strip()
            if text and "://" not in text:
                text = "https://" + text
            if text:
                self.view.load(QUrl(text))

        def _url_changed(self, qurl: Any) -> None:
            text = qurl.toString()
            self.address.setText(text)
            navigation_logger.write({"event": "url_changed", "url": text})

    app = QApplication(sys.argv[:1])
    window = BrowserWindow()
    window.show()

    timer = QTimer()

    def check_callbacks() -> None:
        seen = False
        while True:
            try:
                callback_queue.get_nowait()
                seen = True
            except queue.Empty:
                break
        if seen and args.close_on_callback:
            app.quit()

    timer.timeout.connect(check_callbacks)
    timer.start(500)
    return app.exec_()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Open Nexon TOYSDK in-game login in a Python Qt WebView and capture requests.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--country", default="TW", help="Country code used in signin URL")
    parser.add_argument("--locale", help="Locale used in signin URL; inferred from --country if omitted")
    parser.add_argument("--gid", default=DEFAULT_GID, help="Nexon/TOY service id; BA sample uses 2079")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Local callback/httpHook port")
    parser.add_argument("--hsid", default=make_hsid(), help="httpHook session id; SDK uses UUID v4")
    parser.add_argument("--env", default=DEFAULT_ENV, help="signin env: live/pre/stage/dev")
    parser.add_argument("--base-url", help="Override signin base URL")
    parser.add_argument("--extra-query", action="append", default=[], help="Extra query item, e.g. key=value")
    parser.add_argument("--unity-version", default=DEFAULT_UNITY_VERSION, help="Unity version for default TOYSDK UA")
    parser.add_argument("--user-agent", help="Override WebView User-Agent")
    parser.add_argument("--proxy", default="", help="Proxy server, e.g. socks5://127.0.0.1:60808 or http://127.0.0.1:60808")
    parser.add_argument("--header", action="append", default=[], help="Extra header to inject, format: 'Name: Value'")
    parser.add_argument("--header-domain", dest="header_domains", action="append", default=["nexon.com"], help="Host suffix for injected headers; use * for all")
    parser.add_argument("--no-default-toy-headers", action="store_true", help="Do not inject default x-toy-* headers")
    parser.add_argument("--no-redact", action="store_true", help="Write raw cookies/tokens/tickets to logs")
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR, help="Directory for JSONL logs and WebView storage")
    parser.add_argument("--width", type=int, default=1280, help="Window width")
    parser.add_argument("--height", type=int, default=900, help="Window height")
    parser.add_argument("--listen-host", default="127.0.0.1", help="Callback bind host")
    parser.add_argument("--close-on-callback", action="store_true", help="Close WebView after first callback request")
    parser.add_argument("--print-url-only", action="store_true", help="Only print constructed URL/session JSON; do not open WebView")
    parser.add_argument("--remote-debugging-port", type=int, help="Enable Qt WebEngine DevTools/CDP port")
    parser.add_argument("--capture-cdp", action="store_true", help="Capture Network.* CDP events via remote debugging port")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    args.country = normalize_country(args.country)
    args.locale = infer_locale(args.country, args.locale)
    args.user_agent = args.user_agent or default_user_agent(args.unity_version)
    args.proxy = normalize_proxy_url(args.proxy)
    args.accept_language = f"{args.locale},{args.locale.split('-', 1)[0]};q=0.9,en-US;q=0.8,en;q=0.7"
    args.log_dir = args.log_dir.resolve()
    args.log_dir.mkdir(parents=True, exist_ok=True)

    url = build_signin_url(
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
        "callbacks": JsonlLogger(args.log_dir / "callbacks.jsonl", redact=redact),
        "navigation": JsonlLogger(args.log_dir / "navigation.jsonl", redact=redact),
        "console": JsonlLogger(args.log_dir / "console.jsonl", redact=redact),
        "cdp": JsonlLogger(args.log_dir / "cdp_network.jsonl", redact=redact),
    }

    headers: dict[str, str] = {}
    if not args.no_default_toy_headers:
        headers.update(default_toy_headers(gid=args.gid, country=args.country, locale=args.locale))
    headers.update(parse_headers(args.header))

    session = {
        "created_at": utc_now(),
        "signin_url": url,
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
        "injected_headers": headers,
        "header_domains": args.header_domains,
        "log_dir": str(args.log_dir),
    }
    (args.log_dir / "session.json").write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(session, ensure_ascii=False, indent=2))
    if args.print_url_only:
        return 0

    try:
        with socket.create_connection((args.listen_host, args.port), timeout=0.25):
            print(f"[!] {args.listen_host}:{args.port} is already accepting connections.", file=sys.stderr)
            print("    Stop the existing process or choose another --port.", file=sys.stderr)
            return 3
    except OSError:
        pass

    callback_queue: "queue.Queue[dict[str, Any]]" = queue.Queue()
    args.callback_queue = callback_queue
    callback_server = CallbackServer(
        host=args.listen_host,
        port=args.port,
        logger=loggers["callbacks"],
        callback_queue=callback_queue,
    )
    callback_server.start()
    print(f"[*] Callback listener: http://{args.listen_host}:{args.port}/")
    print(f"[*] Opening WebView: {url}")
    print(f"[*] Logs: {args.log_dir}")

    stop_event = threading.Event()
    cdp_logger: CdpNetworkLogger | None = None
    if args.capture_cdp:
        if not args.remote_debugging_port:
            args.remote_debugging_port = 9222
            os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = str(args.remote_debugging_port)
        cdp_logger = CdpNetworkLogger(port=args.remote_debugging_port, logger=loggers["cdp"], stop_event=stop_event)
        cdp_logger.start()
        print(f"[*] CDP capture: http://127.0.0.1:{args.remote_debugging_port}/json")

    try:
        return run_qt_webview(args, url=url, loggers=loggers, headers=headers)
    finally:
        stop_event.set()
        callback_server.stop()


if __name__ == "__main__":
    raise SystemExit(main())

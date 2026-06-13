#!/usr/bin/env python3
"""Run Nexon web-token -> TOYSDK login -> main-game login replay."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from headlessba.config.paths import DEFAULT_BLUEARCHIVE_CORE_PACKET_DIR, DEFAULT_TOOLS_DIR
from headlessba.log.logging_config import configure_logging
from headlessba import BAReplayClient
from headlessba.modules.runtime.android_mobile_profile import (
    DEFAULT_ANDROID_MOBILE_PROFILE_PATH,
    DEFAULT_GALAXY_STORE_APP_ID,
    AndroidMobileProfile,
    app_version_code_from_client_version,
    fetch_galaxy_store_client_version,
    load_or_create_android_mobile_profile,
    save_android_mobile_profile,
    with_client_version,
)
from headlessba.modules.runtime.android_runtime_profile import (
    AndroidRuntimeProfile,
    find_latest_android_runtime_pull,
    load_android_runtime_profile,
    select_android_runtime_device_id,
)
from headlessba.modules.auth.nexon_login import (
    DEFAULT_OUTPUT_DIR,
    NexonGameCredentials,
    build_credentials,
    run_main_game_login,
    save_toy_results,
    toy_callback_to_dict,
    toy_login_to_dict,
    toy_ticket_to_dict,
)
from headlessba.modules.auth.nexon_web import DEFAULT_LATEST_TOKENS, load_latest_tokens, run_playwright_url_tokens, run_playwright_web_login
from headlessba.modules.auth.nexon_web import start_playwright_url, stop_process
from headlessba.utils.proxy import apply_proxy_env, normalize_proxy_url, redact_proxy_url
from headlessba.modules.runtime.region_config import build_login_url, list_profiles, profile_for
from headlessba.modules.runtime.runtime_config import (
    DEFAULT_LOCAL_LOW_DIR,
    DEFAULT_NXINFACE_CONFIG_PATH,
    NxInfaceConfigInfo,
    NxInfaceTokenInfo,
    PcRuntimeProfile,
    discover_client_version,
    discover_connection_info,
    discover_nxinface_config,
    discover_pc_runtime_profile,
)
from headlessba.modules.auth.toysdk_android import (
    AndroidDeviceProfile,
    AndroidToyConfig,
    AndroidToySdkClient,
    ToySdkAndroidTurnstileRequired,
    android_session_to_dict,
)
from headlessba.modules.auth.toysdk_models import NativeCallbackResult, ToySdkLoginResult, ToySdkTicketResult


DEFAULT_NATIVE_DLL = DEFAULT_BLUEARCHIVE_CORE_PACKET_DIR / "BlueArchive_Data" / "Plugins" / "x86_64" / "gamescale.core.dll"
DEFAULT_NGSX_BRIDGE = DEFAULT_TOOLS_DIR / "ngsx_android_bridge.py"
DEFAULT_NGSX_PC_PROBE = DEFAULT_TOOLS_DIR / "ngsx_pc_probe.py"
DEFAULT_NGSX_PC_DLL = DEFAULT_BLUEARCHIVE_CORE_PACKET_DIR / "BlueArchive_Data" / "Plugins" / "x86_64" / "grap64.dll"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Replay the Nexon Android/mobile HTTP login chain from web_token to game player data.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--full-login",
        action="store_true",
        help="One-shot mode: open Playwright web login if needed, TOYSDK auth, auto gateway, then POST game login",
    )
    parser.add_argument("--list-regions", action="store_true", help="Print built-in region login/API/Gateway profiles")
    parser.add_argument(
        "--native-web-login",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--pc-native-login",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--web-login", action="store_true", help="Open headed Playwright login and capture web_token")
    parser.add_argument(
        "--native-browser",
        choices=["auto", "system", "playwright"],
        default="auto",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--latest-web-token", action="store_true", help="Read analysis latest_tokens.json")
    parser.add_argument("--web-token", help="Use this web_token directly")
    parser.add_argument("--latest-token-path", type=Path, default=DEFAULT_LATEST_TOKENS)
    parser.add_argument("--country", default="TW")
    parser.add_argument("--locale", default="zh-TW")
    parser.add_argument("--region", default="", help="Override runtime server region, e.g. tw/th/eu")
    parser.add_argument("--env", default="live")
    parser.add_argument("--gid", default="2079")
    parser.add_argument("--host-url", default="", help="Main game API host; /gateway is appended if needed")
    parser.add_argument(
        "--api-url",
        default="",
        help="Main game ApiUrl/base used for pre-session API packets such as Account_CheckNexon",
    )
    parser.add_argument(
        "--session-api-url",
        default="",
        help="Main game post-1014 session API URL/base; defaults to ApiUrl, e.g. https://nxm-tw-bagl.nexon.com:5000/api/",
    )
    parser.add_argument("--no-auto-host", action="store_true", help="Disable runtime Hosts/LocalConfig gateway discovery")
    parser.add_argument("--local-config-dir", type=Path, default=DEFAULT_LOCAL_LOW_DIR)
    parser.add_argument(
        "--android-runtime-dir",
        type=Path,
        default=None,
        help="Optional real Android runtime pull directory from tools/collect_android_ba_state.py",
    )
    parser.add_argument(
        "--no-android-runtime-profile",
        action="store_true",
        help="Disable loading a real Android runtime pull; synthetic persistent profile is controlled separately",
    )
    parser.add_argument(
        "--android-profile-json",
        type=Path,
        default=DEFAULT_ANDROID_MOBILE_PROFILE_PATH,
        help="Persistent synthetic Android device profile used for mobile gameauth replay",
    )
    parser.add_argument(
        "--reset-android-profile",
        action="store_true",
        help="Regenerate --android-profile-json instead of reusing persisted device identity",
    )
    parser.add_argument(
        "--no-android-mobile-profile",
        action="store_true",
        help="Disable the synthetic persistent Android profile and use explicit CLI/default fields only",
    )
    parser.add_argument(
        "--android-profile-seed",
        default="",
        help="Optional seed for first-time synthetic profile generation; ignored when profile already exists",
    )
    parser.add_argument(
        "--main-game-profile",
        choices=["android"],
        default="android",
        help="Preset for Android mobile main-game packet fields",
    )
    parser.add_argument(
        "--nxinface-config",
        type=Path,
        default=DEFAULT_NXINFACE_CONFIG_PATH,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--pc-runtime-profile-json",
        type=Path,
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--bundle-version", default="")
    parser.add_argument("--client-version", default="")
    parser.add_argument(
        "--client-version-source",
        choices=["galaxystore", "profile", "runtime", "server-config", "fallback"],
        default="galaxystore",
        help="ClientVersion source when --client-version is not provided",
    )
    parser.add_argument("--galaxy-store-app-id", default=DEFAULT_GALAXY_STORE_APP_ID)
    parser.add_argument("--access-ip", default="")
    parser.add_argument("--ngsm-token", default="")
    parser.add_argument("--np-sn", type=int, default=None, help="Override TOYSDK npSN")
    parser.add_argument("--np-token", default="", help="Override TOYSDK npToken")
    parser.add_argument("--npa-code", default="", help="Override TOYSDK npaCode")
    parser.add_argument("--session-token", default="", help="Override TOYSDK sessionToken")
    parser.add_argument("--guid", default="", help="Override TOYSDK guid")
    parser.add_argument("--member-id", default="", help="Override TOYSDK memberId")
    parser.add_argument("--member-type", default="", help="Override TOYSDK memberType")
    parser.add_argument("--um-key", default="", help="Override TOYSDK umKey")
    parser.add_argument("--game-token", default="", help="Override TOYSDK gameToken")
    parser.add_argument("--game-token-as-np-token", action="store_true", help="Experimental: reuse gameToken as npToken")
    parser.add_argument("--allow-session-token-as-ngsm", action="store_true")
    parser.add_argument(
        "--allow-empty-ngsm-token",
        action="store_true",
        help="Compatibility flag; Android mobile replay now allows an empty NgsmToken by default",
    )
    parser.add_argument(
        "--require-ngsm-token",
        action="store_true",
        help="Strict diagnostic mode: fail locally if TOYSDK/bridge did not provide NgsmToken",
    )
    parser.add_argument(
        "--native-agree-terms",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-agree-mode",
        choices=["none", "ticket", "game-token-all"],
        default="ticket",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-sign-in-with-web-token",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-sign-in-with-ticket",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--launch-platform-type", type=int, default=3)
    parser.add_argument("--store-type", default="google")
    parser.add_argument("--package-name", default="")
    parser.add_argument("--security-token", default="")
    parser.add_argument(
        "--stop-after-toysdk",
        action="store_true",
        help="Stop after TOYSDK login and save artifacts without building main-game packets",
    )
    parser.add_argument(
        "--native-probe-web-ticket-by-game-token",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-probe-web-ticket-with-version",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--native-web-ticket-version", type=int, default=1, help=argparse.SUPPRESS)
    parser.add_argument(
        "--native-probe-game-token-by-scheduler",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-get-ticket-with-npp",
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-probe-account-link-state-nonce",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-probe-account-link-fetch",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-probe-account-link-update-primary",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-probe-toy-sdk-keys",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-probe-trusted-device",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-trusted-device-token",
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-trusted-device-guid",
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-trusted-device-toy-version",
        default="1.3.132",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-account-link-token-source",
        choices=["game-token", "ticket"],
        default="game-token",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-account-link-token-type",
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-account-link-trace-id",
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-primary-platform-type",
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-primary-platform-user-id",
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-primary-platform-guid",
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-link-platform-type",
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--native-link-platform-user-id",
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--proxy",
        default="",
        help="Default proxy for Playwright and Python gateway requests; e.g. socks5://127.0.0.1:60808 or http://127.0.0.1:60808",
    )
    parser.add_argument(
        "--web-proxy",
        default="",
        help="Override proxy for Playwright/Nexon web login only; defaults to --proxy",
    )
    parser.add_argument(
        "--gateway-proxy",
        default="",
        help="Override proxy for Python main-game gateway requests only; defaults to --proxy",
    )
    parser.add_argument(
        "--native-proxy-env",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--native-dll", type=Path, default=DEFAULT_NATIVE_DLL, help=argparse.SUPPRESS)
    parser.add_argument("--no-native-login", action="store_true", help="Only save web token and stop before TOYSDK ticket/login")
    parser.add_argument("--toy-login-json", type=Path, help="Use a previous toy_login_result.json instead of DLL login")
    parser.add_argument(
        "--mobile-direct-login",
        action="store_true",
        help="Use the Android TOYSDK HTTP path after web_token/ticket",
    )
    parser.add_argument(
        "--mobile-legacy-native-ticket",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--mobile-ticket",
        default="",
        help="Use this IAS ticket directly for Android signInWithTicket.nx; avoids DLL ticket exchange",
    )
    parser.add_argument(
        "--mobile-nx-login",
        action="store_true",
        help="Use Android /sdk/signIn.nx with Nexon id/password instead of web_token ticket login",
    )
    parser.add_argument("--nx-id", default="", help="Nexon account id/email for --mobile-nx-login")
    parser.add_argument("--nx-password", default="", help="Nexon account password for --mobile-nx-login")
    parser.add_argument(
        "--mobile-nx-mode",
        choices=["auto", "arena", "nxcom"],
        default="auto",
        help="Android Nexon ID auth mode: auto inspects enterToy memberships, arena uses LoginTypeNXArena(107), nxcom uses legacy NXCom(1)",
    )
    parser.add_argument(
        "--turnstile-cf-token",
        default="",
        help="Cloudflare Turnstile token used as optional.cfToken for Android /sdk/signIn.nx retry",
    )
    parser.add_argument(
        "--turnstile-cf-alt-token",
        default="",
        help="Server cfAltToken used as optional.cfAltToken for Android /sdk/signIn.nx retry",
    )
    parser.add_argument(
        "--turnstile-url",
        default="",
        help="Override Turnstile verification URL; defaults to the Android TOYSDK formula",
    )
    parser.add_argument(
        "--turnstile-no-browser",
        action="store_true",
        help="Do not open Playwright automatically when signIn.nx asks for Turnstile",
    )
    parser.add_argument("--android-uuid", default="", help="Android TOYSDK uuid; defaults to generated UUID")
    parser.add_argument("--android-uuid2", default="", help="Android TOYSDK uuid2; defaults to generated UUID")
    parser.add_argument("--android-adid", default="", help="Android advertising id for TOYSDK headers")
    parser.add_argument("--android-model", default="Pixel 7", help="Android device model for TOYSDK headers")
    parser.add_argument("--android-os-version", default="Android 13", help="Android osVersion header")
    parser.add_argument("--android-mcc", type=int, default=None, help="Android TOYSDK MCC header/body value")
    parser.add_argument("--android-mnc", type=int, default=None, help="Android TOYSDK MNC header/body value")
    parser.add_argument("--android-carrier-name", default="", help="Android TOYSDK carrierName header/body value")
    parser.add_argument("--android-appset-id", default="", help="Android TOYSDK appset-id header")
    parser.add_argument("--android-appset-scope", type=int, default=None, help="Android TOYSDK appset-scope header")
    parser.add_argument("--android-app-version-code", type=int, default=429659)
    parser.add_argument(
        "--android-bolt-url",
        default="",
        help="Override Android TOYSDK Bolt base URL used for /sdk/enterToy.nx and /sdk/getUserInfo.nx",
    )
    parser.add_argument("--android-client-id", default="2708")
    parser.add_argument("--android-game-id", default="toy2079")
    parser.add_argument("--mobile-skip-enter-toy", action="store_true", help="Skip /sdk/enterToy.nx before mobile login")
    parser.add_argument(
        "--mobile-create-np-token",
        action="store_true",
        help="Experimental refresh path: call /sdk/createNPToken.nx after IAS game-token is issued",
    )
    parser.add_argument(
        "--mobile-skip-create-np-token",
        action="store_true",
        help="Deprecated compatibility flag; initial Android ticket login does not call createNPToken by default",
    )
    parser.add_argument("--mobile-skip-user-info", action="store_true", help="Skip /sdk/getUserInfo.nx after mobile login")
    parser.add_argument(
        "--android-bridge",
        action="store_true",
        help="After TOYSDK login, run tools/ngsx_android_bridge.py to trigger Android NgsX/Ngsm state before main-game login",
    )
    parser.add_argument("--bridge-package", default="com.nexon.bluearchive", help="Android package/process name for --android-bridge")
    parser.add_argument("--bridge-device-id", default="", help="Frida/adb device id for --android-bridge, e.g. 127.0.0.1:16448")
    parser.add_argument("--bridge-adb-path", default="adb", help="adb executable path used by --android-bridge")
    parser.add_argument("--bridge-frida-address", default="", help="Optional remote frida-server address for --android-bridge")
    parser.add_argument("--bridge-pid", type=int, default=None, help="Attach this PID directly in --android-bridge")
    parser.add_argument("--bridge-timeout", type=float, default=30.0, help="Seconds to wait for bridge callbacks")
    parser.add_argument("--bridge-attach-timeout", type=float, default=10.0, help="Seconds to wait for Frida device resolution")
    parser.add_argument("--bridge-init-wait-ms", type=int, default=5000, help="Fallback delay before NgsX.Run if Init callback is slow")
    parser.add_argument("--bridge-no-init", action="store_true", help="Call NgsX.Run directly in --android-bridge")
    parser.add_argument("--bridge-output", type=Path, default=None, help="Where to save bridge JSON; defaults to <output-dir>/ngsx_bridge_result.json")
    parser.add_argument(
        "--pc-ngsx-bridge",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--pc-ngsx-dll", type=Path, default=DEFAULT_NGSX_PC_DLL, help=argparse.SUPPRESS)
    parser.add_argument("--pc-ngsx-timeout", type=float, default=10.0, help=argparse.SUPPRESS)
    parser.add_argument("--pc-ngsx-output", type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--pc-ngsx-no-init", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--pc-ngsx-no-close", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--pc-ngsx-getversion-only",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--post", action="store_true", help="Actually POST main-game login requests")
    parser.add_argument("--body-mode", choices=["multipart", "besthttp-multipart", "raw"], default="besthttp-multipart")
    parser.add_argument(
        "--account-check-key-mode",
        choices=["rsa-raw", "rsa-oaep-sha1", "rsa-pkcs1", "rsa-oaep-sha256", "raw-base64", "rsa-base64-text", "rsa-hex-text"],
        default="rsa-oaep-sha1",
        help="Diagnostic Account_CheckNexon ClientGeneratedKey/IV encoding mode",
    )
    parser.add_argument(
        "--account-check-url-mode",
        choices=["api", "gateway"],
        default="api",
        help="Diagnostic Account_CheckNexon post target; client code uses api",
    )
    parser.add_argument(
        "--account-check-field-mode",
        choices=["android-minimal", "full"],
        default="android-minimal",
        help="Account_CheckNexon JSON fields: android-minimal matches Android runtime assignment; full keeps the older diagnostic fields",
    )
    parser.add_argument(
        "--queue-subchain",
        action="store_true",
        help="Experimental: run Queuing_GetCryptoKeys/GetAuthTicket/ProcessWaitingQueue after Queuing_GetTicket",
    )
    parser.add_argument(
        "--queue-subchain-url-mode",
        choices=["gateway", "api"],
        default="gateway",
        help="POST target for queue subchain diagnostics; queueing requests likely belong to gateway",
    )
    parser.add_argument(
        "--queue-carry-crypto-forward",
        action="store_true",
        help="Keep any EncryptedKey/EncryptedIV learned during queue subchain for following requests",
    )
    parser.add_argument(
        "--skip-native-relay-queue",
        action="store_true",
        help="Skip the native LoginTask relay queue before Account_Auth",
    )
    parser.add_argument(
        "--native-relay-battle-pass-id",
        type=int,
        default=None,
        help="Force BattlePass_GetInfo in the native relay queue with this BattlePassId; omitted by default unless known active",
    )
    parser.add_argument(
        "--native-relay-account-link-reward",
        action="store_true",
        help="Also post the conditional Account_LinkReward task in the native relay queue",
    )
    parser.add_argument(
        "--native-relay-continue-on-error",
        action="store_true",
        help="Diagnostic: continue after a native relay queue task returns an Error packet",
    )
    parser.add_argument("--skip-proof-token", action="store_true", help="Skip ProofToken_RequestQuestion/Submit")
    parser.add_argument(
        "--proof-token-stage",
        choices=["before-queue", "after-account-check"],
        default="after-account-check",
        help="Where to run ProofToken_RequestQuestion/Submit in the main-game login chain",
    )
    parser.add_argument(
        "--proof-token-url-mode",
        choices=["api", "gateway"],
        default="api",
        help="Diagnostic ProofToken post target; Android login path uses normal api",
    )
    parser.add_argument(
        "--proof-token-max-attempts",
        type=int,
        default=None,
        help="Abort ProofToken solving if the hint-derived search span is larger than this value",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--device-id", default="")
    parser.add_argument(
        "--android-device-id-source",
        choices=["auto", "uuid", "save-uid", "uuid2", "mid", "idfv", "platform-store-uuid", "none"],
        default="auto",
        help="Runtime profile source used for Account_Auth DeviceUniqueId when --device-id is empty",
    )
    parser.add_argument("--os-type", default="Android", help="Main-game OSType for queue/account auth packets")
    parser.add_argument(
        "--device-system-memory-size",
        type=int,
        default=8192,
        help="Main-game Account_Auth DeviceSystemMemorySize; Android client sends SystemInfo.systemMemorySize",
    )
    parser.add_argument(
        "--game-option-language",
        default="",
        help="Override Account_Auth GameOptionLanguage; default maps locale to FlatData.Language enum name such as Tw/Th/Kr/En",
    )
    parser.add_argument("--account-auth-country", default="", help="Override Account_Auth CountryCode only")
    parser.add_argument("--account-auth-locale", default="", help="Override Account_Auth DeviceLocaleCode only")
    parser.add_argument(
        "--account-auth-advertisement-id",
        default="",
        help="Override Account_Auth AdvertisementId; defaults to Android runtime advertisingId/adid",
    )
    parser.add_argument(
        "--account-auth-idfv",
        default="",
        help="Override Account_Auth Idfv; defaults to Android runtime NxAnalytics idfv",
    )
    parser.add_argument(
        "--account-auth-version",
        type=int,
        default=None,
        help="Diagnostic Account_Auth Version field; omitted by default because Android ProcessSession does not set it",
    )
    parser.add_argument(
        "--account-auth-dev-id",
        default=None,
        help="Diagnostic Account_Auth DevId override; omitted by default unless a captured native AccountInfo.DevId is known",
    )
    parser.add_argument(
        "--omit-account-auth-dev-id",
        action="store_true",
        help="Diagnostic: omit Account_Auth DevId to match the native branch when stored DevId is empty",
    )
    parser.add_argument(
        "--account-auth-imei",
        type=int,
        default=0,
        help="Diagnostic Account_Auth IMEI value; Android leaves the long field at default 0",
    )
    parser.add_argument(
        "--omit-account-auth-imei",
        action="store_true",
        help="Diagnostic: omit Account_Auth IMEI from JSON instead of sending the default 0",
    )
    parser.add_argument("--market-id", default="GooglePlay")
    parser.add_argument(
        "--user-type",
        default="",
        help="Diagnostic Account_Auth UserType; Android ProcessSession does not set this by default",
    )
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--log-level", default="INFO", help="Python logger level for service-oriented components")
    parser.add_argument("--json-logs", action="store_true", help="Emit structured JSON logs for service deployments")
    return parser


def response_packet_from_path(path: str | Path | None) -> dict[str, Any]:
    if not path:
        return {}
    response_path = Path(path)
    if not response_path.exists():
        return {}
    try:
        response = json.loads(response_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    packet = response.get("parsed", response)
    if isinstance(packet, dict):
        for key in ("packet", "payload", "raw"):
            nested = packet.get(key)
            if isinstance(nested, str) and nested.strip().startswith(("{", "[")):
                try:
                    parsed_nested = json.loads(nested)
                except json.JSONDecodeError:
                    continue
                if isinstance(parsed_nested, dict):
                    packet = parsed_nested
                    break
    return packet if isinstance(packet, dict) else {}


def response_path_for_step(flow: dict[str, Any], output_dir: Path, step_name: str) -> Path:
    for step in flow.get("steps", []):
        if isinstance(step, dict) and step.get("name") == step_name and step.get("response_path"):
            return Path(step["response_path"])
    return output_dir / f"{step_name}.response.json"


def collect_player_info(flow: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    auth_packet = response_packet_from_path(response_path_for_step(flow, output_dir, "03_account_auth"))
    sync_packet = response_packet_from_path(flow.get("player_data_path") or response_path_for_step(flow, output_dir, "04_account_login_sync"))
    account_db = auth_packet.get("AccountDB") if isinstance(auth_packet.get("AccountDB"), dict) else {}
    candidates = {
        "AccountId": auth_packet.get("AccountId") or account_db.get("ServerId"),
        "Nickname": account_db.get("Nickname"),
        "Level": account_db.get("Level"),
        "Exp": account_db.get("Exp"),
        "FriendCode": sync_packet.get("FriendCode"),
        "PublisherAccountId": account_db.get("PublisherAccountId"),
    }
    return {key: value for key, value in candidates.items() if value not in (None, "")}


def print_player_info(flow: dict[str, Any], output_dir: Path) -> None:
    info = collect_player_info(flow, output_dir)
    if not info:
        return
    ordered_keys = ("AccountId", "Nickname", "Level", "Exp", "FriendCode", "PublisherAccountId")
    summary = " ".join(f"{key}={info[key]}" for key in ordered_keys if key in info)
    print(f"[*] Player info: {summary}")


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    configure_logging(level=args.log_level, json_logs=args.json_logs)
    if args.list_regions:
        print_region_profiles(args)
        return 0
    args.output_dir = args.output_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    android_mobile_profile = resolve_android_mobile_profile(args)
    apply_android_mobile_profile_defaults(args, android_mobile_profile)
    early_client_version = resolve_client_version(args)
    if early_client_version:
        args.client_version = early_client_version
        version_code = app_version_code_from_client_version(early_client_version)
        if version_code is not None and args.android_app_version_code == 429659:
            args.android_app_version_code = version_code
        android_mobile_profile = update_android_mobile_profile_client_version(
            args,
            android_mobile_profile,
            early_client_version,
        )
    android_runtime_profile = resolve_android_runtime_profile(args)
    apply_android_runtime_profile_defaults(args, android_runtime_profile)
    apply_region_profile_defaults(args)
    apply_main_game_profile_defaults(args)
    validate_android_only_mode(args)
    if args.full_login:
        args.post = True
        if not args.web_token and not args.latest_web_token and not args.web_login and not args.native_web_login:
            args.web_login = True
    if (
        not args.native_web_login
        and not args.pc_native_login
        and not args.mobile_nx_login
        and not args.no_native_login
        and not args.toy_login_json
    ):
        args.mobile_direct_login = True
    if args.native_agree_terms:
        args.native_agree_mode = "game-token-all"

    args.proxy = normalize_proxy_url(args.proxy)
    args.web_proxy = normalize_proxy_url(args.web_proxy or args.proxy)
    args.gateway_proxy = normalize_proxy_url(args.gateway_proxy or args.proxy)
    native_env_proxy = args.proxy or args.web_proxy or args.gateway_proxy
    if args.proxy or args.web_proxy or args.gateway_proxy:
        if args.native_proxy_env:
            apply_proxy_env(native_env_proxy)
        write_json(
            args.output_dir / "proxy_config.json",
            {
                "proxy": redact_proxy_url(args.proxy),
                "web_proxy": redact_proxy_url(args.web_proxy),
                "gateway_proxy": redact_proxy_url(args.gateway_proxy),
                "native_env_proxy": redact_proxy_url(native_env_proxy) if args.native_proxy_env else "",
                "native_proxy_env": bool(args.native_proxy_env),
            },
        )
        if args.proxy:
            print(f"[*] Proxy enabled: {redact_proxy_url(args.proxy)}")
        if args.web_proxy and args.web_proxy != args.proxy:
            print(f"[*] Web proxy: {redact_proxy_url(args.web_proxy)}")
        if args.gateway_proxy and args.gateway_proxy != args.proxy:
            print(f"[*] Gateway proxy: {redact_proxy_url(args.gateway_proxy)}")
        if args.native_proxy_env:
            print("[*] Native proxy env enabled")

    if args.mobile_nx_login:
        print("[*] Login mode: android-nx-login -> toysdk-http -> gateway")
    elif args.mobile_direct_login:
        print("[*] Login mode: web-token/ticket -> android-toysdk-http -> gateway")
    elif args.pc_native_login:
        print("[*] Login mode: web-token -> pc-gamescale-native -> gateway")
    elif args.native_web_login:
        print("[*] Login mode: native-webview-callback -> toysdk -> gateway")
    elif args.web_login:
        print("[*] Login mode: playwright-web-token -> toysdk -> gateway")
    elif args.latest_web_token:
        print("[*] Login mode: latest-web-token -> toysdk -> gateway")
    elif args.web_token:
        print("[*] Login mode: provided-web-token -> toysdk -> gateway")

    web_token = "" if args.native_web_login or args.mobile_nx_login else resolve_web_token(args)
    if web_token:
        write_json(args.output_dir / "selected_web_token.json", {"web_token": web_token})

    if args.no_native_login and not args.toy_login_json and not has_toy_login_overrides(args) and not args.native_web_login:
        print(f"[*] web_token saved: {args.output_dir / 'selected_web_token.json'}")
        print("[*] --no-native-login set; stopping before TOYSDK ticket/login.")
        return 0

    try:
        toy_login = resolve_toy_login(args, web_token)
    except Exception as exc:
        error_payload = {"type": type(exc).__name__, "message": str(exc)}
        write_json(args.output_dir / "toy_login_error.json", error_payload)
        write_json(args.output_dir / "toy_native_error.json", error_payload)
        raise
    toy_login = apply_toy_login_overrides(args, toy_login)
    toy_login = maybe_run_android_bridge(args, toy_login)
    toy_login = maybe_run_pc_ngsx_bridge(args, toy_login)
    write_json(args.output_dir / "toy_login_summary.json", toy_login_to_dict(toy_login))
    if args.stop_after_toysdk:
        print(f"[*] TOYSDK artifacts saved: {args.output_dir}")
        print("[*] --stop-after-toysdk set; stopping before main-game packet build.")
        return 0

    credentials = build_credentials(
        toy_login,
        ngsm_token=args.ngsm_token,
        allow_session_token_as_ngsm=args.allow_session_token_as_ngsm,
        allow_empty_ngsm_token=(args.allow_empty_ngsm_token or not args.require_ngsm_token)
        or (args.pc_ngsx_bridge and not args.pc_ngsx_getversion_only),
    )
    host_url, api_url = resolve_service_urls(args)
    session_api_url = resolve_session_api_url(args, host_url, api_url)
    client_version = args.client_version or resolve_client_version(args)
    client = BAReplayClient(
        host_url=host_url,
        api_url=api_url,
        session_api_url=session_api_url,
        bundle_version=args.bundle_version or client_version or None,
        client_version=client_version,
        timeout=args.timeout,
        proxy=args.gateway_proxy,
    )
    flow = run_main_game_login(
        client,
        credentials,
        output_dir=args.output_dir,
        post=args.post,
        body_mode=args.body_mode,
        client_version=client_version,
        access_ip=args.access_ip,
        advertisement_id=args.account_auth_advertisement_id,
        idfv=args.account_auth_idfv,
        country=args.account_auth_country or args.country,
        locale=args.account_auth_locale or args.locale,
        device_id=args.device_id,
        os_type=args.os_type,
        device_model=args.android_model,
        device_system_memory_size=args.device_system_memory_size,
        os_version=args.android_os_version,
        market_id=args.market_id,
        user_type=args.user_type,
        game_option_language=args.game_option_language,
        account_auth_version=args.account_auth_version,
        account_auth_dev_id=args.account_auth_dev_id,
        omit_account_auth_dev_id=args.omit_account_auth_dev_id,
        account_auth_imei=args.account_auth_imei,
        omit_account_auth_imei=args.omit_account_auth_imei,
        account_check_key_mode=args.account_check_key_mode,
        account_check_url_mode=args.account_check_url_mode,
        account_check_field_mode=args.account_check_field_mode,
        queue_subchain=args.queue_subchain,
        queue_subchain_url_mode=args.queue_subchain_url_mode,
        queue_carry_crypto_forward=args.queue_carry_crypto_forward,
        native_relay_queue=not args.skip_native_relay_queue,
        native_relay_battle_pass_id=args.native_relay_battle_pass_id,
        native_relay_account_link_reward=args.native_relay_account_link_reward,
        native_relay_continue_on_error=args.native_relay_continue_on_error,
        skip_proof_token=args.skip_proof_token,
        proof_token_stage=args.proof_token_stage,
        proof_token_url_mode=args.proof_token_url_mode,
        proof_token_max_attempts=args.proof_token_max_attempts,
    )
    print(f"[*] Flow status: {flow.get('status')}")
    print(f"[*] Output: {args.output_dir}")
    if args.post and flow.get("player_data_path"):
        print_player_info(flow, args.output_dir)
        print(f"[*] Player data response: {flow['player_data_path']}")
    elif not args.post:
        print("[*] Built request packets only. Add --post to submit them.")
    return 0


def resolve_host_url(args: argparse.Namespace) -> str:
    return resolve_service_urls(args)[0]


def resolve_android_mobile_profile(args: argparse.Namespace) -> AndroidMobileProfile | None:
    args.android_mobile_profile = None
    if args.no_android_mobile_profile:
        return None
    profile = load_or_create_android_mobile_profile(
        args.android_profile_json,
        reset=args.reset_android_profile,
        country=args.country,
        locale=args.locale,
        seed=args.android_profile_seed,
    )
    args.android_mobile_profile = profile
    write_json(args.output_dir / "android_mobile_profile.json", profile.to_dict())
    print(
        f"[*] Android mobile profile: {Path(args.android_profile_json).expanduser().resolve()} "
        f"(source={profile.source}, device={profile.device_model}, os={profile.os_version}, "
        f"memory_mb={profile.system_memory_mb})"
    )
    return profile


def update_android_mobile_profile_client_version(
    args: argparse.Namespace,
    profile: AndroidMobileProfile | None,
    client_version: str,
) -> AndroidMobileProfile | None:
    if profile is None or not client_version:
        return profile
    updated = with_client_version(profile, client_version)
    if updated != profile:
        save_android_mobile_profile(args.android_profile_json, updated)
        args.android_mobile_profile = updated
        write_json(args.output_dir / "android_mobile_profile.json", updated.to_dict())
    return updated


def apply_android_mobile_profile_defaults(
    args: argparse.Namespace,
    profile: AndroidMobileProfile | None,
) -> None:
    if profile is None:
        return
    if not args.package_name:
        args.package_name = profile.package_name
    if not args.store_type or args.store_type == "steam":
        args.store_type = profile.store_type
    if not args.android_uuid:
        args.android_uuid = profile.uuid
    if not args.android_uuid2:
        args.android_uuid2 = profile.uuid2
    if not args.android_adid:
        args.android_adid = profile.advertisement_id
    if args.android_model == "Pixel 7":
        args.android_model = profile.device_model
    if args.android_os_version == "Android 13":
        args.android_os_version = profile.os_version
    if args.device_system_memory_size == 8192 and profile.system_memory_mb:
        args.device_system_memory_size = profile.system_memory_mb
    if args.android_mcc is None:
        args.android_mcc = profile.mcc
    if args.android_mnc is None:
        args.android_mnc = profile.mnc
    if not args.android_carrier_name:
        args.android_carrier_name = profile.carrier_name
    if args.android_appset_scope is None:
        args.android_appset_scope = profile.app_set_scope
    if not args.android_appset_id:
        args.android_appset_id = profile.app_set_id
    if not args.device_id:
        args.device_id = profile.device_unique_id or profile.uuid
    if not args.account_auth_advertisement_id:
        args.account_auth_advertisement_id = profile.advertisement_id
    if not args.account_auth_idfv:
        args.account_auth_idfv = profile.idfv
    if not args.account_auth_country:
        args.account_auth_country = profile.country
    if not args.account_auth_locale:
        args.account_auth_locale = profile.locale
    if not args.android_adid:
        args.android_adid = profile.advertisement_id
    if profile.app_version_code and args.android_app_version_code == 429659:
        args.android_app_version_code = profile.app_version_code


def resolve_android_runtime_profile(args: argparse.Namespace) -> AndroidRuntimeProfile | None:
    args.android_runtime_profile = None
    if args.no_android_runtime_profile:
        return None
    root = args.android_runtime_dir
    if root is None:
        return None
    try:
        profile = load_android_runtime_profile(root)
    except Exception as exc:
        error = {"type": type(exc).__name__, "message": str(exc), "path": str(root)}
        write_json(args.output_dir / "android_runtime_profile_error.json", error)
        if args.android_runtime_dir is not None:
            raise
        print(f"[!] Android runtime profile skipped: {type(exc).__name__}: {exc}")
        return None
    args.android_runtime_profile = profile
    write_json(args.output_dir / "android_runtime_profile.json", profile.to_dict())
    print(
        f"[*] Android runtime profile: {profile.source_root} "
        f"(region={profile.region}, device={profile.device_model or 'unknown'}, "
        f"country={profile.user_country or profile.country}, locale={profile.locale})"
    )
    return profile


def apply_android_runtime_profile_defaults(
    args: argparse.Namespace,
    profile: AndroidRuntimeProfile | None,
) -> None:
    if profile is None:
        return
    if not args.region and profile.region:
        args.region = profile.region
    if not args.package_name and profile.app_id:
        args.package_name = profile.app_id
    if not args.android_uuid and profile.uuid:
        args.android_uuid = profile.uuid
    if not args.android_uuid2 and profile.uuid2:
        args.android_uuid2 = profile.uuid2
    if not args.android_adid and profile.advertising_id:
        args.android_adid = profile.advertising_id
    if args.android_model == "Pixel 7" and profile.device_model:
        args.android_model = profile.device_model
    if args.android_os_version == "Android 13" and profile.android_os_version:
        args.android_os_version = profile.android_os_version
    if args.android_app_version_code == 429659 and profile.app_version_code is not None:
        args.android_app_version_code = profile.app_version_code
    if args.android_client_id == "2708" and profile.service_client_id:
        args.android_client_id = profile.service_client_id
    if not args.device_id:
        args.device_id = select_android_runtime_device_id(profile, args.android_device_id_source)
    if not args.game_option_language and profile.language:
        args.game_option_language = profile.language
    if not args.account_auth_country:
        args.account_auth_country = profile.user_country or profile.country
    if not args.account_auth_locale:
        args.account_auth_locale = profile.locale
    if not args.account_auth_advertisement_id:
        args.account_auth_advertisement_id = profile.advertising_id
    if not args.account_auth_idfv:
        args.account_auth_idfv = profile.idfv


def apply_main_game_profile_defaults(args: argparse.Namespace) -> None:
    # Active replay mode is Android mobile gameauth only.  PC/Steam helpers stay
    # in the repository for old artifacts, but they are not applied to CLI runs.
    return


def validate_android_only_mode(args: argparse.Namespace) -> None:
    blocked = []
    if args.pc_native_login:
        blocked.append("--pc-native-login")
    if args.pc_ngsx_bridge:
        blocked.append("--pc-ngsx-bridge")
    if args.pc_ngsx_getversion_only:
        blocked.append("--pc-ngsx-getversion-only")
    if args.native_web_login:
        blocked.append("--native-web-login")
    if args.mobile_legacy_native_ticket:
        blocked.append("--mobile-legacy-native-ticket")
    if args.native_agree_terms:
        blocked.append("--native-agree-terms")
    if args.native_sign_in_with_web_token:
        blocked.append("--native-sign-in-with-web-token")
    if args.native_sign_in_with_ticket:
        blocked.append("--native-sign-in-with-ticket")
    if has_native_probe_flags(args):
        blocked.append("--native-probe-*")
    if args.main_game_profile != "android":
        blocked.append(f"--main-game-profile {args.main_game_profile}")
    if blocked:
        raise SystemExit(
            "PC/Steam login paths are disabled in this Android mobile replay build; "
            f"remove {', '.join(blocked)} and use --web-login/--web-token or --mobile-nx-login."
        )


def load_pc_runtime_profile_override(path: Path) -> tuple[PcRuntimeProfile, NxInfaceConfigInfo | None, dict[str, Any]]:
    profile_path = Path(path).expanduser().resolve()
    data = json.loads(profile_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"PC runtime profile JSON must be an object: {profile_path}")

    pc_data = _first_mapping(data, "pcRuntimeProfile", "pc_runtime_profile", "pc")
    if not pc_data:
        pc_data = data
    pc_profile = PcRuntimeProfile(
        computer_name=str(_first_value(pc_data, "computer_name", "computerName") or ""),
        device_model=str(_first_value(pc_data, "device_model", "deviceModel") or ""),
        os_version=str(_first_value(pc_data, "os_version", "osVersion") or ""),
        system_memory_mb=_to_int(_first_value(pc_data, "system_memory_mb", "systemMemoryMb", "memory_mb")),
        source=str(pc_data.get("source") or "json-override"),
    )

    launcher_data = _first_mapping(data, "launcherState", "launcher_state", "nxinface")
    cid = str(_first_value(launcher_data or data, "cid", "device_id", "deviceId") or "")
    launcher_state = None
    if cid or launcher_data:
        raw_pool = _first_value(launcher_data or {}, "cid_pool", "cidPool") or []
        cid_pool = tuple(str(item) for item in raw_pool if item)
        token_infos = tuple(
            NxInfaceTokenInfo(
                key=str(item.get("key") or ""),
                uid=str(item.get("uid") or ""),
                access_token_type=str(item.get("access_token_type") or item.get("accessTokenType") or ""),
                access_token=str(item.get("access_token") or item.get("accessToken") or ""),
                guid=str(item.get("guid") or ""),
                gid=str(item.get("gid") or ""),
                issuer=str(item.get("issuer") or item.get("iss") or ""),
            )
            for item in (_first_value(launcher_data or {}, "token_infos", "tokenInfos") or [])
            if isinstance(item, dict)
        )
        launcher_state = NxInfaceConfigInfo(
            config_path=str(_first_value(launcher_data or {}, "config_path", "configPath") or profile_path),
            nxi_dirs=tuple(str(item) for item in (_first_value(launcher_data or {}, "nxi_dirs", "nxiDirs") or []) if item),
            cid=cid,
            cid_pool=cid_pool,
            token_infos=token_infos,
        )
    return pc_profile, launcher_state, data


def _first_mapping(data: dict[str, Any], *keys: str) -> dict[str, Any]:
    for key in keys:
        value = data.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _first_value(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return None


def resolve_service_urls(args: argparse.Namespace) -> tuple[str, str]:
    if args.host_url:
        return args.host_url, args.api_url
    if args.no_auto_host:
        return "", args.api_url
    runtime_profile = getattr(args, "android_runtime_profile", None)
    if runtime_profile and runtime_profile.gateway_url:
        print(
            f"[*] Android runtime gateway: {runtime_profile.gateway_endpoint} "
            f"(region={runtime_profile.region}, source={runtime_profile.connection_source})"
        )
        print(f"[*] Android runtime api: {runtime_profile.api_url}")
        return runtime_profile.gateway_url, args.api_url or runtime_profile.api_url
    try:
        info = discover_connection_info(
            country=args.country,
            region=args.region,
            server=args.env,
            local_low_dir=args.local_config_dir,
        )
    except Exception as exc:
        write_json(
            args.output_dir / "connection_info_error.json",
            {"type": type(exc).__name__, "message": str(exc)},
        )
        if args.post:
            raise
        return "", args.api_url

    write_json(args.output_dir / "connection_info.json", info.to_dict())
    print(f"[*] Auto gateway: {info.gateway_endpoint} (region={info.region}, source={info.source})")
    print(f"[*] Auto api: {info.api_url} (region={info.region}, source={info.source})")
    return info.gateway_url, args.api_url or info.api_url


def resolve_session_api_url(args: argparse.Namespace, gateway_url: str, api_url: str) -> str:
    if args.session_api_url:
        return args.session_api_url
    return api_url


def resolve_client_version(args: argparse.Namespace) -> str:
    if args.client_version:
        write_json(args.output_dir / "client_version.json", {"client_version": args.client_version, "source": "cli"})
        return args.client_version
    source = args.client_version_source
    if source == "galaxystore":
        try:
            version, raw = fetch_galaxy_store_client_version(app_id=args.galaxy_store_app_id, timeout=args.timeout)
            write_json(
                args.output_dir / "client_version.json",
                {
                    "client_version": version,
                    "source": "galaxystore",
                    "app_id": args.galaxy_store_app_id,
                    "contentId": (raw.get("DetailMain") or {}).get("contentId") if isinstance(raw, dict) else "",
                    "modifyDate": (raw.get("DetailMain") or {}).get("modifyDate") if isinstance(raw, dict) else "",
                },
            )
            print(f"[*] GalaxyStore client version: {version}")
            return version
        except Exception as exc:
            write_json(
                args.output_dir / "client_version_error.json",
                {"source": "galaxystore", "type": type(exc).__name__, "message": str(exc)},
            )
            print(f"[!] GalaxyStore client version skipped: {type(exc).__name__}: {exc}")
            source = "profile"
    mobile_profile = getattr(args, "android_mobile_profile", None)
    if source == "profile" and mobile_profile is not None and mobile_profile.client_version:
        version = mobile_profile.client_version
        write_json(args.output_dir / "client_version.json", {"client_version": version, "source": "android-mobile-profile"})
        print(f"[*] Android mobile profile client version: {version}")
        return version
    runtime_profile = getattr(args, "android_runtime_profile", None)
    if source in ("runtime", "profile") and runtime_profile is not None and runtime_profile.client_version:
        version = runtime_profile.client_version
        print(f"[*] Android runtime client version: {version}")
        write_json(args.output_dir / "client_version.json", {"client_version": version, "source": "android-runtime-profile"})
        return version
    if source == "server-config":
        version = discover_client_version()
        print(f"[*] Server-config client version: {version}")
        write_json(args.output_dir / "client_version.json", {"client_version": version, "source": "server_config"})
        return version
    version = discover_client_version()
    print(f"[*] Fallback client version: {version}")
    write_json(args.output_dir / "client_version.json", {"client_version": version, "source": "fallback_server_config"})
    return version


def resolve_web_token(args: argparse.Namespace) -> str:
    if args.web_token:
        return args.web_token
    if args.web_login:
        tokens = run_playwright_web_login(
            country=args.country,
            locale=args.locale,
            proxy=args.web_proxy,
            close_on_callback=True,
            no_redact=True,
        )
        return tokens.require_web_token()
    tokens = load_latest_tokens(args.latest_token_path)
    return tokens.require_web_token()


def resolve_toy_login(args: argparse.Namespace, web_token: str) -> ToySdkLoginResult:
    if args.toy_login_json:
        return toy_login_from_file(args.toy_login_json)
    if args.no_native_login:
        return ToySdkLoginResult(
            np_sn=None,
            np_token="",
            npa_code="",
            session_token="",
            guid="",
            member_id="",
            member_type="",
            um_key="",
            game_token="",
            ngsm_token="",
            callback=None,
        )
    if args.mobile_direct_login or args.mobile_nx_login:
        return resolve_mobile_toy_login(args, web_token)
    if not args.native_web_login and not args.pc_native_login:
        return resolve_mobile_toy_login(args, web_token)

    values = {
        "gid": args.gid,
        "serviceId": args.gid,
        "clientId": args.gid,
        "country": args.country,
        "locale": args.locale,
        "packageName": args.package_name,
    }
    from headlessba.modules.auth.toysdk_native import ToySdkNative

    with ToySdkNative(
        dll_path=args.native_dll,
        env=args.env,
        country=args.country,
        locale=args.locale,
        values=values,
    ) as sdk:
        def native_stage_callback(stage: str, value: Any) -> None:
            if stage in ("native_open_port_result", "native_web_callback", "toy_game_token_result", "toy_agree_terms_result"):
                write_json(args.output_dir / f"{stage}.json", toy_callback_to_dict(value))
                if stage == "native_web_callback":
                    callback_web_token = extract_web_token_from_callback(value)
                    if callback_web_token:
                        write_json(args.output_dir / "selected_web_token.json", {"web_token": callback_web_token})
                return
            if stage == "toy_initialize_result":
                inface_result, game_auth_result = value
                write_json(
                    args.output_dir / "toy_initialize_result.json",
                    {
                        "inface": toy_callback_to_dict(inface_result),
                        "game_auth": toy_callback_to_dict(game_auth_result),
                    },
                )
                return
            if stage == "toy_ticket_result":
                write_json(args.output_dir / "toy_ticket_result.json", toy_ticket_to_dict(value))
                return
            if stage in ("toy_partial_login_result", "toy_sign_in_with_ticket_result", "toy_sign_in_with_web_token_result"):
                write_json(args.output_dir / f"{stage}.json", toy_login_to_dict(value))
                return
            write_json(args.output_dir / f"{stage}.json", value)

        if args.native_web_login:
            browser_opener = None
            browser_cleanup = None
            browser_mode = args.native_browser
            if browser_mode == "auto":
                browser_mode = "playwright" if args.web_proxy else "system"
            if browser_mode == "playwright":
                browser_log_dir = args.output_dir / "native_web_playwright"

                def browser_opener(url: str) -> Any:
                    print(f"[*] Native web login via Playwright: {url}")
                    return start_playwright_url(
                        url,
                        country=args.country,
                        locale=args.locale,
                        proxy=args.web_proxy,
                        log_dir=browser_log_dir,
                        no_redact=True,
                    )

                browser_cleanup = stop_process

            ticket, login, login_url, web_callback = sdk.login_with_native_web(
                gid=args.gid,
                launch_platform_type=args.launch_platform_type,
                store_type=args.store_type,
                package_name=args.package_name,
                security_token=args.security_token,
                timeout=args.timeout,
                browser_opener=browser_opener,
                browser_cleanup=browser_cleanup,
                stage_callback=native_stage_callback,
                agree_terms=args.native_agree_terms,
                agree_mode=args.native_agree_mode,
                sign_in_with_ticket=args.native_sign_in_with_ticket,
                sign_in_with_web_token=args.native_sign_in_with_web_token,
            )
            write_json(args.output_dir / "native_web_login_url.json", {"url": login_url})
            write_json(args.output_dir / "native_web_callback.json", toy_callback_to_dict(web_callback))
            callback_web_token = extract_web_token_from_callback(web_callback)
            if callback_web_token:
                write_json(args.output_dir / "selected_web_token.json", {"web_token": callback_web_token})
        else:
            ticket, login = sdk.login_with_web_token(
                web_token,
                launch_platform_type=args.launch_platform_type,
                store_type=args.store_type,
                package_name=args.package_name,
                security_token=args.security_token,
                timeout=args.timeout,
                stage_callback=native_stage_callback,
                agree_terms=args.native_agree_terms,
                agree_mode=args.native_agree_mode,
                sign_in_with_ticket=args.native_sign_in_with_ticket,
                sign_in_with_web_token=args.native_sign_in_with_web_token,
            )
        run_native_probes(args, sdk, ticket=ticket, login=login)
        if sdk.last_partial_login is not None:
            write_json(args.output_dir / "toy_partial_login_result.json", toy_login_to_dict(sdk.last_partial_login))
        if sdk.last_game_token_callback is not None:
            write_json(args.output_dir / "toy_game_token_result.json", toy_callback_to_dict(sdk.last_game_token_callback))
        if sdk.last_agree_terms_callback is not None:
            write_json(args.output_dir / "toy_agree_terms_result.json", toy_callback_to_dict(sdk.last_agree_terms_callback))
        if sdk.last_sign_in_with_ticket_login is not None:
            write_json(
                args.output_dir / "toy_sign_in_with_ticket_result.json",
                toy_login_to_dict(sdk.last_sign_in_with_ticket_login),
            )
        if sdk.last_sign_in_with_ticket_callback is not None:
            write_json(
                args.output_dir / "toy_sign_in_with_ticket_callback.json",
                toy_callback_to_dict(sdk.last_sign_in_with_ticket_callback),
            )
        if sdk.last_sign_in_with_web_token_callback is not None:
            write_json(
                args.output_dir / "toy_sign_in_with_web_token_result.json",
                toy_callback_to_dict(sdk.last_sign_in_with_web_token_callback),
            )
    save_toy_results(args.output_dir, ticket_result=ticket, login_result=login)
    return login


def resolve_mobile_toy_login(args: argparse.Namespace, web_token: str) -> ToySdkLoginResult:
    client = build_android_toy_client(args)
    session = client.session
    ticket_result: ToySdkTicketResult | None = None
    try:
        if args.mobile_nx_login:
            if not args.nx_id or not args.nx_password:
                raise ValueError("--mobile-nx-login requires --nx-id and --nx-password")
            print("[*] Android TOYSDK: enterToy -> Nexon ID auth -> getUserInfo.nx")
            session = run_mobile_nx_login_with_turnstile(args, client)
        else:
            ticket = args.mobile_ticket
            if not ticket:
                if not web_token:
                    raise ValueError("--mobile-direct-login requires --mobile-ticket or a web_token source")
                if args.mobile_legacy_native_ticket:
                    print("[*] Android TOYSDK: web_token -> ticket via legacy native bridge")
                    ticket_result = native_ticket_from_web_token(args, web_token)
                else:
                    print("[*] Android TOYSDK: web_token -> ticket via IAS HTTP")
                    ticket_result = client.issue_ticket_by_web_token(web_token)
                ticket = ticket_result.ticket
                write_json(args.output_dir / "toy_ticket_result.json", toy_ticket_to_dict(ticket_result))
            else:
                write_json(args.output_dir / "toy_ticket_result.json", {"ticket": ticket, "source": "provided"})
            print("[*] Android TOYSDK: enterToy -> signInWithTicket.nx -> IAS game-token -> getUserInfo.nx")
            session = client.login_with_ticket_flow(
                ticket,
                enter_toy=not args.mobile_skip_enter_toy,
                create_np_token=bool(args.mobile_create_np_token and not args.mobile_skip_create_np_token),
                get_user_info=not args.mobile_skip_user_info,
            )
    except Exception:
        write_android_toy_artifacts(args, client, session=session, suffix="_partial")
        raise

    toy_login = session.to_toy_login_result()
    maybe_run_native_probes_after_mobile_login(args, ticket_result=ticket_result, toy_login=toy_login)
    write_android_toy_artifacts(args, client, session=session, toy_login=toy_login)
    return toy_login


def has_native_probe_flags(args: argparse.Namespace) -> bool:
    return any(
        bool(value)
        for value in (
            args.native_probe_toy_sdk_keys,
            args.native_probe_trusted_device,
            args.native_probe_game_token_by_scheduler,
            args.native_probe_account_link_state_nonce,
            args.native_probe_account_link_fetch,
            args.native_probe_account_link_update_primary,
            args.native_probe_web_ticket_by_game_token,
            args.native_probe_web_ticket_with_version,
            args.native_get_ticket_with_npp,
        )
    )


def maybe_run_native_probes_after_mobile_login(
    args: argparse.Namespace,
    *,
    ticket_result: ToySdkTicketResult | None,
    toy_login: ToySdkLoginResult,
) -> None:
    if not has_native_probe_flags(args):
        return

    from headlessba.modules.auth.toysdk_native import ToySdkNative

    values = {
        "gid": args.gid,
        "serviceId": args.gid,
        "clientId": args.gid,
        "country": args.country,
        "locale": args.locale,
        "packageName": args.package_name,
    }
    fallback_ticket = ticket_result or ToySdkTicketResult(
        ticket=args.mobile_ticket or "",
        callback=NativeCallbackResult(
            payload=json.dumps({"ticket": args.mobile_ticket or ""}, ensure_ascii=False),
            parsed={"ticket": args.mobile_ticket or ""},
        ),
    )
    with ToySdkNative(
        dll_path=args.native_dll,
        env=args.env,
        country=args.country,
        locale=args.locale,
        values=values,
    ) as sdk:
        sdk.initialize(launch_platform_type=args.launch_platform_type, timeout=args.timeout)
        run_native_probes(args, sdk, ticket=fallback_ticket, login=toy_login)


def run_mobile_nx_login_with_turnstile(
    args: argparse.Namespace,
    client: AndroidToySdkClient,
) -> Any:
    try:
        return client.login_with_nx_flow(
            args.nx_id,
            args.nx_password,
            enter_toy=not args.mobile_skip_enter_toy,
            get_user_info=not args.mobile_skip_user_info,
            cf_token=args.turnstile_cf_token,
            cf_alt_token=args.turnstile_cf_alt_token,
            login_mode=args.mobile_nx_mode,
        )
    except ToySdkAndroidTurnstileRequired as exc:
        write_json(args.output_dir / "toy_turnstile_required.json", turnstile_error_to_dict(exc))
        cf_alt_token = args.turnstile_cf_alt_token or exc.cf_alt_token
        if args.turnstile_no_browser:
            url = build_turnstile_url(args)
            write_json(
                args.output_dir / "toy_turnstile_manual.json",
                {
                    "turnstile_url": url,
                    "cfAltToken": cf_alt_token,
                    "retry": "rerun with --turnstile-cf-token <turnstile_token> and optional --turnstile-cf-alt-token <cfAltToken>",
                },
            )
            raise
        print("[*] Android TOYSDK: Turnstile required; opening verification browser")
        tokens = run_turnstile_browser(args, cf_alt_token=cf_alt_token)
        cf_token = tokens.turnstile_token
        if not cf_token:
            raise RuntimeError(f"Turnstile browser finished without turnstile_token; raw={tokens.raw}")
        write_json(
            args.output_dir / "toy_turnstile_tokens.json",
            {
                "turnstile_token": cf_token,
                "cfAltToken": cf_alt_token,
                "source": tokens.raw or {
                    "query": tokens.query,
                    "callback_url": tokens.callback_url,
                    "source_path": tokens.source_path,
                },
            },
        )
        print("[*] Android TOYSDK: retry signIn.nx with Turnstile cfToken")
        return client.login_with_nx_flow(
            args.nx_id,
            args.nx_password,
            enter_toy=False,
            get_user_info=not args.mobile_skip_user_info,
            cf_token=cf_token,
            cf_alt_token=cf_alt_token,
            login_mode=args.mobile_nx_mode,
        )


def build_turnstile_url(args: argparse.Namespace) -> str:
    if args.turnstile_url:
        return args.turnstile_url
    query = urlencode(
        {
            "gid": str(args.gid),
            "type": "ingame-mobile",
            "country": args.country,
            "locale": args.locale,
            "use_loading": "false",
        }
    )
    return f"https://signin.nexon.com/security-check/turnstile?{query}"


def run_turnstile_browser(args: argparse.Namespace, *, cf_alt_token: str = "") -> Any:
    url = build_turnstile_url(args)
    log_dir = args.output_dir / "turnstile_playwright"
    write_json(
        args.output_dir / "toy_turnstile_url.json",
        {
            "url": url,
            "cfAltToken": cf_alt_token,
            "callback_scheme": "insign://security-check/turnstile",
            "expected_query": "turnstile_token",
        },
    )
    print(f"[*] Turnstile URL: {url}")
    return run_playwright_url_tokens(
        url,
        country=args.country,
        locale=args.locale,
        proxy=args.web_proxy or args.proxy,
        close_on_callback=True,
        no_redact=True,
        log_dir=log_dir,
    )


def turnstile_error_to_dict(exc: ToySdkAndroidTurnstileRequired) -> dict[str, Any]:
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "errorCode": exc.error_code,
        "errorText": exc.error_text,
        "errorDetail": exc.error_detail,
        "cfAltToken": exc.cf_alt_token,
        "raw": exc.result,
    }


def write_android_toy_artifacts(
    args: argparse.Namespace,
    client: AndroidToySdkClient,
    *,
    session: Any,
    toy_login: ToySdkLoginResult | None = None,
    suffix: str = "",
) -> None:
    if toy_login is None:
        toy_login = session.to_toy_login_result()
    write_json(
        args.output_dir / f"toy_android_login_result{suffix}.json",
        {
            "session": android_session_to_dict(session),
            "toyLogin": toy_login_to_dict(toy_login),
            "device": asdict_safe(client.device),
            "config": asdict_safe(client.config),
            "availableLoginTypes": client.available_login_types,
            "serviceFlags": client.service_flags,
            "selectedLoginType": client.last_login_type,
        },
    )
    write_json(args.output_dir / f"toy_android_requests{suffix}.json", client.last_requests)


def build_android_toy_client(args: argparse.Namespace) -> AndroidToySdkClient:
    store_type = args.store_type if args.store_type and args.store_type != "steam" else "google"
    package_name = args.package_name or "com.nexon.bluearchive"
    runtime_profile = getattr(args, "android_runtime_profile", None)
    runtime_country = args.country
    runtime_locale = args.locale
    initial_country = args.country
    device_country = args.country
    if runtime_profile is not None:
        runtime_country = runtime_profile.user_country or runtime_profile.country or runtime_country
        runtime_locale = runtime_profile.locale or runtime_locale
        initial_country = runtime_profile.initial_country or runtime_profile.country or runtime_country
        device_country = runtime_profile.country or runtime_country
    config = AndroidToyConfig(
        service_id=str(args.gid),
        client_id=str(args.android_client_id),
        game_id=str(args.android_game_id),
        package_name=package_name,
        store_type=store_type,
        app_version_code=int(args.android_app_version_code),
        bolt_url=args.android_bolt_url or AndroidToyConfig.bolt_url,
    )
    device = AndroidDeviceProfile(
        country=runtime_country,
        locale=runtime_locale,
        initial_country=initial_country,
        device_country=device_country,
        uuid=args.android_uuid,
        uuid2=args.android_uuid2,
        os="A",
        os_version=args.android_os_version,
        device_model=args.android_model,
        advertising_id=args.android_adid,
        carrier_name=args.android_carrier_name,
        mnc=int(args.android_mnc or 0),
        mcc=int(args.android_mcc or 0),
        app_set_scope=int(args.android_appset_scope or 0),
        app_set_id=args.android_appset_id,
    )
    return AndroidToySdkClient(
        config=config,
        device=device,
        proxy=args.web_proxy or args.proxy,
        timeout=args.timeout,
    )


def native_ticket_from_web_token(args: argparse.Namespace, web_token: str) -> Any:
    from headlessba.modules.auth.toysdk_native import ToySdkNative

    values = {
        "gid": args.gid,
        "serviceId": args.gid,
        "clientId": args.gid,
        "country": args.country,
        "locale": args.locale,
        "packageName": args.package_name,
    }
    with ToySdkNative(
        dll_path=args.native_dll,
        env=args.env,
        country=args.country,
        locale=args.locale,
        values=values,
    ) as sdk:
        sdk.initialize(launch_platform_type=args.launch_platform_type, timeout=args.timeout)
        return sdk.get_ticket_with_web_token(web_token, timeout=args.timeout)


def run_native_probes(args: argparse.Namespace, sdk: Any, *, ticket: Any, login: ToySdkLoginResult) -> None:
    errors: list[dict[str, str]] = []

    def save_probe_error(stage: str, exc: Exception) -> None:
        errors.append({"stage": stage, "type": type(exc).__name__, "message": str(exc)})
        write_json(args.output_dir / "toy_native_probe_errors.json", errors)
        print(f"[!] Native probe failed: {stage}: {exc}")

    def account_link_token() -> tuple[str, str, str]:
        source = args.native_account_link_token_source
        if source == "ticket":
            value = ticket.ticket
            default_type = "x-ias-ticket"
        else:
            value = login.game_token
            default_type = "x-ias-game-token"
        return source, value, args.native_account_link_token_type or default_type

    def trusted_device_token() -> tuple[str, str]:
        if args.native_trusted_device_token:
            return "override", args.native_trusted_device_token
        if login.game_token:
            return "gameToken", login.game_token
        if login.np_token:
            return "npToken", login.np_token
        return "missing", ""

    if args.native_probe_toy_sdk_keys:
        try:
            callback = sdk.get_sdk_keys(timeout=args.timeout)
            write_json(args.output_dir / "toy_service_sdk_keys_result.json", toy_callback_to_dict(callback))
        except Exception as exc:
            save_probe_error("ToyServiceGetSdkKeys", exc)

    if args.native_probe_trusted_device:
        try:
            token_source, token_value = trusted_device_token()
            if not token_value:
                raise RuntimeError("cannot probe trusted-device without gameToken/npToken")
            guid = args.native_trusted_device_guid or login.guid or (str(login.np_sn) if login.np_sn is not None else "")
            if not guid:
                raise RuntimeError("cannot probe trusted-device without guid")
            payload, callback = sdk.trusted_device_get_registered_status(
                token_value,
                guid=guid,
                toy_version=args.native_trusted_device_toy_version,
                timeout=args.timeout,
            )
            write_json(
                args.output_dir / "toy_service_trusted_device_result.json",
                {
                    "tokenSource": token_source,
                    "guid": guid,
                    "payload": payload,
                    "callback": toy_callback_to_dict(callback),
                },
            )
        except Exception as exc:
            save_probe_error("ToyServiceTrustedDeviceGetRegisteredStatus", exc)

    if args.native_probe_game_token_by_scheduler:
        try:
            game_token, callback = sdk.get_game_token_by_scheduler(ticket.ticket, timeout=args.timeout)
            write_json(
                args.output_dir / "toy_game_token_by_scheduler_result.json",
                {"gameToken": game_token, "callback": toy_callback_to_dict(callback)},
            )
        except Exception as exc:
            save_probe_error("GameAuthInsignGetGameTokenByScheduler", exc)

    trace_id = args.native_account_link_trace_id or str(uuid.uuid4())
    if args.native_probe_account_link_state_nonce:
        try:
            callback = sdk.account_link_state_nonce(timeout=args.timeout)
            write_json(args.output_dir / "toy_account_link_state_nonce_result.json", toy_callback_to_dict(callback))
        except Exception as exc:
            save_probe_error("GameAuthAccountLinkStateNonce", exc)

    if args.native_probe_account_link_fetch:
        try:
            source, token_value, token_type = account_link_token()
            if not token_value:
                raise RuntimeError(f"cannot probe account-link fetch without {source}")
            payload, callback = sdk.account_link_fetch_linked_account(
                token_value,
                token_type=token_type,
                trace_id=trace_id,
                timeout=args.timeout,
            )
            write_json(
                args.output_dir / "toy_account_link_fetch_result.json",
                {
                    "tokenSource": source,
                    "payload": payload,
                    "callback": toy_callback_to_dict(callback),
                },
            )
        except Exception as exc:
            save_probe_error("GameAuthAccountLinkFetchLinkedAccount", exc)

    if args.native_probe_account_link_update_primary:
        try:
            source, token_value, token_type = account_link_token()
            if not token_value:
                raise RuntimeError(f"cannot probe account-link update-primary without {source}")
            platform_type = args.native_primary_platform_type or args.native_link_platform_type or login.member_type
            platform_user_id = (
                args.native_primary_platform_user_id
                or args.native_link_platform_user_id
                or login.member_id
            )
            platform_guid = (
                args.native_primary_platform_guid
                or login.guid
                or (str(login.np_sn) if login.np_sn is not None else "")
            )
            missing = [
                name
                for name, value in (
                    ("primary_platform_type", platform_type),
                    ("primary_platform_user_id", platform_user_id),
                    ("primary_platform_guid", platform_guid),
                )
                if not value
            ]
            if missing:
                raise RuntimeError(f"cannot probe account-link update-primary without {', '.join(missing)}")
            payload, callback = sdk.account_link_update_primary_link(
                token_value,
                token_type=token_type,
                trace_id=trace_id,
                platform_type=platform_type,
                platform_user_id=platform_user_id,
                platform_guid=platform_guid,
                timeout=args.timeout,
            )
            write_json(
                args.output_dir / "toy_account_link_update_primary_result.json",
                {
                    "tokenSource": source,
                    "payload": payload,
                    "callback": toy_callback_to_dict(callback),
                },
            )
        except Exception as exc:
            save_probe_error("GameAuthAccountLinkUpdatePrimaryLink", exc)

    game_token = login.game_token
    if (args.native_probe_web_ticket_by_game_token or args.native_probe_web_ticket_with_version) and not game_token:
        save_probe_error("game_token", RuntimeError("cannot probe web ticket without gameToken"))
        return

    if args.native_probe_web_ticket_by_game_token or args.native_probe_web_ticket_with_version:
        platform_type = args.native_link_platform_type or login.member_type
        platform_user_id = args.native_link_platform_user_id or login.member_id
        injected = {}
        for key, value in (
            ("linkPlatformType", platform_type),
            ("link_platform_type", platform_type),
            ("platformType", platform_type),
            ("linkPlatformUserId", platform_user_id),
            ("link_platform_user_id", platform_user_id),
            ("platformUserId", platform_user_id),
        ):
            if value:
                sdk.set_value(key, value)
                injected[key] = value
        write_json(
            args.output_dir / "toy_native_probe_context.json",
            {
                "gameToken": bool(game_token),
                "memberType": login.member_type,
                "memberId": login.member_id,
                "umKey": login.um_key,
                "injected": injected,
            },
        )

    if args.native_probe_web_ticket_by_game_token:
        try:
            callback = sdk.web_ticket_by_game_token(game_token, timeout=args.timeout)
            write_json(args.output_dir / "toy_web_ticket_by_game_token_result.json", toy_callback_to_dict(callback))
        except Exception as exc:
            save_probe_error("GameAuthInsignWebTicketByGameToken", exc)

    if args.native_probe_web_ticket_with_version:
        try:
            callback = sdk.web_ticket_by_game_token_with_version(
                game_token,
                api_version=args.native_web_ticket_version,
                timeout=args.timeout,
            )
            write_json(
                args.output_dir / "toy_web_ticket_by_game_token_with_version_result.json",
                {
                    "apiVersion": args.native_web_ticket_version,
                    "callback": toy_callback_to_dict(callback),
                },
            )
        except Exception as exc:
            save_probe_error("GameAuthInsignWebTicketByGameTokenWithVersion", exc)

    if args.native_get_ticket_with_npp:
        try:
            npp_ticket = sdk.get_ticket_with_npp(args.native_get_ticket_with_npp, timeout=args.timeout)
            write_json(args.output_dir / "toy_ticket_with_npp_result.json", toy_ticket_to_dict(npp_ticket))
        except Exception as exc:
            save_probe_error("GameAuthInsignGetTicketWithNPP", exc)


def extract_web_token_from_callback(callback: Any) -> str:
    def find(obj: Any) -> Any:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if str(key).lower() in ("web_token", "webtoken"):
                    return value
            for value in obj.values():
                found = find(value)
                if found is not None:
                    return found
        if isinstance(obj, list):
            for item in obj:
                found = find(item)
                if found is not None:
                    return found
        return None

    value = find(callback.parsed)
    return "" if value is None else str(value)


def has_toy_login_overrides(args: argparse.Namespace) -> bool:
    return any(
        (
            args.np_sn is not None,
            bool(args.np_token),
            bool(args.npa_code),
            bool(args.session_token),
            bool(args.guid),
            bool(args.member_id),
            bool(args.member_type),
            bool(args.um_key),
            bool(args.game_token),
            bool(args.ngsm_token),
            bool(args.game_token_as_np_token),
        )
    )


def apply_toy_login_overrides(args: argparse.Namespace, login: ToySdkLoginResult) -> ToySdkLoginResult:
    game_token = args.game_token or login.game_token
    np_token = args.np_token or login.np_token
    ngsm_token = args.ngsm_token or login.ngsm_token
    if args.game_token_as_np_token and not np_token:
        np_token = game_token
    return ToySdkLoginResult(
        np_sn=args.np_sn if args.np_sn is not None else login.np_sn,
        np_token=np_token,
        npa_code=args.npa_code or login.npa_code,
        session_token=args.session_token or login.session_token,
        guid=args.guid or login.guid,
        member_id=args.member_id or login.member_id,
        member_type=args.member_type or login.member_type,
        um_key=args.um_key or login.um_key,
        game_token=game_token,
        ngsm_token=ngsm_token,
        callback=login.callback,
    )


def maybe_run_android_bridge(args: argparse.Namespace, login: ToySdkLoginResult) -> ToySdkLoginResult:
    if not args.android_bridge:
        return login
    if not login.guid or not login.npa_code:
        raise RuntimeError("--android-bridge requires TOYSDK guid and npaCode")

    bridge_output = (args.bridge_output.resolve() if args.bridge_output else (args.output_dir / "ngsx_bridge_result.json"))
    command = build_android_bridge_command(args, login, bridge_output)
    print(f"[*] Android bridge: {args.bridge_package} -> {bridge_output}")
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=max(int(args.bridge_timeout) + 30, 30),
    )
    if completed.returncode != 0:
        error_payload = {
            "type": "AndroidBridgeError",
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "command": command,
            "output": str(bridge_output),
        }
        write_json(args.output_dir / "ngsx_bridge_error.json", error_payload)
        detail = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(f"Android bridge failed with exit={completed.returncode}: {detail}")
    if not bridge_output.exists():
        raise RuntimeError(f"Android bridge did not produce output: {bridge_output}")

    data = json.loads(bridge_output.read_text(encoding="utf-8"))
    ngsm_token = ngsm_token_from_bridge_result(data)
    if ngsm_token and not login.ngsm_token:
        login = toy_login_with_ngsm_token(login, ngsm_token)
    return login


def maybe_run_pc_ngsx_bridge(args: argparse.Namespace, login: ToySdkLoginResult) -> ToySdkLoginResult:
    if not args.pc_ngsx_bridge:
        return login
    if not args.pc_ngsx_getversion_only and (not login.guid or not login.npa_code):
        raise RuntimeError("--pc-ngsx-bridge requires TOYSDK guid and npaCode")

    bridge_output = (
        args.pc_ngsx_output.resolve()
        if args.pc_ngsx_output
        else (args.output_dir / "ngsx_pc_bridge_result.json")
    )
    command = build_pc_ngsx_bridge_command(args, login, bridge_output)
    print(f"[*] PC NGS-X bridge: {args.pc_ngsx_dll} -> {bridge_output}")
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=max(int(args.pc_ngsx_timeout) + 5, 10),
    )
    if completed.returncode != 0:
        error_payload = {
            "type": "PcNgsXBridgeError",
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "command": command,
            "output": str(bridge_output),
        }
        write_json(args.output_dir / "ngsx_pc_bridge_error.json", error_payload)
        detail = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(f"PC NGS-X bridge failed with exit={completed.returncode}: {detail}")
    if not bridge_output.exists():
        raise RuntimeError(f"PC NGS-X bridge did not produce output: {bridge_output}")

    data = json.loads(bridge_output.read_text(encoding="utf-8"))
    ngsm_token = ngsm_token_from_bridge_result(data)
    if ngsm_token and not login.ngsm_token:
        login = toy_login_with_ngsm_token(login, ngsm_token)
    return login


def build_pc_ngsx_bridge_command(args: argparse.Namespace, login: ToySdkLoginResult, output_path: Path) -> list[str]:
    try:
        service_id = int(str(args.gid))
    except ValueError:
        service_id = 2079
    command = [
        sys.executable,
        str(DEFAULT_NGSX_PC_PROBE),
        "--dll",
        str(args.pc_ngsx_dll),
        "--service-id",
        str(service_id),
        "--timeout",
        str(args.pc_ngsx_timeout),
        "--output",
        str(output_path),
        "--diagnose-system",
    ]
    if args.pc_ngsx_getversion_only:
        return command
    command.extend(["--guid", login.guid, "--npa-code", login.npa_code, "--run"])
    if not args.pc_ngsx_no_init:
        command.append("--init")
    if args.pc_ngsx_no_close:
        command.append("--no-close")
    return command


def build_android_bridge_command(args: argparse.Namespace, login: ToySdkLoginResult, output_path: Path) -> list[str]:
    try:
        service_id = int(str(args.gid))
    except ValueError:
        service_id = 2079
    command = [
        sys.executable,
        str(DEFAULT_NGSX_BRIDGE),
        "--package",
        args.bridge_package,
        "--service-id",
        str(service_id),
        "--guid",
        login.guid,
        "--npa-code",
        login.npa_code,
        "--timeout",
        str(args.bridge_timeout),
        "--attach-timeout",
        str(args.bridge_attach_timeout),
        "--init-wait-ms",
        str(args.bridge_init_wait_ms),
        "--output",
        str(output_path),
    ]
    if args.bridge_no_init:
        command.append("--no-init")
    if args.bridge_device_id:
        command.extend(["--device-id", args.bridge_device_id])
    if args.bridge_adb_path:
        command.extend(["--adb-path", args.bridge_adb_path])
    if args.bridge_frida_address:
        command.extend(["--frida-address", args.bridge_frida_address])
    if args.bridge_pid is not None:
        command.extend(["--pid", str(args.bridge_pid)])
    return command


def toy_login_with_ngsm_token(login: ToySdkLoginResult, ngsm_token: str) -> ToySdkLoginResult:
    return ToySdkLoginResult(
        np_sn=login.np_sn,
        np_token=login.np_token,
        npa_code=login.npa_code,
        session_token=login.session_token,
        guid=login.guid,
        member_id=login.member_id,
        member_type=login.member_type,
        um_key=login.um_key,
        game_token=login.game_token,
        ngsm_token=ngsm_token,
        callback=login.callback,
    )


def toy_login_from_file(path: Path) -> ToySdkLoginResult:
    data = json.loads(path.read_text(encoding="utf-8"))
    ngsm_token = str(data.get("ngsmToken") or data.get("ngsm_token") or "")
    if not ngsm_token:
        ngsm_token = load_adjacent_bridge_ngsm_token(path.parent)
    return ToySdkLoginResult(
        np_sn=_to_int(data.get("npSN") or data.get("np_sn")),
        np_token=str(data.get("npToken") or data.get("np_token") or ""),
        npa_code=str(data.get("npaCode") or data.get("npa_code") or ""),
        session_token=str(data.get("sessionToken") or data.get("session_token") or ""),
        guid=str(data.get("guid") or ""),
        member_id=str(data.get("memberId") or data.get("member_id") or ""),
        member_type=str(data.get("memberType") or data.get("member_type") or ""),
        um_key=str(data.get("umKey") or data.get("um_key") or ""),
        game_token=str(data.get("gameToken") or data.get("game_token") or ""),
        ngsm_token=ngsm_token,
        callback=None,
    )


def load_adjacent_bridge_ngsm_token(directory: Path) -> str:
    for name in ("ngsx_bridge_result.json", "ngsx_pc_bridge_result.json", "ngsm_bridge_result.json"):
        path = directory / name
        if not path.exists():
            continue
        try:
            return ngsm_token_from_bridge_result(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return ""


def ngsm_token_from_bridge_result(data: Any) -> str:
    if not isinstance(data, dict):
        return ""
    direct = str(data.get("ngsmToken") or "")
    if direct:
        return direct
    ngsm_result = data.get("ngsmResult")
    if isinstance(ngsm_result, dict):
        token = str(ngsm_result.get("ngsmToken") or "")
        if token:
            return token
    events = data.get("events")
    if isinstance(events, list):
        for event in reversed(events):
            if not isinstance(event, dict):
                continue
            if str(event.get("event") or "") != "ngsm-token":
                continue
            token = str(event.get("ngsmToken") or "")
            if token:
                return token
    return ""


def _to_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def asdict_safe(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    return value


def print_region_profiles(args: argparse.Namespace) -> None:
    port = 12121
    print("region\tcountry\tlocale\tapi_url\tgateway_url\tgateway_endpoint\tlogin_url")
    for base_profile in list_profiles():
        profile = profile_for(base_profile.region, gid=args.gid)
        print(
            "\t".join(
                (
                    profile.region,
                    profile.default_country,
                    profile.default_locale,
                    profile.api_url,
                    profile.gateway_url,
                    profile.gateway_endpoint,
                    build_login_url(profile, port=port, hsid="00000000-0000-4000-8000-000000000000"),
                )
            )
        )


def apply_region_profile_defaults(args: argparse.Namespace) -> None:
    if not args.region and not args.country:
        return
    if args.region:
        base_profile = profile_for(args.region, gid=args.gid)
        args.region = base_profile.region
        if args.country in ("", "TW") and base_profile.region != "tw":
            args.country = base_profile.default_country
        if args.locale in ("", "zh-TW") and base_profile.region != "tw":
            args.locale = base_profile.default_locale
        return
    profile = profile_for(country=args.country, locale=args.locale, gid=args.gid)
    args.region = profile.region
    args.country = args.country or profile.default_country
    args.locale = args.locale or profile.default_locale


if __name__ == "__main__":
    raise SystemExit(main())

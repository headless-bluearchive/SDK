"""Nexon web-token to main-game login replay orchestration."""

from __future__ import annotations

import base64
import json
import platform
import socket
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.request import Request, urlopen

from config.paths import DEFAULT_REPORT_DIR, DEFAULT_TOOLS_DIR
from core.client import BAReplayClient, BuiltRequest, decode_gateway_response
from core.crypto import account_check_nexon_key_iv_fields, generated_key_iv_fields
from modules.auth.login import LoginReplay
from modules.auth.proof_token import proof_token_search_span, solve_proof_token
from modules.auth.toysdk_models import NativeCallbackResult, ToySdkLoginResult, ToySdkTicketResult


DEFAULT_OUTPUT_DIR = DEFAULT_REPORT_DIR

NATIVE_LOGIN_SYNC_NO_PART_PROTOCOLS = [
    20000,  # Cafe_Get
    1003,  # Account_CurrencySync
    2000,  # Character_List
    3000,  # Equipment_List
    5000,  # Echelon_List
    12000,  # MemoryLobby_List
    6000,  # Campaign_List
    22001,  # Arena_Login
    17018,  # Raid_Login
    21000,  # Craft_List
    28001,  # Clan_Login
    33000,  # MomoTalk_OutLine
    19000,  # Scenario_List
    10006,  # Shop_GachaRecruitList
    39006,  # TimeAttackDungeon_Login
    44000,  # CharacterGear_List
    29005,  # Billing_PurchaseListByNexon
    30041,  # EventContent_PermanentList
    45000,  # EliminateRaid_Login
    46000,  # Attachment_Get
    46001,  # Attachment_EmblemList
    47000,  # Sticker_Login
    49000,  # MultiFloorRaid_Sync
    27002,  # ContentSweep_MultiSweepPresetList
    49004,  # MultiFloorRaid_Login
]

NATIVE_RELAY_QUEUE_CORE = [
    {
        "name": "network_time_sync",
        "task_name": "NetworkTimeSyncTask",
        "protocol_name": "NetworkTime_Sync",
        "request_class": "NetworkTimeSyncRequest",
        "slot": "0x18C608DC8",
        "fields": {},
    },
    {
        "name": "academy_get_info",
        "task_name": "AcademyGetInfoNetworkTask",
        "protocol_name": "Academy_GetInfo",
        "request_class": "AcademyGetInfoRequest",
        "slot": "0x18C608608",
        "fields": {},
    },
    {
        "name": "account_login_sync_no_part",
        "task_name": "AccountLoginSyncNoPartNetworkTask",
        "protocol_name": "Account_LoginSync",
        "request_class": "AccountLoginSyncRequest",
        "slot": "0x18C608650",
        "fields": None,
    },
    {
        "name": "item_list",
        "task_name": "ItemListNetworkTask",
        "protocol_name": "Item_List",
        "request_class": "ItemListRequest",
        "slot": "0x18C608D20",
        "fields": {},
    },
    {
        "name": "content_save_get",
        "task_name": "ContentSaveGetNetworkTask",
        "protocol_name": "ContentSave_Get",
        "request_class": "ContentSaveGetRequest",
        "slot": "0x18C6089B0",
        "fields": {},
    },
    {
        "name": "shop_beforehand_gacha_get",
        "task_name": "ShopBeforehandGachaGetNetworkTask",
        "protocol_name": "Shop_BeforehandGachaGet",
        "request_class": "ShopBeforehandGachaGetRequest",
        "slot": "0x18C608F20",
        "fields": {},
    },
]


@dataclass(frozen=True)
class NexonGameCredentials:
    np_sn: int
    np_token: str
    npa_code: str
    ngsm_token: str
    session_token: str = ""
    guid: str = ""
    member_id: str = ""
    member_type: str = ""
    um_key: str = ""


def build_android_security_state(credentials: NexonGameCredentials) -> dict[str, Any]:
    """Describe the Android NgsX state that the pure HTTP replay cannot perform."""

    ngsm_present = bool(credentials.ngsm_token)
    required_run_args = {
        "guid": credentials.guid,
        "npaCode": credentials.npa_code,
    }
    return {
        "platform": "android",
        "serviceId": "2079",
        "security": "NgsX",
        "ngsmTokenPresent": ngsm_present,
        "pureHttpExecutedNgsX": False,
        "status": "ngsm-token-provided" if ngsm_present else "missing-ngsx-side-effect",
        "unitySetup": {
            "NPOptions.setNgsxEnabled": True,
            "Toy.SetServiceKeyForEditor": "2079.MjcwOA.toy2079",
        },
        "observedAndroidFlow": [
            "NPAccount.initialize() initializes NgsX",
            "NPAccount.getUserInfo() calls nPNexonGameSecurity.run(session.getNpaCode(), session.getUserId(), ...)",
            "NPNgsx.run(npaCode, guid) calls native NgsX.Run(guid, npaCode)",
        ],
        "requiredNativeSideEffect": {
            "javaWrapper": "NPNgsx.run(npaCode, guid)",
            "nativeCall": "NgsX.Run(guid, npaCode)",
            "args": required_run_args,
        },
        "optionalBridge": {
            "tool": str((DEFAULT_TOOLS_DIR / "ngsx_android_bridge.py").resolve()),
            "command": (
                "python tools/ngsx_android_bridge.py "
                "--package com.nexon.bluearchive "
                "--toy-login-json <output_dir>/toy_login_summary.json"
            ),
            "notes": [
                "Start the Android game process first.",
                "The bridge only triggers NgsX.Init/Run; Python still performs TOYSDK and main-game HTTP replay.",
            ],
        },
        "expectedImpact": (
            "Queuing_GetTicket can accept an empty NgsmToken in the current replay, "
            "but Account_Auth may return ErrorCode=500 until the NgsX registration side-effect is reproduced."
        ),
    }


def build_credentials(
    toy_login: ToySdkLoginResult,
    *,
    ngsm_token: str = "",
    allow_session_token_as_ngsm: bool = False,
    allow_empty_ngsm_token: bool = False,
) -> NexonGameCredentials:
    resolved_ngsm = ngsm_token or getattr(toy_login, "ngsm_token", "")
    if not resolved_ngsm and allow_session_token_as_ngsm:
        resolved_ngsm = toy_login.session_token
    missing = []
    if toy_login.np_sn is None:
        missing.append("npSN")
    if not toy_login.np_token:
        missing.append("npToken")
    if not toy_login.npa_code:
        missing.append("npaCode")
    if not resolved_ngsm and not allow_empty_ngsm_token:
        missing.append("NgsmToken")
    if missing:
        present = {
            "npSN": toy_login.np_sn,
            "npaCode": bool(toy_login.npa_code),
            "npToken": bool(toy_login.np_token),
            "sessionToken": bool(toy_login.session_token),
            "gameToken": bool(toy_login.game_token),
            "NgsmToken": bool(resolved_ngsm),
        }
        raise ValueError(
            "TOYSDK login result is not enough for Queuing_GetTicket; "
            f"missing {', '.join(missing)}; present={present}. "
            "gameToken is an IAS game_token and is not proven to be the main-game NpToken. "
            "Use --native-probe-web-ticket-by-game-token / --native-probe-web-ticket-with-version "
            "to collect the next native callbacks, pass captured --np-token and --ngsm-token explicitly, "
            "or pass --allow-empty-ngsm-token to let the gateway validate the Android ticket path."
        )
    return NexonGameCredentials(
        np_sn=int(toy_login.np_sn or 0),
        np_token=toy_login.np_token,
        npa_code=toy_login.npa_code,
        ngsm_token=resolved_ngsm,
        session_token=toy_login.session_token,
        guid=toy_login.guid,
        member_id=toy_login.member_id,
        member_type=toy_login.member_type,
        um_key=toy_login.um_key,
    )


def build_queuing_get_ticket_fields(
    credentials: NexonGameCredentials,
    *,
    client_version: str = "",
    access_ip: str = "",
    os_type: str = "Android",
    waiting_ticket: str = "",
    make_standby: bool = False,
) -> dict[str, Any]:
    return {
        "AccessIP": access_ip,
        "ClientVersion": client_version,
        "MakeStandby": make_standby,
        "NgsmToken": credentials.ngsm_token,
        "Npacode": credentials.npa_code,
        "NpSN": credentials.np_sn,
        "NpToken": credentials.np_token,
        "OSType": os_type,
        "PassCheck": False,
        "PassCheckNexon": True,
        "WaitingTicket": waiting_ticket,
    }


def build_account_check_nexon_fields(
    credentials: NexonGameCredentials,
    *,
    enter_ticket: str,
    client_generated_key: str,
    client_generated_iv: str,
    mode: str = "android-minimal",
) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "EnterTicket": enter_ticket,
        "ClientGeneratedKey": client_generated_key,
        "ClientGeneratedIV": client_generated_iv,
    }
    normalized_mode = mode.strip().lower()
    if normalized_mode == "android-minimal":
        return fields
    if normalized_mode == "full":
        fields.update(
            {
                "NpSN": credentials.np_sn,
                "NpToken": credentials.np_token,
                "PassCheckNexonServer": True,
            }
        )
        return fields
    raise ValueError("account_check_field_mode must be 'android-minimal' or 'full'")


def build_account_auth_fields(
    *,
    country: str = "TW",
    locale: str = "zh-TW",
    device_id: str = "",
    os_type: str = "Android",
    os_version: str | None = None,
    device_model: str = "Pixel 7",
    market_id: str = "GooglePlay",
    user_type: str = "",
    access_ip: str = "",
    advertisement_id: str = "",
    idfv: str = "",
    game_option_language: str = "",
    device_system_memory_size: int | None = None,
    imei: int | None = 0,
    omit_imei: bool = False,
    version: int | None = None,
    dev_id: str | None = None,
    omit_dev_id: bool = False,
) -> dict[str, Any]:
    resolved_device_id = device_id or str(uuid.uuid4())
    language = game_option_language or default_game_option_language(country=country, locale=locale)
    resolved_os_type = normalize_account_auth_os_type(os_type)
    fields: dict[str, Any] = {
        "AccessIP": access_ip or outbound_ipv4_address(),
        "AdvertisementId": advertisement_id,
        "CountryCode": country,
        "DeviceLocaleCode": locale,
        "DeviceModel": device_model,
        "DeviceUniqueId": resolved_device_id,
        "GameOptionLanguage": language,
        "Idfv": idfv,
        "IsTeenVersion": False,
        "MarketId": market_id,
        "OSType": resolved_os_type,
        "OSVersion": normalize_account_auth_os_version(os_type=os_type, os_version=os_version),
    }
    if not omit_imei and imei is not None:
        fields["IMEI"] = int(imei)
    if user_type:
        fields["UserType"] = user_type
    if not omit_dev_id and dev_id:
        fields["DevId"] = dev_id
    if version is not None:
        fields["Version"] = int(version)
    if device_system_memory_size is not None:
        fields["DeviceSystemMemorySize"] = int(device_system_memory_size)
    return fields


def build_queuing_get_auth_ticket_fields(
    *,
    client_generated_key: str,
    client_generated_iv: str,
    client_version: str = "",
    os_type: str = "Android",
    make_standby: bool = False,
    pass_check: bool = False,
    pass_check_yostar: bool = False,
    yostar_token: str = "",
    yostar_uid: int = 0,
) -> dict[str, Any]:
    return {
        "ClientGeneratedKey": client_generated_key,
        "ClientGeneratedIV": client_generated_iv,
        "ClientVersion": client_version,
        "MakeStandby": make_standby,
        "OSType": os_type,
        "PassCheck": pass_check,
        "PassCheckYostar": pass_check_yostar,
        "YostarToken": yostar_token,
        "YostarUID": int(yostar_uid),
    }


def build_queuing_process_waiting_queue_fields(
    *,
    auth_ticket: str,
    waiting_ticket: str,
    client_version: str = "",
    os_type: str = "Android",
) -> dict[str, Any]:
    return {
        "AuthTicket": auth_ticket,
        "ClientVersion": client_version,
        "OSType": os_type,
        "WaitingTicket": waiting_ticket,
    }


def default_game_option_language(*, country: str = "", locale: str = "") -> str:
    """Return the FlatData.Language enum name used by GameSetting.Language.ToString()."""

    normalized = (locale or "").strip().lower()
    country_code = (country or "").strip().upper()
    if normalized.startswith("ko") or country_code == "KR":
        return "Kr"
    if normalized.startswith("th") or country_code == "TH":
        return "Th"
    if normalized in ("zh-tw", "zh-hk", "zh-mo") or country_code in ("TW", "HK", "MO"):
        return "Tw"
    if normalized.startswith("ja") or country_code == "JP":
        return "Jp"
    return "En"


def normalize_account_auth_os_type(os_type: str) -> str:
    """Match AccountAuthNetworkTask's RuntimePlatform -> short OSType mapping."""

    raw = (os_type or "").strip()
    normalized = raw.lower().replace("_", "").replace("-", "").replace(" ", "")
    aliases = {
        "android": "A",
        "a": "A",
        "windowsplayer": "W",
        "windowseditor": "W",
        "windows": "W",
        "win": "W",
        "pc": "W",
        "w": "W",
        "iphoneplayer": "I",
        "iphone": "I",
        "ios": "I",
        "i": "I",
    }
    return aliases.get(normalized, raw)


def normalize_account_auth_os_version(*, os_type: str, os_version: str | None) -> str:
    if os_version and os_version.strip().lower() not in ("android 13", "android13"):
        return os_version
    if normalize_account_auth_os_type(os_type) == "A":
        return "Android OS 13 / API-33"
    return os_version or platform.version()


def local_ipv4_address() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return ""


def outbound_ipv4_address(timeout: float = 5.0) -> str:
    request = Request("https://api.ipify.org", headers={"User-Agent": "BAReplay/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            value = response.read(64).decode("ascii", errors="ignore").strip()
    except Exception:
        return local_ipv4_address()
    if value.count(".") == 3 and all(part.isdigit() and 0 <= int(part) <= 255 for part in value.split(".")):
        return value
    return local_ipv4_address()


def build_account_login_sync_fields(
    *,
    skill_cut_in_option: str = "All",
    sync_protocols: list[int] | None = None,
) -> dict[str, Any]:
    return {"SkillCutInOption": skill_cut_in_option, "SyncProtocols": list(sync_protocols or [])}


def build_account_login_sync_no_part_fields(*, skill_cut_in_option: str = "All") -> dict[str, Any]:
    return build_account_login_sync_fields(
        skill_cut_in_option=skill_cut_in_option,
        sync_protocols=NATIVE_LOGIN_SYNC_NO_PART_PROTOCOLS,
    )


def save_toy_results(
    output_dir: str | Path,
    *,
    ticket_result: ToySdkTicketResult | None = None,
    login_result: ToySdkLoginResult | None = None,
) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    if ticket_result is not None:
        write_json(out / "toy_ticket_result.json", toy_ticket_to_dict(ticket_result))
    if login_result is not None:
        write_json(out / "toy_login_result.json", toy_login_to_dict(login_result))


def run_main_game_login(
    client: BAReplayClient,
    credentials: NexonGameCredentials,
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    post: bool = False,
    body_mode: str = "multipart",
    client_version: str = "",
    access_ip: str = "",
    advertisement_id: str = "",
    idfv: str = "",
    country: str = "TW",
    locale: str = "zh-TW",
    device_id: str = "",
    os_type: str = "Android",
    os_version: str | None = None,
    device_model: str = "Pixel 7",
    device_system_memory_size: int | None = 8192,
    market_id: str = "GooglePlay",
    user_type: str = "",
    game_option_language: str = "",
    account_auth_version: int | None = None,
    account_auth_dev_id: str | None = None,
    omit_account_auth_dev_id: bool = False,
    account_auth_imei: int | None = 0,
    omit_account_auth_imei: bool = False,
    enter_ticket: str = "",
    account_check_key_mode: str = "rsa-oaep-sha1",
    account_check_url_mode: str = "api",
    account_check_field_mode: str = "android-minimal",
    queue_subchain: bool = False,
    queue_subchain_url_mode: str = "gateway",
    queue_carry_crypto_forward: bool = False,
    native_relay_queue: bool = True,
    native_relay_battle_pass_id: int | None = None,
    native_relay_account_link_reward: bool = False,
    native_relay_continue_on_error: bool = False,
    skip_proof_token: bool = False,
    proof_token_stage: str = "after-account-check",
    proof_token_url_mode: str = "api",
    proof_token_max_attempts: int | None = None,
) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    login = LoginReplay(client)
    flow: dict[str, Any] = {
        "post": post,
        "host_url": client.host_url,
        "api_url": client.api_host_url,
        "session_api_url": client.session_api_host_url,
        "body_mode": body_mode,
        "account_check_key_mode": account_check_key_mode,
        "account_check_url_mode": account_check_url_mode,
        "account_check_field_mode": account_check_field_mode,
        "queue_subchain": queue_subchain,
        "queue_subchain_url_mode": queue_subchain_url_mode,
        "queue_carry_crypto_forward": queue_carry_crypto_forward,
        "native_relay_queue": native_relay_queue,
        "native_relay_battle_pass_id": native_relay_battle_pass_id,
        "native_relay_account_link_reward": native_relay_account_link_reward,
        "native_relay_continue_on_error": native_relay_continue_on_error,
        "skip_proof_token": skip_proof_token,
        "proof_token_stage": proof_token_stage,
        "proof_token_url_mode": proof_token_url_mode,
        "proof_token_max_attempts": proof_token_max_attempts,
        "native_sequence_model": [
            "Queuing_GetTicket(gateway)",
            "Account_CheckNexon(api)",
            "Account_CheckNexon response SessionKey is injected into later RequestPacket hashes",
            "ProofToken_RequestQuestion/Submit(session_api) when enabled",
            "Native relay queue(session_api): NetworkTimeSync, AcademyGetInfo, AccountLoginSyncNoPart, ItemList, ContentSaveGet, ShopBeforehandGachaGet, optional BattlePassGetInfo/AccountLinkReward",
            "Account_Auth(session_api)",
            "Account_LoginSync(session_api)",
        ],
        "steps": [],
    }
    android_security_state = build_android_security_state(credentials)
    flow["android_security_state"] = android_security_state
    flow["android_security_state_path"] = str((out / "android_security_state.json").resolve())
    write_json(out / "android_security_state.json", android_security_state)
    write_json(
        out / "game_login_args.json",
        {
            "credentials": asdict(credentials),
            "client_version": client_version,
            "android_security_state_path": flow["android_security_state_path"],
        },
    )

    resolved_access_ip = access_ip or outbound_ipv4_address()
    flow["access_ip"] = resolved_access_ip
    write_json(out / "access_ip.json", {"access_ip": resolved_access_ip, "source": "cli" if access_ip else "outbound"})

    resolved_proof_token_stage = _normalize_proof_token_stage(proof_token_stage)
    flow["proof_token_stage"] = resolved_proof_token_stage
    if not skip_proof_token and resolved_proof_token_stage == "before-queue":
        run_proof_token_stage(
            client,
            login,
            output_dir=out,
            flow=flow,
            post=post,
            body_mode=body_mode,
            proof_token_url_mode=proof_token_url_mode,
            proof_token_max_attempts=proof_token_max_attempts,
            stage=resolved_proof_token_stage,
            name_prefix="00",
        )

    queue_fields = build_queuing_get_ticket_fields(
        credentials,
        client_version=client_version,
        access_ip=resolved_access_ip,
        os_type=os_type,
    )
    queue_request = login.queuing_get_ticket(queue_fields)
    queue_record = save_built_request(out, "01_queuing_get_ticket", queue_request)
    flow["steps"].append(queue_record)

    if not post:
        flow["status"] = "built_queuing_get_ticket_only"
        flow["next"] = "rerun with --post --host-url, or pass --enter-ticket to build Account_CheckNexon offline"
        write_json(out / "main_login_flow.json", flow)
        return flow

    queue_response = post_built_request_to_url(
        client,
        queue_request,
        url=client.gateway_url,
        body_mode=body_mode,
    )
    write_json(out / "01_queuing_get_ticket.response.json", queue_response)
    flow["steps"][-1]["response_path"] = str((out / "01_queuing_get_ticket.response.json").resolve())

    parsed_queue = queue_response.get("parsed")
    resolved_enter_ticket = enter_ticket or _as_str(_find_first(parsed_queue, "EnterTicket", "enterTicket"))
    resolved_waiting_ticket = _as_str(_find_first(parsed_queue, "WaitingTicket", "waitingTicket"))
    if not resolved_enter_ticket:
        flow["status"] = "missing_enter_ticket"
        flow["queue_response"] = parsed_queue
        write_json(out / "main_login_flow.json", flow)
        raise RuntimeError("Queuing_GetTicket did not return EnterTicket; see 01_queuing_get_ticket.response.json")

    if queue_subchain:
        queue_stage = run_queue_subchain(
            client,
            login,
            output_dir=out,
            flow=flow,
            post=post,
            body_mode=body_mode,
            client_version=client_version,
            os_type=os_type,
            waiting_ticket=resolved_waiting_ticket,
            url_mode=queue_subchain_url_mode,
            carry_crypto_forward=queue_carry_crypto_forward,
        )
        resolved_enter_ticket = queue_stage.get("enter_ticket") or resolved_enter_ticket
        resolved_waiting_ticket = queue_stage.get("waiting_ticket") or resolved_waiting_ticket

    generated_fields, raw_key, raw_iv = account_check_nexon_key_iv_fields(mode=account_check_key_mode)
    client.set_crypto(aes_key=raw_key, aes_iv=raw_iv)
    account_check_fields = build_account_check_nexon_fields(
        credentials,
        enter_ticket=resolved_enter_ticket,
        client_generated_key=generated_fields["ClientGeneratedKey"],
        client_generated_iv=generated_fields["ClientGeneratedIV"],
        mode=account_check_field_mode,
    )
    check_request = login.account_check_nexon(account_check_fields)
    check_record = save_built_request(out, "02_account_check_nexon", check_request)
    check_record["client_generated_key_mode"] = account_check_key_mode
    check_record["account_check_field_mode"] = account_check_field_mode
    check_record["client_generated_key_field"] = generated_fields["ClientGeneratedKey"]
    check_record["client_generated_iv_field"] = generated_fields["ClientGeneratedIV"]
    flow["steps"].append(check_record)

    check_response = post_built_request_to_url(
        client,
        check_request,
        url=_account_check_url(client, account_check_url_mode),
        body_mode=body_mode,
    )
    write_json(out / "02_account_check_nexon.response.json", check_response)
    flow["steps"][-1]["response_path"] = str((out / "02_account_check_nexon.response.json").resolve())
    if _is_error_response(check_response):
        flow["status"] = "account_check_nexon_error"
        flow["error_response_path"] = flow["steps"][-1]["response_path"]
        flow["error_response"] = check_response.get("parsed")
        write_json(out / "main_login_flow.json", flow)
        raise RuntimeError("Account_CheckNexon returned Error; see 02_account_check_nexon.response.json")
    account_check_state = _apply_account_check_state(client, check_response.get("parsed"))
    account_check_state_path = out / "02_account_check_nexon.state.json"
    write_json(account_check_state_path, account_check_state)
    flow["account_check_state_path"] = str(account_check_state_path.resolve())
    flow["account_check_state"] = _account_check_state_summary(account_check_state)
    flow["session_key_after_account_check"] = dict(client.session_key) if client.session_key else None

    if not account_check_state["o22_semantics"]["applied_to_client"]:
        flow["warning"] = "Account_CheckNexon did not expose EncryptedKey/EncryptedIV; later request headers stay empty"

    if not skip_proof_token and resolved_proof_token_stage == "after-account-check":
        run_proof_token_stage(
            client,
            login,
            output_dir=out,
            flow=flow,
            post=post,
            body_mode=body_mode,
            proof_token_url_mode=proof_token_url_mode,
            proof_token_max_attempts=proof_token_max_attempts,
            stage=resolved_proof_token_stage,
            name_prefix="02a",
        )

    if native_relay_queue:
        run_native_relay_queue(
            client,
            login,
            output_dir=out,
            flow=flow,
            post=post,
            body_mode=body_mode,
            skill_cut_in_option="All",
            battle_pass_id=native_relay_battle_pass_id,
            include_account_link_reward=native_relay_account_link_reward,
            continue_on_error=native_relay_continue_on_error,
        )

    auth_fields = build_account_auth_fields(
        country=country,
        locale=locale,
        device_id=device_id,
        os_type=os_type,
        os_version=os_version,
        device_model=device_model,
        market_id=market_id,
        user_type=user_type,
        access_ip=resolved_access_ip,
        advertisement_id=advertisement_id,
        idfv=idfv,
        game_option_language=game_option_language,
        device_system_memory_size=device_system_memory_size,
        imei=account_auth_imei,
        omit_imei=omit_account_auth_imei,
        version=account_auth_version,
        dev_id=account_auth_dev_id,
        omit_dev_id=omit_account_auth_dev_id,
    )
    auth_request = login.account_auth(auth_fields, include_base_defaults=True)
    auth_record = save_built_request(out, "03_account_auth", auth_request)
    auth_record["account_check_state_present"] = client.account_check_state is not None
    auth_record["account_id"] = client.account_id
    auth_record["server_time_ticks"] = client.server_time_ticks
    auth_record["url"] = client.session_api_url
    flow["steps"].append(auth_record)
    auth_response = post_built_request_to_url(
        client,
        auth_request,
        url=client.session_api_url,
        body_mode=body_mode,
    )
    write_json(out / "03_account_auth.response.json", auth_response)
    flow["steps"][-1]["response_path"] = str((out / "03_account_auth.response.json").resolve())
    if _is_error_response(auth_response):
        flow["status"] = "account_auth_error"
        flow["error_response_path"] = flow["steps"][-1]["response_path"]
        flow["error_response"] = auth_response.get("parsed")
        write_json(out / "main_login_flow.json", flow)
        raise RuntimeError("Account_Auth returned Error; see 03_account_auth.response.json")
    _update_session_key(client, auth_response.get("parsed"))

    sync_request = login.account_login_sync(build_account_login_sync_fields(), include_base_defaults=True)
    sync_record = save_built_request(out, "04_account_login_sync", sync_request)
    flow["steps"].append(sync_record)
    sync_response = post_built_request_to_url(
        client,
        sync_request,
        url=client.session_api_url,
        body_mode=body_mode,
    )
    write_json(out / "04_account_login_sync.response.json", sync_response)
    flow["steps"][-1]["response_path"] = str((out / "04_account_login_sync.response.json").resolve())
    if _is_error_response(sync_response):
        flow["status"] = "account_login_sync_error"
        flow["error_response_path"] = flow["steps"][-1]["response_path"]
        flow["error_response"] = sync_response.get("parsed")
        write_json(out / "main_login_flow.json", flow)
        raise RuntimeError("Account_LoginSync returned Error; see 04_account_login_sync.response.json")

    flow["status"] = "posted_login_sync"
    flow["player_data_path"] = str((out / "04_account_login_sync.response.json").resolve())
    flow["player_data"] = sync_response.get("parsed")
    write_json(out / "main_login_flow.json", flow)
    return flow


def run_native_relay_queue(
    client: BAReplayClient,
    login: LoginReplay,
    *,
    output_dir: Path,
    flow: dict[str, Any],
    post: bool,
    body_mode: str,
    skill_cut_in_option: str,
    battle_pass_id: int | None,
    include_account_link_reward: bool,
    continue_on_error: bool,
) -> dict[str, Any]:
    relay_state: dict[str, Any] = {
        "url": client.session_api_url,
        "account_check_state_present": client.account_check_state is not None,
        "account_id": client.account_id,
        "server_time_ticks": client.server_time_ticks,
        "tasks": [],
        "battle_pass_id": battle_pass_id,
        "include_account_link_reward": include_account_link_reward,
    }
    write_json(output_dir / "02b_native_relay_queue.json", relay_state)

    tasks: list[dict[str, Any]] = []
    for task in NATIVE_RELAY_QUEUE_CORE:
        task_copy = dict(task)
        if task_copy["name"] == "account_login_sync_no_part":
            task_copy["fields"] = build_account_login_sync_no_part_fields(skill_cut_in_option=skill_cut_in_option)
        else:
            task_copy["fields"] = dict(task_copy["fields"] or {})
        tasks.append(task_copy)

    if battle_pass_id is None:
        tasks.append(
            {
                "name": "battle_pass_get_info",
                "task_name": "BattlePassGetInfoNetworkTask",
                "protocol_name": "BattlePass_GetInfo",
                "request_class": "BattlePassGetInfoRequest",
                "slot": "0x18C6086E8",
                "fields": {},
                "skip_reason": "native task only posts when BattlePassTask.IsSeasonActive; pass --native-relay-battle-pass-id to force it",
            }
        )
    else:
        tasks.append(
            {
                "name": "battle_pass_get_info",
                "task_name": "BattlePassGetInfoNetworkTask",
                "protocol_name": "BattlePass_GetInfo",
                "request_class": "BattlePassGetInfoRequest",
                "slot": "0x18C6086E8",
                "fields": {"BattlePassId": int(battle_pass_id)},
            }
        )

    if include_account_link_reward:
        tasks.append(
            {
                "name": "account_link_reward",
                "task_name": "AccountLinkRewardNetworkTask",
                "protocol_name": "Account_LinkReward",
                "request_class": "AccountLinkRewardRequest",
                "slot": "0x18C608648",
                "fields": {},
                "condition": "PlatformService.HasAccountLink && AccountInfo flag at +0x78",
            }
        )

    for index, task in enumerate(tasks, start=1):
        step_name = f"02b_native_relay_{index:02d}_{task['name']}"
        if task.get("skip_reason"):
            skipped = {
                "name": step_name,
                "status": "skipped",
                "reason": task["skip_reason"],
                "task_name": task["task_name"],
                "protocol_name": task["protocol_name"],
                "request_class": task["request_class"],
                "slot": task["slot"],
            }
            relay_state["tasks"].append(skipped)
            flow["steps"].append(skipped)
            write_json(output_dir / "02b_native_relay_queue.json", relay_state)
            continue

        built = login.native_relay_request(task["request_class"], task["fields"])
        record = save_built_request(output_dir, step_name, built)
        record.update(
            {
                "task_name": task["task_name"],
                "protocol_name": task["protocol_name"],
                "request_class": task["request_class"],
                "slot": task["slot"],
                "url_mode": "session_api",
            }
        )
        if task["name"] == "account_login_sync_no_part":
            record["sync_protocols"] = list(task["fields"].get("SyncProtocols", []))
        if task.get("condition"):
            record["condition"] = task["condition"]
        flow["steps"].append(record)
        relay_state["tasks"].append(record)

        if not post:
            write_json(output_dir / "02b_native_relay_queue.json", relay_state)
            continue

        response_path = output_dir / f"{step_name}.response.json"
        response = post_built_request_to_url(
            client,
            built,
            url=client.session_api_url,
            body_mode=body_mode,
        )
        write_json(response_path, response)
        flow["steps"][-1]["response_path"] = str(response_path.resolve())
        relay_state["tasks"][-1]["response_path"] = str(response_path.resolve())
        if _is_error_response(response):
            flow["status"] = "native_relay_queue_error"
            flow["error_response_path"] = flow["steps"][-1]["response_path"]
            flow["error_response"] = response.get("parsed")
            write_json(output_dir / "02b_native_relay_queue.json", relay_state)
            write_json(output_dir / "main_login_flow.json", flow)
            if not continue_on_error:
                raise RuntimeError(f"{task['task_name']} returned Error; see {response_path.name}")
        _update_session_key(client, response.get("parsed"))
        write_json(output_dir / "02b_native_relay_queue.json", relay_state)

    flow["native_relay_queue_result"] = relay_state
    return relay_state


def run_queue_subchain(
    client: BAReplayClient,
    login: LoginReplay,
    *,
    output_dir: Path,
    flow: dict[str, Any],
    post: bool,
    body_mode: str,
    client_version: str,
    os_type: str,
    waiting_ticket: str,
    url_mode: str,
    carry_crypto_forward: bool,
) -> dict[str, str]:
    saved_aes_key = bytes(client.aes_key)
    saved_aes_iv = bytes(client.aes_iv)
    saved_aes_encrypted_key = bytes(client.aes_encrypted_key)
    saved_aes_encrypted_iv = bytes(client.aes_encrypted_iv)

    fields, queue_raw_key, queue_raw_iv = generated_key_iv_fields()
    queue_state = {
        "client_generated_key": fields["ClientGeneratedKey"],
        "client_generated_iv": fields["ClientGeneratedIV"],
        "waiting_ticket": waiting_ticket,
        "enter_ticket": "",
        "auth_ticket": "",
    }
    write_json(output_dir / "01a_queue_crypto_material.json", queue_state)

    try:
        crypto_request = login.queuing_get_crypto_keys(fields)
        crypto_record = save_built_request(output_dir, "01a_queuing_get_crypto_keys", crypto_request)
        crypto_record["url_mode"] = url_mode
        flow["steps"].append(crypto_record)
        crypto_response = post_built_request_to_url(
            client,
            crypto_request,
            url=_queue_subchain_url(client, url_mode),
            body_mode=body_mode,
            response_aes_key=queue_raw_key,
            response_aes_iv=queue_raw_iv,
        )
        write_json(output_dir / "01a_queuing_get_crypto_keys.response.json", crypto_response)
        flow["steps"][-1]["response_path"] = str((output_dir / "01a_queuing_get_crypto_keys.response.json").resolve())
        if _is_error_response(crypto_response):
            flow["status"] = "queue_get_crypto_keys_error"
            flow["error_response_path"] = flow["steps"][-1]["response_path"]
            flow["error_response"] = crypto_response.get("parsed") or crypto_response.get("payload")
            write_json(output_dir / "main_login_flow.json", flow)
            raise RuntimeError("Queuing_GetCryptoKeys returned Error; see 01a_queuing_get_crypto_keys.response.json")
        _apply_crypto_material_from_response(client, crypto_response.get("parsed"), aes_key=queue_raw_key, aes_iv=queue_raw_iv)

        auth_fields = build_queuing_get_auth_ticket_fields(
            client_generated_key=fields["ClientGeneratedKey"],
            client_generated_iv=fields["ClientGeneratedIV"],
            client_version=client_version,
            os_type=os_type,
        )
        auth_request = login.queuing_get_auth_ticket(auth_fields)
        auth_record = save_built_request(output_dir, "01b_queuing_get_auth_ticket", auth_request)
        auth_record["url_mode"] = url_mode
        flow["steps"].append(auth_record)
        auth_response = post_built_request_to_url(
            client,
            auth_request,
            url=_queue_subchain_url(client, url_mode),
            body_mode=body_mode,
            response_aes_key=queue_raw_key,
            response_aes_iv=queue_raw_iv,
        )
        write_json(output_dir / "01b_queuing_get_auth_ticket.response.json", auth_response)
        flow["steps"][-1]["response_path"] = str((output_dir / "01b_queuing_get_auth_ticket.response.json").resolve())
        if _is_error_response(auth_response):
            flow["status"] = "queue_get_auth_ticket_error"
            flow["error_response_path"] = flow["steps"][-1]["response_path"]
            flow["error_response"] = auth_response.get("parsed") or auth_response.get("payload")
            write_json(output_dir / "main_login_flow.json", flow)
            raise RuntimeError("Queuing_GetAuthTicket returned Error; see 01b_queuing_get_auth_ticket.response.json")
        _apply_crypto_material_from_response(client, auth_response.get("parsed"), aes_key=queue_raw_key, aes_iv=queue_raw_iv)

        auth_ticket = _as_str(_find_first(auth_response.get("parsed"), "AuthTicket", "authTicket"))
        if not auth_ticket:
            flow["status"] = "queue_missing_auth_ticket"
            flow["queue_auth_ticket_response"] = auth_response.get("parsed") or auth_response.get("payload")
            write_json(output_dir / "main_login_flow.json", flow)
            raise RuntimeError("Queuing_GetAuthTicket did not return AuthTicket; see 01b_queuing_get_auth_ticket.response.json")
        queue_state["auth_ticket"] = auth_ticket

        process_fields = build_queuing_process_waiting_queue_fields(
            auth_ticket=auth_ticket,
            waiting_ticket=waiting_ticket,
            client_version=client_version,
            os_type=os_type,
        )
        process_request = login.queuing_process_waiting_queue(process_fields)
        process_record = save_built_request(output_dir, "01c_queuing_process_waiting_queue", process_request)
        process_record["url_mode"] = url_mode
        flow["steps"].append(process_record)
        process_response = post_built_request_to_url(
            client,
            process_request,
            url=_queue_subchain_url(client, url_mode),
            body_mode=body_mode,
            response_aes_key=queue_raw_key,
            response_aes_iv=queue_raw_iv,
        )
        write_json(output_dir / "01c_queuing_process_waiting_queue.response.json", process_response)
        flow["steps"][-1]["response_path"] = str((output_dir / "01c_queuing_process_waiting_queue.response.json").resolve())
        if _is_error_response(process_response):
            flow["status"] = "queue_process_waiting_queue_error"
            flow["error_response_path"] = flow["steps"][-1]["response_path"]
            flow["error_response"] = process_response.get("parsed") or process_response.get("payload")
            write_json(output_dir / "main_login_flow.json", flow)
            raise RuntimeError(
                "Queuing_ProcessWaitingQueue returned Error; see 01c_queuing_process_waiting_queue.response.json"
            )

        queue_state["waiting_ticket"] = _as_str(
            _find_first(process_response.get("parsed"), "WaitingTicket", "waitingTicket")
        ) or waiting_ticket
        queue_state["enter_ticket"] = _as_str(
            _find_first(process_response.get("parsed"), "EnterTicket", "enterTicket")
        )
        write_json(output_dir / "01a_queue_crypto_material.json", queue_state)
        flow["queue_subchain_result"] = queue_state
        return queue_state
    finally:
        if not carry_crypto_forward:
            client.set_crypto(
                aes_key=saved_aes_key,
                aes_iv=saved_aes_iv,
                aes_encrypted_key=saved_aes_encrypted_key,
                aes_encrypted_iv=saved_aes_encrypted_iv,
            )


def run_proof_token_stage(
    client: BAReplayClient,
    login: LoginReplay,
    *,
    output_dir: Path,
    flow: dict[str, Any],
    post: bool,
    body_mode: str,
    proof_token_url_mode: str,
    proof_token_max_attempts: int | None,
    stage: str,
    name_prefix: str,
) -> None:
    question_name = f"{name_prefix}_proof_token_question"
    question_request = login.proof_token_question()
    question_record = save_built_request(output_dir, question_name, question_request)
    question_record["url_mode"] = proof_token_url_mode
    question_record["stage"] = stage
    question_record["session_key_present"] = bool(client.session_key)
    question_record["account_check_state_present"] = client.account_check_state is not None
    question_record["account_id"] = client.account_id
    question_record["server_time_ticks"] = client.server_time_ticks
    question_record["aes_encrypted_key_len"] = len(client.aes_encrypted_key)
    question_record["aes_encrypted_iv_len"] = len(client.aes_encrypted_iv)
    flow["steps"].append(question_record)

    if not post:
        return

    question_response_path = output_dir / f"{question_name}.response.json"
    question_response = post_built_request_to_url(
        client,
        question_request,
        url=_proof_token_url(client, proof_token_url_mode),
        body_mode=body_mode,
    )
    write_json(question_response_path, question_response)
    flow["steps"][-1]["response_path"] = str(question_response_path.resolve())
    if _is_error_response(question_response):
        flow["status"] = "proof_token_question_error"
        flow["error_response_path"] = flow["steps"][-1]["response_path"]
        flow["error_response"] = question_response.get("parsed")
        write_json(output_dir / "main_login_flow.json", flow)
        raise RuntimeError(f"ProofToken_RequestQuestion returned Error; see {question_response_path.name}")
    if _is_empty_success_response(question_response):
        flow["steps"][-1]["status"] = "empty_success_no_question"
        flow["proof_token_status"] = "empty_success_no_question"
        write_json(output_dir / "main_login_flow.json", flow)
        return

    parsed_question = question_response.get("parsed")
    question = _as_str(_find_first(parsed_question, "Question", "question"))
    hint = _as_int(_find_first(parsed_question, "Hint", "hint"))
    if not question or hint is None:
        flow["status"] = "proof_token_missing_question_or_hint"
        flow["proof_token_response"] = parsed_question
        write_json(output_dir / "main_login_flow.json", flow)
        raise RuntimeError(f"ProofToken_RequestQuestion did not return Question/Hint; see {question_response_path.name}")

    answer = solve_proof_token(question, hint, max_attempts=proof_token_max_attempts)
    solution_name = f"{name_prefix}_proof_token_solution"
    solver_record = {
        "question": question,
        "hint": hint,
        "search_span": proof_token_search_span(hint),
        "answer": answer,
        "stage": stage,
    }
    solution_path = output_dir / f"{solution_name}.json"
    write_json(solution_path, solver_record)
    flow["proof_token_solution_path"] = str(solution_path.resolve())

    submit_name = f"{name_prefix}_proof_token_submit"
    submit_request = login.proof_token_submit(answer)
    submit_record = save_built_request(output_dir, submit_name, submit_request)
    submit_record["url_mode"] = proof_token_url_mode
    submit_record["stage"] = stage
    submit_record["session_key_present"] = bool(client.session_key)
    submit_record["account_check_state_present"] = client.account_check_state is not None
    submit_record["account_id"] = client.account_id
    submit_record["server_time_ticks"] = client.server_time_ticks
    submit_record["aes_encrypted_key_len"] = len(client.aes_encrypted_key)
    submit_record["aes_encrypted_iv_len"] = len(client.aes_encrypted_iv)
    flow["steps"].append(submit_record)
    submit_response_path = output_dir / f"{submit_name}.response.json"
    submit_response = post_built_request_to_url(
        client,
        submit_request,
        url=_proof_token_url(client, proof_token_url_mode),
        body_mode=body_mode,
    )
    write_json(submit_response_path, submit_response)
    flow["steps"][-1]["response_path"] = str(submit_response_path.resolve())
    if _is_error_response(submit_response):
        flow["status"] = "proof_token_submit_error"
        flow["error_response_path"] = flow["steps"][-1]["response_path"]
        flow["error_response"] = submit_response.get("parsed")
        write_json(output_dir / "main_login_flow.json", flow)
        raise RuntimeError(f"ProofToken_Submit returned Error; see {submit_response_path.name}")


def post_built_request(client: BAReplayClient, built: BuiltRequest, *, body_mode: str) -> dict[str, Any]:
    raw = client.post_packet(built.packet, body_mode=body_mode)
    return decode_posted_response(client, raw, http_meta=client.last_exchange)


def post_built_request_to_url(
    client: BAReplayClient,
    built: BuiltRequest,
    *,
    url: str,
    body_mode: str,
    response_aes_key: bytes | None = None,
    response_aes_iv: bytes | None = None,
) -> dict[str, Any]:
    raw = client.post_packet(built.packet, url=url, body_mode=body_mode)
    return decode_posted_response(
        client,
        raw,
        aes_key=response_aes_key,
        aes_iv=response_aes_iv,
        http_meta=client.last_exchange,
    )


def _account_check_url(client: BAReplayClient, mode: str) -> str:
    normalized = mode.strip().lower()
    if normalized == "api":
        return client.api_url
    if normalized == "gateway":
        return client.gateway_url
    raise ValueError("account_check_url_mode must be 'api' or 'gateway'")


def _proof_token_url(client: BAReplayClient, mode: str) -> str:
    normalized = mode.strip().lower()
    if normalized == "api":
        return client.session_api_url
    if normalized == "gateway":
        return client.gateway_url
    raise ValueError("proof_token_url_mode must be 'api' or 'gateway'")


def _queue_subchain_url(client: BAReplayClient, mode: str) -> str:
    normalized = mode.strip().lower()
    if normalized == "gateway":
        return client.gateway_url
    if normalized == "api":
        return client.api_url
    raise ValueError("queue_subchain_url_mode must be 'api' or 'gateway'")


def _normalize_proof_token_stage(stage: str) -> str:
    normalized = (stage or "after-account-check").strip().lower().replace("_", "-")
    if normalized in ("before-queue", "after-account-check"):
        return normalized
    raise ValueError("proof_token_stage must be 'before-queue' or 'after-account-check'")


def decode_posted_response(
    client: BAReplayClient,
    raw: str,
    *,
    aes_key: bytes | None = None,
    aes_iv: bytes | None = None,
    http_meta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_key = client.aes_key if aes_key is None else aes_key
    resolved_iv = client.aes_iv if aes_iv is None else aes_iv
    try:
        decoded = decode_gateway_response(raw, aes_key=resolved_key, aes_iv=resolved_iv)
        parsed = _try_json(decoded.payload)
        return {
            "http": dict(http_meta) if http_meta else None,
            "raw": raw,
            "gateway": asdict(decoded),
            "payload": decoded.payload,
            "parsed": parsed,
        }
    except Exception as exc:
        return {
            "http": dict(http_meta) if http_meta else None,
            "raw": raw,
            "gateway": {"protocol": None, "packet": raw, "payload": raw, "raw": raw},
            "payload": raw,
            "parsed": _try_json(raw),
            "decode_error": {"type": type(exc).__name__, "message": str(exc)},
        }


def _is_error_response(response: Mapping[str, Any]) -> bool:
    gateway = response.get("gateway")
    parsed = response.get("parsed")
    if isinstance(gateway, Mapping) and str(gateway.get("protocol", "")).lower() == "error":
        return True
    return isinstance(parsed, Mapping) and int(parsed.get("Protocol", 0) or 0) == -1


def _is_empty_success_response(response: Mapping[str, Any]) -> bool:
    http = response.get("http")
    status_code = http.get("status_code") if isinstance(http, Mapping) else None
    return (
        status_code is not None
        and 200 <= int(status_code) < 300
        and response.get("raw", "") == ""
        and response.get("payload", "") == ""
        and response.get("parsed") is None
    )


def save_built_request(output_dir: Path, name: str, built: BuiltRequest) -> dict[str, Any]:
    packet_path = output_dir / f"{name}.bin"
    request_path = output_dir / f"{name}.request.json"
    packet_path.write_bytes(built.packet)
    serialized_request_bytes = built.serialized_request_bytes or built.request_bytes
    request_text = serialized_request_bytes.decode("utf-8", errors="replace")
    request_path.write_text(_pretty_json_text(request_text), encoding="utf-8")
    request_payload_path: Path | None = None
    if built.meta.request_payload_encrypted:
        request_payload_path = output_dir / f"{name}.request_payload.bin"
        request_payload_path.write_bytes(built.request_bytes)
    record = {
        "name": name,
        "protocol": built.protocol,
        "protocol_name": built.meta.protocol_name,
        "packet_len": len(built.packet),
        "packet_base64": base64.b64encode(built.packet).decode("ascii"),
        "packet_path": str(packet_path.resolve()),
        "request_path": str(request_path.resolve()),
        "request_json": _try_json(request_text),
        "meta": asdict(built.meta),
    }
    if request_payload_path is not None:
        record["request_payload_path"] = str(request_payload_path.resolve())
        record["request_payload_base64"] = base64.b64encode(built.request_bytes).decode("ascii")
    write_json(output_dir / f"{name}.built.json", record)
    return record


def write_json(path: str | Path, obj: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=_json_default), encoding="utf-8")


def toy_callback_to_dict(callback: NativeCallbackResult | None) -> dict[str, Any] | None:
    if callback is None:
        return None
    return asdict(callback)


def toy_ticket_to_dict(result: ToySdkTicketResult) -> dict[str, Any]:
    return {"ticket": result.ticket, "callback": toy_callback_to_dict(result.callback)}


def toy_login_to_dict(result: ToySdkLoginResult) -> dict[str, Any]:
    return {
        "npSN": result.np_sn,
        "npToken": result.np_token,
        "npaCode": result.npa_code,
        "sessionToken": result.session_token,
        "guid": result.guid,
        "memberId": result.member_id,
        "memberType": result.member_type,
        "umKey": result.um_key,
        "gameToken": result.game_token,
        "ngsmToken": result.ngsm_token,
        "callback": toy_callback_to_dict(result.callback),
    }


def _apply_account_check_state(client: BAReplayClient, parsed: Any) -> dict[str, Any]:
    """Apply the GameSessionManager.O22 state transition after 1014 succeeds."""

    _update_session_key(client, parsed)
    encrypted_key = _as_str(_find_first(parsed, "EncryptedKey", "encryptedKey"))
    encrypted_iv = _as_str(_find_first(parsed, "EncryptedIV", "encryptedIV"))
    signed_key = _as_str(_find_first(parsed, "SignedKey", "signedKey"))
    signed_iv = _as_str(_find_first(parsed, "SignedIV", "signedIV"))
    account_id = _as_int(_find_first(parsed, "AccountId", "accountId"))
    server_time_ticks = _as_int(_find_first(parsed, "ServerTimeTicks", "serverTimeTicks"))

    encrypted_key_bytes, encrypted_key_state = _base64_material_state(encrypted_key, include_hex=True)
    encrypted_iv_bytes, encrypted_iv_state = _base64_material_state(encrypted_iv, include_hex=True)
    signed_key_bytes, signed_key_state = _base64_material_state(signed_key)
    signed_iv_bytes, signed_iv_state = _base64_material_state(signed_iv)

    if encrypted_key_bytes and encrypted_iv_bytes:
        client.set_crypto(aes_encrypted_key=encrypted_key_bytes, aes_encrypted_iv=encrypted_iv_bytes)
    client.signed_key = signed_key_bytes
    client.signed_iv = signed_iv_bytes
    client.account_id = account_id
    client.server_time_ticks = server_time_ticks

    state: dict[str, Any] = {
        "account_id": account_id,
        "server_time_ticks": server_time_ticks,
        "session_key": dict(client.session_key) if client.session_key else None,
        "encrypted_key": encrypted_key_state,
        "encrypted_iv": encrypted_iv_state,
        "signed_key": signed_key_state,
        "signed_iv": signed_iv_state,
        "local_crypto_lane": {
            "aes_key_len": len(client.aes_key),
            "aes_iv_len": len(client.aes_iv),
        },
        "o22_semantics": {
            "applied_to_client": bool(encrypted_key_bytes and encrypted_iv_bytes),
            "game_session_manager_0x78_len": len(client.aes_encrypted_key),
            "game_session_manager_0x80_len": len(client.aes_encrypted_iv),
        },
    }
    client.account_check_state = state
    return state


def _account_check_state_summary(state: Mapping[str, Any]) -> dict[str, Any]:
    encrypted_key = state.get("encrypted_key") if isinstance(state.get("encrypted_key"), Mapping) else {}
    encrypted_iv = state.get("encrypted_iv") if isinstance(state.get("encrypted_iv"), Mapping) else {}
    signed_key = state.get("signed_key") if isinstance(state.get("signed_key"), Mapping) else {}
    signed_iv = state.get("signed_iv") if isinstance(state.get("signed_iv"), Mapping) else {}
    return {
        "account_id": state.get("account_id"),
        "server_time_ticks": state.get("server_time_ticks"),
        "session_key": state.get("session_key"),
        "encrypted_key_decoded_len": encrypted_key.get("decoded_len"),
        "encrypted_iv_decoded_len": encrypted_iv.get("decoded_len"),
        "signed_key_decoded_len": signed_key.get("decoded_len"),
        "signed_iv_decoded_len": signed_iv.get("decoded_len"),
        "local_crypto_lane": state.get("local_crypto_lane"),
        "o22_semantics": state.get("o22_semantics"),
    }


def _base64_material_state(value: str, *, include_hex: bool = False) -> tuple[bytes, dict[str, Any]]:
    state: dict[str, Any] = {
        "base64": value,
        "decoded_len": 0,
    }
    if not value:
        return b"", state
    try:
        decoded = base64.b64decode(value)
    except Exception as exc:
        state["decode_error"] = {"type": type(exc).__name__, "message": str(exc)}
        return b"", state
    state["decoded_len"] = len(decoded)
    if include_hex:
        state["decoded_hex"] = " ".join(f"{byte:02X}" for byte in decoded)
    return decoded, state


def _update_session_key(client: BAReplayClient, parsed: Any) -> None:
    session_key = _find_first(parsed, "SessionKey", "sessionKey")
    if isinstance(session_key, Mapping):
        client.session_key = dict(session_key)


def _apply_crypto_material_from_response(
    client: BAReplayClient,
    parsed: Any,
    *,
    aes_key: bytes,
    aes_iv: bytes,
) -> bool:
    encrypted_key = _as_str(_find_first(parsed, "EncryptedKey", "encryptedKey"))
    encrypted_iv = _as_str(_find_first(parsed, "EncryptedIV", "encryptedIV"))
    if not encrypted_key or not encrypted_iv:
        return False
    client.set_crypto(
        aes_key=aes_key,
        aes_iv=aes_iv,
        aes_encrypted_key=encrypted_key,
        aes_encrypted_iv=encrypted_iv,
        byte_encoding="auto",
    )
    return True


def _pretty_json_text(text: str) -> str:
    parsed = _try_json(text)
    if parsed is None:
        return text
    return json.dumps(parsed, ensure_ascii=False, indent=2)


def _try_json(text: str) -> Any:
    try:
        return json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return None


def _find_first(obj: Any, *names: str) -> Any:
    wanted = {name.lower() for name in names}
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            if str(key).lower() in wanted:
                return value
        for value in obj.values():
            found = _find_first(value, *names)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = _find_first(item, *names)
            if found is not None:
                return found
    return None


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _json_default(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray, memoryview)):
        return base64.b64encode(bytes(value)).decode("ascii")
    if isinstance(value, Path):
        return str(value)
    return str(value)

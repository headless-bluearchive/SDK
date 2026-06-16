
from __future__ import annotations

import base64
import json
import re
import socket
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Callable, Mapping
from urllib.request import Request, urlopen

from config.game import DEFAULTS
from core.client import BAReplayClient, BuiltRequest, decode_gateway_response
from core.crypto import account_check_nexon_key_iv_fields, decode_sqlcipher_material, generated_key_iv_fields
from core.error import AuthenticationError, ConfigurationError, GatewayError, ProofTokenError
from modules.auth.login import LoginReplay
from modules.auth.proof_token import proof_token_search_span, solve_proof_token
from modules.auth.toysdk_models import ToySdkCallbackResult, ToySdkLoginResult
from modules.runtime.ngsm_token import generate_ngsm_token

SESSION_LOGIN_SYNC_NO_PART_PROTOCOLS = [
    20000,
    1003,
    2000,
    3000,
    5000,
    12000,
    6000,
    22001,
    17018,
    21000,
    28001,
    33000,
    19000,
    10006,
    39006,
    44000,
    29005,
    30041,
    45000,
    46000,
    46001,
    47000,
    49000,
    27002,
    49004,
]

SESSION_BOOTSTRAP_QUEUE_CORE = [
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

    ngsm_present = bool(credentials.ngsm_token)
    required_run_args = {
        "guid": credentials.guid,
        "npaCode": credentials.npa_code,
    }
    return {
        "platform": "android",
        "serviceId": DEFAULTS.service_id,
        "security": "NgsX",
        "ngsmTokenPresent": ngsm_present,
        "pureHttpExecutedNgsX": False,
        "status": "ngsm-token-provided" if ngsm_present else "missing-ngsx-side-effect",
        "unitySetup": {
            "NPOptions.setNgsxEnabled": True,
            "Toy.SetServiceKeyForEditor": f"{DEFAULTS.service_id}.MjcwOA.{DEFAULTS.game_id}",
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
        "expectedImpact": "NgsmToken is treated as an input supplied by the headless client state.",
    }


def build_credentials(
    toy_login: ToySdkLoginResult,
    *,
    profile: Mapping[str, Any] | None = None,
) -> NexonGameCredentials:
    resolved_ngsm = getattr(toy_login, "ngsm_token", "")
    if not resolved_ngsm and profile is not None:
        resolved_ngsm = generate_ngsm_token(profile)
    missing = []
    if toy_login.np_sn is None:
        missing.append("npSN")
    if not toy_login.np_token:
        missing.append("npToken")
    if not toy_login.npa_code:
        missing.append("npaCode")
    if missing:
        present = {
            "npSN": toy_login.np_sn,
            "npaCode": bool(toy_login.npa_code),
            "npToken": bool(toy_login.np_token),
            "sessionToken": bool(toy_login.session_token),
            "NgsmToken": bool(resolved_ngsm),
        }
        raise AuthenticationError(
            "TOYSDK login result is not enough for Queuing_GetTicket; "
            f"missing {', '.join(missing)}; present={present}."
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
    raise ConfigurationError("account_check_field_mode must be 'android-minimal' or 'full'")


def build_account_auth_fields(
    *,
    country: str = DEFAULTS.country,
    locale: str = DEFAULTS.locale,
    device_id: str = "",
    os_type: str = "Android",
    os_version: str | None = None,
    device_model: str = DEFAULTS.android_model,
    market_id: str = DEFAULTS.market_id,
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
    return "A"


def normalize_account_auth_os_version(*, os_type: str, os_version: str | None) -> str:
    derived = android_account_auth_os_version(os_version or DEFAULTS.android_os_version)
    return derived or DEFAULTS.android_account_auth_os_version


def android_account_auth_os_version(value: str | None) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    match = re.search(r"(\d+)", text)
    if not match:
        return text
    major = int(match.group(1))
    api = {12: 32, 13: 33, 14: 34, 15: 35, 16: 36}.get(major)
    if api is None:
        return text
    return f"Android OS {major} / API-{api}"


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
    request = Request(DEFAULTS.ip_lookup_url, headers={"User-Agent": DEFAULTS.replay_user_agent})
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
        sync_protocols=SESSION_LOGIN_SYNC_NO_PART_PROTOCOLS,
    )


def run_main_game_login(
    client: BAReplayClient,
    credentials: NexonGameCredentials,
    *,
    body_mode: str = "multipart",
    client_version: str = "",
    access_ip: str = "",
    advertisement_id: str = "",
    idfv: str = "",
    country: str = DEFAULTS.country,
    locale: str = DEFAULTS.locale,
    device_id: str = "",
    os_type: str = "Android",
    os_version: str | None = None,
    device_model: str = DEFAULTS.android_model,
    device_system_memory_size: int | None = None,
    market_id: str = DEFAULTS.market_id,
    user_type: str = "",
    game_option_language: str = "",
    account_auth_version: int | None = None,
    account_auth_dev_id: str | None = None,
    omit_account_auth_dev_id: bool = False,
    account_auth_imei: int | None = 0,
    omit_account_auth_imei: bool = False,
    enter_ticket: str = "",
    account_check_key_mode: str = "rsa-oaep-sha1",
    account_check_url_mode: str = "wiki",
    account_check_field_mode: str = "android-minimal",
    queue_subchain: bool = False,
    queue_subchain_url_mode: str = "gateway",
    queue_carry_crypto_forward: bool = False,
    fetch_sqlcipher_material: bool = True,
    session_bootstrap_queue: bool = True,
    session_bootstrap_battle_pass_id: int | None = None,
    session_bootstrap_account_link_reward: bool = False,
    session_bootstrap_continue_on_error: bool = False,
    skip_proof_token: bool = False,
    proof_token_stage: str = "after-account-check",
    proof_token_url_mode: str = "wiki",
    proof_token_max_attempts: int | None = None,
    debug_logger: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    login = LoginReplay(client)
    flow: dict[str, Any] = {
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
        "fetch_sqlcipher_material": fetch_sqlcipher_material,
        "session_bootstrap_queue": session_bootstrap_queue,
        "session_bootstrap_battle_pass_id": session_bootstrap_battle_pass_id,
        "session_bootstrap_account_link_reward": session_bootstrap_account_link_reward,
        "session_bootstrap_continue_on_error": session_bootstrap_continue_on_error,
        "skip_proof_token": skip_proof_token,
        "proof_token_stage": proof_token_stage,
        "proof_token_url_mode": proof_token_url_mode,
        "proof_token_max_attempts": proof_token_max_attempts,
        "session_sequence_model": [
            "Queuing_GetTicket(gateway)",
            "Account_CheckNexon(wiki)",
            "Account_CheckNexon response SessionKey is injected into later RequestPacket hashes",
            "ProofToken_RequestQuestion/Submit(session_api) when enabled",
            "Session bootstrap queue(session_api): NetworkTimeSync, AcademyGetInfo, AccountLoginSyncNoPart, ItemList, ContentSaveGet, ShopBeforehandGachaGet, optional BattlePassGetInfo/AccountLinkReward",
            "Account_Auth(session_api)",
            "Account_LoginSync(session_api)",
        ],
        "steps": [],
    }
    android_security_state = build_android_security_state(credentials)
    flow["android_security_state"] = android_security_state
    _log(debug_logger, f"ngsx.state ngsmTokenPresent={android_security_state['ngsmTokenPresent']}")

    resolved_access_ip = access_ip or outbound_ipv4_address()
    flow["access_ip"] = resolved_access_ip
    _log(debug_logger, f"access_ip.ready value={resolved_access_ip}")

    resolved_proof_token_stage = _normalize_proof_token_stage(proof_token_stage)
    flow["proof_token_stage"] = resolved_proof_token_stage
    if not skip_proof_token and resolved_proof_token_stage == "before-queue":
        run_proof_token_stage(
            client,
            login,
            flow=flow,
            body_mode=body_mode,
            proof_token_url_mode=proof_token_url_mode,
            proof_token_max_attempts=proof_token_max_attempts,
            stage=resolved_proof_token_stage,
            name_prefix="00",
            debug_logger=debug_logger,
        )

    queue_fields = build_queuing_get_ticket_fields(
        credentials,
        client_version=client_version,
        access_ip=resolved_access_ip,
        os_type=os_type,
    )
    queue_request = login.queuing_get_ticket(queue_fields)
    queue_record = build_request_record("01_queuing_get_ticket", queue_request)
    flow["steps"].append(queue_record)
    _log(debug_logger, "gateway.post Queuing_GetTicket")

    queue_response = post_built_request_to_url(
        client,
        queue_request,
        url=client.gateway_url,
        body_mode=body_mode,
    )

    parsed_queue = queue_response.get("parsed")
    resolved_enter_ticket = enter_ticket or _as_str(_find_first(parsed_queue, "EnterTicket", "enterTicket"))
    resolved_waiting_ticket = _as_str(_find_first(parsed_queue, "WaitingTicket", "waitingTicket"))
    if not resolved_enter_ticket:
        flow["status"] = "missing_enter_ticket"
        flow["queue_response"] = parsed_queue
        raise GatewayError("Queuing_GetTicket did not return EnterTicket")
    _log(debug_logger, f"gateway.ok Queuing_GetTicket enterTicket={bool(resolved_enter_ticket)} waitingTicket={bool(resolved_waiting_ticket)}")

    if queue_subchain:
        queue_stage = run_queue_subchain(
            client,
            login,
            flow=flow,
            body_mode=body_mode,
            client_version=client_version,
            os_type=os_type,
            waiting_ticket=resolved_waiting_ticket,
            url_mode=queue_subchain_url_mode,
            carry_crypto_forward=queue_carry_crypto_forward,
            debug_logger=debug_logger,
        )
        resolved_enter_ticket = queue_stage.get("enter_ticket") or resolved_enter_ticket
        resolved_waiting_ticket = queue_stage.get("waiting_ticket") or resolved_waiting_ticket
    elif fetch_sqlcipher_material:
        fetch_sqlcipher_material_from_queue(
            client,
            login,
            flow=flow,
            body_mode=body_mode,
            client_version=client_version,
            os_type=os_type,
            url_mode=queue_subchain_url_mode,
            debug_logger=debug_logger,
        )

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
    check_record = build_request_record("02_account_check_nexon", check_request)
    check_record["client_generated_key_mode"] = account_check_key_mode
    check_record["account_check_field_mode"] = account_check_field_mode
    check_record["client_generated_key_field"] = generated_fields["ClientGeneratedKey"]
    check_record["client_generated_iv_field"] = generated_fields["ClientGeneratedIV"]
    flow["steps"].append(check_record)
    _log(debug_logger, "gateway.post Account_CheckNexon")

    check_response = post_built_request_to_url(
        client,
        check_request,
        url=_account_check_url(client, account_check_url_mode),
        body_mode=body_mode,
    )
    if _is_error_response(check_response):
        flow["status"] = "account_check_nexon_error"
        flow["error_response"] = check_response.get("parsed")
        raise GatewayError("Account_CheckNexon returned Error")
    account_check_state = _apply_account_check_state(client, check_response.get("parsed"))
    flow["account_check_state"] = _account_check_state_summary(account_check_state)
    _log(debug_logger, f"gateway.ok Account_CheckNexon accountId={client.account_id} sessionKey={bool(client.session_key)}")

    if not account_check_state["o22_semantics"]["applied_to_client"]:
        flow["warning"] = "Account_CheckNexon did not expose EncryptedKey/EncryptedIV; later request headers stay empty"

    if not skip_proof_token and resolved_proof_token_stage == "after-account-check":
        run_proof_token_stage(
            client,
            login,
            flow=flow,
            body_mode=body_mode,
            proof_token_url_mode=proof_token_url_mode,
            proof_token_max_attempts=proof_token_max_attempts,
            stage=resolved_proof_token_stage,
            name_prefix="02a",
            debug_logger=debug_logger,
        )

    if session_bootstrap_queue:
        run_session_bootstrap_queue(
            client,
            login,
            flow=flow,
            body_mode=body_mode,
            skill_cut_in_option="All",
            battle_pass_id=session_bootstrap_battle_pass_id,
            include_account_link_reward=session_bootstrap_account_link_reward,
            continue_on_error=session_bootstrap_continue_on_error,
            debug_logger=debug_logger,
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
    auth_record = build_request_record("03_account_auth", auth_request)
    auth_record["account_check_state_present"] = client.account_check_state is not None
    auth_record["account_id"] = client.account_id
    auth_record["server_time_ticks"] = client.server_time_ticks
    auth_record["url"] = client.session_api_url
    flow["steps"].append(auth_record)
    _log(debug_logger, "gateway.post Account_Auth")
    auth_response = post_built_request_to_url(
        client,
        auth_request,
        url=client.session_api_url,
        body_mode=body_mode,
    )
    if _is_error_response(auth_response):
        flow["status"] = "account_auth_error"
        flow["error_response"] = auth_response.get("parsed")
        raise GatewayError("Account_Auth returned Error")
    _update_session_key(client, auth_response.get("parsed"))
    flow["account_data"] = auth_response.get("parsed")
    _log(debug_logger, "gateway.ok Account_Auth")

    sync_request = login.account_login_sync(build_account_login_sync_fields(), include_base_defaults=True)
    sync_record = build_request_record("04_account_login_sync", sync_request)
    flow["steps"].append(sync_record)
    _log(debug_logger, "gateway.post Account_LoginSync")
    sync_response = post_built_request_to_url(
        client,
        sync_request,
        url=client.session_api_url,
        body_mode=body_mode,
    )
    if _is_error_response(sync_response):
        flow["status"] = "account_login_sync_error"
        flow["error_response"] = sync_response.get("parsed")
        raise GatewayError("Account_LoginSync returned Error")

    flow["status"] = "posted_login_sync"
    flow["player_data"] = sync_response.get("parsed")
    _log(debug_logger, "gateway.ok Account_LoginSync")
    return flow


def run_session_bootstrap_queue(
    client: BAReplayClient,
    login: LoginReplay,
    *,
    flow: dict[str, Any],
    body_mode: str,
    skill_cut_in_option: str,
    battle_pass_id: int | None,
    include_account_link_reward: bool,
    continue_on_error: bool,
    debug_logger: Callable[[str], None] | None = None,
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

    tasks: list[dict[str, Any]] = []
    for task in SESSION_BOOTSTRAP_QUEUE_CORE:
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
                "skip_reason": "BattlePass_GetInfo is only posted when BattlePassTask.IsSeasonActive; provide a battle_pass_id to force it",
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
        step_name = f"02b_session_bootstrap_{index:02d}_{task['name']}"
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
            continue

        built = login.session_api_request(task["request_class"], task["fields"])
        record = build_request_record(step_name, built)
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
        _log(debug_logger, f"gateway.post {task['protocol_name']}")

        response = post_built_request_to_url(
            client,
            built,
            url=client.session_api_url,
            body_mode=body_mode,
        )
        if _is_error_response(response):
            flow["status"] = "session_bootstrap_queue_error"
            flow["error_response"] = response.get("parsed")
            if not continue_on_error:
                raise GatewayError(f"{task['task_name']} returned Error")
        _update_session_key(client, response.get("parsed"))
        _log(debug_logger, f"gateway.ok {task['protocol_name']}")

    flow["session_bootstrap_queue_result"] = relay_state
    return relay_state


def run_queue_subchain(
    client: BAReplayClient,
    login: LoginReplay,
    *,
    flow: dict[str, Any],
    body_mode: str,
    client_version: str,
    os_type: str,
    waiting_ticket: str,
    url_mode: str,
    carry_crypto_forward: bool,
    debug_logger: Callable[[str], None] | None = None,
) -> dict[str, Any]:
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

    try:
        crypto_request = login.queuing_get_crypto_keys(fields)
        crypto_record = build_request_record("01a_queuing_get_crypto_keys", crypto_request)
        crypto_record["url_mode"] = url_mode
        flow["steps"].append(crypto_record)
        _log(debug_logger, "gateway.post Queuing_GetCryptoKeys")
        crypto_response = post_built_request_to_url(
            client,
            crypto_request,
            url=_queue_subchain_url(client, url_mode),
            body_mode=body_mode,
            response_aes_key=queue_raw_key,
            response_aes_iv=queue_raw_iv,
        )
        if _is_error_response(crypto_response):
            flow["status"] = "queue_get_crypto_keys_error"
            flow["error_response"] = crypto_response.get("parsed") or crypto_response.get("payload")
            raise GatewayError("Queuing_GetCryptoKeys returned Error")
        crypto_state = _apply_crypto_material_from_response(
            client,
            crypto_response.get("parsed"),
            aes_key=queue_raw_key,
            aes_iv=queue_raw_iv,
        )
        if crypto_state.get("sqlcipher"):
            queue_state["sqlcipher"] = crypto_state["sqlcipher"]
        _log(debug_logger, "gateway.ok Queuing_GetCryptoKeys")

        auth_fields = build_queuing_get_auth_ticket_fields(
            client_generated_key=fields["ClientGeneratedKey"],
            client_generated_iv=fields["ClientGeneratedIV"],
            client_version=client_version,
            os_type=os_type,
        )
        auth_request = login.queuing_get_auth_ticket(auth_fields)
        auth_record = build_request_record("01b_queuing_get_auth_ticket", auth_request)
        auth_record["url_mode"] = url_mode
        flow["steps"].append(auth_record)
        _log(debug_logger, "gateway.post Queuing_GetAuthTicket")
        auth_response = post_built_request_to_url(
            client,
            auth_request,
            url=_queue_subchain_url(client, url_mode),
            body_mode=body_mode,
            response_aes_key=queue_raw_key,
            response_aes_iv=queue_raw_iv,
        )
        if _is_error_response(auth_response):
            flow["status"] = "queue_get_auth_ticket_error"
            flow["error_response"] = auth_response.get("parsed") or auth_response.get("payload")
            raise GatewayError("Queuing_GetAuthTicket returned Error")
        auth_crypto_state = _apply_crypto_material_from_response(
            client,
            auth_response.get("parsed"),
            aes_key=queue_raw_key,
            aes_iv=queue_raw_iv,
        )
        if auth_crypto_state.get("sqlcipher"):
            queue_state["sqlcipher"] = auth_crypto_state["sqlcipher"]
        _log(debug_logger, "gateway.ok Queuing_GetAuthTicket")

        auth_ticket = _as_str(_find_first(auth_response.get("parsed"), "AuthTicket", "authTicket"))
        if not auth_ticket:
            flow["status"] = "queue_missing_auth_ticket"
            flow["queue_auth_ticket_response"] = auth_response.get("parsed") or auth_response.get("payload")
            raise GatewayError("Queuing_GetAuthTicket did not return AuthTicket")
        queue_state["auth_ticket"] = auth_ticket

        process_fields = build_queuing_process_waiting_queue_fields(
            auth_ticket=auth_ticket,
            waiting_ticket=waiting_ticket,
            client_version=client_version,
            os_type=os_type,
        )
        process_request = login.queuing_process_waiting_queue(process_fields)
        process_record = build_request_record("01c_queuing_process_waiting_queue", process_request)
        process_record["url_mode"] = url_mode
        flow["steps"].append(process_record)
        _log(debug_logger, "gateway.post Queuing_ProcessWaitingQueue")
        process_response = post_built_request_to_url(
            client,
            process_request,
            url=_queue_subchain_url(client, url_mode),
            body_mode=body_mode,
            response_aes_key=queue_raw_key,
            response_aes_iv=queue_raw_iv,
        )
        if _is_error_response(process_response):
            flow["status"] = "queue_process_waiting_queue_error"
            flow["error_response"] = process_response.get("parsed") or process_response.get("payload")
            raise GatewayError("Queuing_ProcessWaitingQueue returned Error")
        _log(debug_logger, "gateway.ok Queuing_ProcessWaitingQueue")

        queue_state["waiting_ticket"] = _as_str(
            _find_first(process_response.get("parsed"), "WaitingTicket", "waitingTicket")
        ) or waiting_ticket
        queue_state["enter_ticket"] = _as_str(
            _find_first(process_response.get("parsed"), "EnterTicket", "enterTicket")
        )
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


def fetch_sqlcipher_material_from_queue(
    client: BAReplayClient,
    login: LoginReplay,
    *,
    flow: dict[str, Any],
    body_mode: str,
    client_version: str,
    os_type: str,
    url_mode: str,
    debug_logger: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    fields, raw_key, raw_iv = generated_key_iv_fields()
    state: dict[str, Any] = {"available": False, "source": "", "responses": []}

    def request_crypto(name: str, built: BuiltRequest) -> dict[str, Any]:
        record = build_request_record(name, built)
        record["url_mode"] = url_mode
        flow["steps"].append(record)
        _log(debug_logger, f"gateway.post {record['protocol_name']}")
        response = post_built_request_to_url(
            client,
            built,
            url=_queue_subchain_url(client, url_mode),
            body_mode=body_mode,
            response_aes_key=raw_key,
            response_aes_iv=raw_iv,
        )
        parsed = response.get("parsed")
        crypto_state = _apply_crypto_material_from_response(
            client,
            parsed,
            aes_key=raw_key,
            aes_iv=raw_iv,
        )
        response_state = {
            "name": name,
            "protocol": record.get("protocol_name"),
            "parsed": parsed is not None,
            "http_status": (response.get("http") or {}).get("status_code")
            if isinstance(response.get("http"), Mapping)
            else None,
            "raw_len": len(response.get("raw") or ""),
            "payload_len": len(response.get("payload") or ""),
            "decode_error": response.get("decode_error"),
            "sqlcipher": crypto_state.get("sqlcipher"),
        }
        state["responses"].append(response_state)
        if crypto_state.get("sqlcipher"):
            state["available"] = True
            state["source"] = record.get("protocol_name") or name
            state["sqlcipher"] = crypto_state["sqlcipher"]
        _log(debug_logger, f"gateway.ok {record['protocol_name']} sqlcipher={bool(crypto_state.get('sqlcipher'))}")
        return response

    try:
        request_crypto("01a_queuing_get_crypto_keys", login.queuing_get_crypto_keys(fields))
        if not state["available"]:
            auth_fields = build_queuing_get_auth_ticket_fields(
                client_generated_key=fields["ClientGeneratedKey"],
                client_generated_iv=fields["ClientGeneratedIV"],
                client_version=client_version,
                os_type=os_type,
            )
            request_crypto("01b_queuing_get_auth_ticket_crypto", login.queuing_get_auth_ticket(auth_fields))
    except Exception as exc:
        state["error"] = {"type": type(exc).__name__, "message": str(exc)}
        _log(debug_logger, f"gateway.sqlcipher_material error={type(exc).__name__}")

    flow["sqlcipher_material"] = state
    return state


def run_proof_token_stage(
    client: BAReplayClient,
    login: LoginReplay,
    *,
    flow: dict[str, Any],
    body_mode: str,
    proof_token_url_mode: str,
    proof_token_max_attempts: int | None,
    stage: str,
    name_prefix: str,
    debug_logger: Callable[[str], None] | None = None,
) -> None:
    question_name = f"{name_prefix}_proof_token_question"
    question_request = login.proof_token_question()
    question_record = build_request_record(question_name, question_request)
    question_record["url_mode"] = proof_token_url_mode
    question_record["stage"] = stage
    question_record["session_key_present"] = bool(client.session_key)
    question_record["account_check_state_present"] = client.account_check_state is not None
    question_record["account_id"] = client.account_id
    question_record["server_time_ticks"] = client.server_time_ticks
    question_record["aes_encrypted_key_len"] = len(client.aes_encrypted_key)
    question_record["aes_encrypted_iv_len"] = len(client.aes_encrypted_iv)
    flow["steps"].append(question_record)
    _log(debug_logger, f"gateway.post ProofToken_RequestQuestion stage={stage}")

    question_response = post_built_request_to_url(
        client,
        question_request,
        url=_proof_token_url(client, proof_token_url_mode),
        body_mode=body_mode,
    )
    if _is_error_response(question_response):
        flow["status"] = "proof_token_question_error"
        flow["error_response"] = question_response.get("parsed")
        raise ProofTokenError("ProofToken_RequestQuestion returned Error")
    if _is_empty_success_response(question_response):
        flow["steps"][-1]["status"] = "empty_success_no_question"
        flow["proof_token_status"] = "empty_success_no_question"
        _log(debug_logger, f"gateway.ok ProofToken_RequestQuestion stage={stage} empty=True")
        return

    parsed_question = question_response.get("parsed")
    question = _as_str(_find_first(parsed_question, "Question", "question"))
    hint = _as_int(_find_first(parsed_question, "Hint", "hint"))
    if not question or hint is None:
        flow["status"] = "proof_token_missing_question_or_hint"
        flow["proof_token_response"] = parsed_question
        raise ProofTokenError("ProofToken_RequestQuestion did not return Question/Hint")

    answer = solve_proof_token(question, hint, max_attempts=proof_token_max_attempts)
    _log(debug_logger, f"proof_token.solved stage={stage}")
    solution_name = f"{name_prefix}_proof_token_solution"
    solver_record = {
        "question": question,
        "hint": hint,
        "search_span": proof_token_search_span(hint),
        "answer": answer,
        "stage": stage,
    }
    flow["proof_token_solution"] = solver_record

    submit_name = f"{name_prefix}_proof_token_submit"
    submit_request = login.proof_token_submit(answer)
    submit_record = build_request_record(submit_name, submit_request)
    submit_record["url_mode"] = proof_token_url_mode
    submit_record["stage"] = stage
    submit_record["session_key_present"] = bool(client.session_key)
    submit_record["account_check_state_present"] = client.account_check_state is not None
    submit_record["account_id"] = client.account_id
    submit_record["server_time_ticks"] = client.server_time_ticks
    submit_record["aes_encrypted_key_len"] = len(client.aes_encrypted_key)
    submit_record["aes_encrypted_iv_len"] = len(client.aes_encrypted_iv)
    flow["steps"].append(submit_record)
    _log(debug_logger, f"gateway.post ProofToken_Submit stage={stage}")
    submit_response = post_built_request_to_url(
        client,
        submit_request,
        url=_proof_token_url(client, proof_token_url_mode),
        body_mode=body_mode,
    )
    if _is_error_response(submit_response):
        flow["status"] = "proof_token_submit_error"
        flow["error_response"] = submit_response.get("parsed")
        raise ProofTokenError("ProofToken_Submit returned Error")
    _log(debug_logger, f"gateway.ok ProofToken_Submit stage={stage}")


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
    if normalized == "wiki":
        return client.api_url
    if normalized == "gateway":
        return client.gateway_url
    raise ConfigurationError("account_check_url_mode must be 'wiki' or 'gateway'")


def _proof_token_url(client: BAReplayClient, mode: str) -> str:
    normalized = mode.strip().lower()
    if normalized == "wiki":
        return client.session_api_url
    if normalized == "gateway":
        return client.gateway_url
    raise ConfigurationError("proof_token_url_mode must be 'wiki' or 'gateway'")


def _queue_subchain_url(client: BAReplayClient, mode: str) -> str:
    normalized = mode.strip().lower()
    if normalized == "gateway":
        return client.gateway_url
    if normalized == "wiki":
        return client.api_url
    raise ConfigurationError("queue_subchain_url_mode must be 'wiki' or 'gateway'")


def _normalize_proof_token_stage(stage: str) -> str:
    normalized = (stage or "after-account-check").strip().lower().replace("_", "-")
    if normalized in ("before-queue", "after-account-check"):
        return normalized
    raise ConfigurationError("proof_token_stage must be 'before-queue' or 'after-account-check'")


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


def build_request_record(name: str, built: BuiltRequest) -> dict[str, Any]:
    record = {
        "name": name,
        "protocol": built.protocol,
        "protocol_name": built.meta.protocol_name,
        "packet_len": len(built.packet),
        "meta": asdict(built.meta),
    }
    return record


def toy_callback_to_dict(callback: ToySdkCallbackResult | None) -> dict[str, Any] | None:
    if callback is None:
        return None
    return asdict(callback)


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
        "ngsmToken": result.ngsm_token,
        "callback": toy_callback_to_dict(result.callback),
    }


def _apply_account_check_state(client: BAReplayClient, parsed: Any) -> dict[str, Any]:

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


def _account_check_state_summary(state: Mapping[str, Any], *, include_session_key: bool = False) -> dict[str, Any]:
    encrypted_key = state.get("encrypted_key") if isinstance(state.get("encrypted_key"), Mapping) else {}
    encrypted_iv = state.get("encrypted_iv") if isinstance(state.get("encrypted_iv"), Mapping) else {}
    signed_key = state.get("signed_key") if isinstance(state.get("signed_key"), Mapping) else {}
    signed_iv = state.get("signed_iv") if isinstance(state.get("signed_iv"), Mapping) else {}
    summary = {
        "account_id": state.get("account_id"),
        "server_time_ticks": state.get("server_time_ticks"),
        "encrypted_key_decoded_len": encrypted_key.get("decoded_len"),
        "encrypted_iv_decoded_len": encrypted_iv.get("decoded_len"),
        "signed_key_decoded_len": signed_key.get("decoded_len"),
        "signed_iv_decoded_len": signed_iv.get("decoded_len"),
        "local_crypto_lane": state.get("local_crypto_lane"),
        "o22_semantics": state.get("o22_semantics"),
    }
    if include_session_key:
        summary["session_key"] = state.get("session_key")
    return summary


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
) -> dict[str, Any]:
    state: dict[str, Any] = {"gateway": False, "sqlcipher": None}
    encrypted_key = _as_str(_find_first(parsed, "EncryptedKey", "encryptedKey"))
    encrypted_iv = _as_str(_find_first(parsed, "EncryptedIV", "encryptedIV"))
    if encrypted_key and encrypted_iv:
        client.set_crypto(
            aes_key=aes_key,
            aes_iv=aes_iv,
            aes_encrypted_key=encrypted_key,
            aes_encrypted_iv=encrypted_iv,
            byte_encoding="auto",
        )
        state["gateway"] = True

    encrypted_sql_key = _as_str(_find_first(parsed, "EncryptedSqlCipherKey", "encryptedSqlCipherKey"))
    encrypted_sql_license = _as_str(_find_first(parsed, "EncryptedSqlCipherLicense", "encryptedSqlCipherLicense"))
    if encrypted_sql_key and encrypted_sql_license:
        sqlcipher_key, sqlcipher_license = decode_sqlcipher_material(
            encrypted_sql_key,
            encrypted_sql_license,
            aes_key=aes_key,
            aes_iv=aes_iv,
        )
        client.set_sqlcipher(sqlcipher_key=sqlcipher_key, sqlcipher_license=sqlcipher_license, byte_encoding="base64")
        state["sqlcipher"] = {
            "available": True,
            "key_length": len(sqlcipher_key),
            "license_length": len(sqlcipher_license),
        }
    return state


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


def _log(logger: Callable[[str], None] | None, message: str) -> None:
    if logger is not None:
        logger(message)

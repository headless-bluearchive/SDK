"""One-shot Nexon web-token -> TOYSDK -> main-game login flow."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Mapping

from modules.runtime.android_runtime_profile import (
    AndroidRuntimeProfile,
    find_latest_android_runtime_pull,
    load_android_runtime_profile,
    select_android_runtime_device_id,
)
from core.client import BAReplayClient
from modules.auth.nexon_login import (
    DEFAULT_OUTPUT_DIR,
    NexonGameCredentials,
    build_credentials,
    run_main_game_login,
    save_toy_results,
    toy_login_to_dict,
)
from modules.auth.nexon_web import DEFAULT_LATEST_TOKENS, WebLoginTokens, load_latest_tokens, run_playwright_web_login
from utils.proxy import apply_proxy_env, normalize_proxy_url
from modules.runtime.region_config import profile_for
from modules.runtime.runtime_config import RuntimeConnectionInfo, discover_client_version, discover_connection_info
from modules.auth.toysdk_android import AndroidDeviceProfile, AndroidToyConfig, AndroidToySdkClient, android_session_to_dict
from modules.auth.toysdk_models import ToySdkLoginResult


@dataclass(frozen=True)
class ToyLoginOverrides:
    np_sn: int | None = None
    np_token: str = ""
    npa_code: str = ""
    session_token: str = ""
    guid: str = ""
    member_id: str = ""
    member_type: str = ""
    game_token: str = ""
    ngsm_token: str = ""
    game_token_as_np_token: bool = False

    def has_values(self) -> bool:
        return any(
            (
                self.np_sn is not None,
                bool(self.np_token),
                bool(self.npa_code),
                bool(self.session_token),
                bool(self.guid),
                bool(self.member_id),
                bool(self.member_type),
                bool(self.game_token),
                bool(self.ngsm_token),
                bool(self.game_token_as_np_token),
            )
        )


@dataclass(frozen=True)
class IntegratedLoginOptions:
    web_token: str = ""
    web_login: bool = False
    latest_token_path: Path = DEFAULT_LATEST_TOKENS
    country: str = "TW"
    locale: str = "zh-TW"
    region: str = ""
    env: str = "live"
    gid: str = "2079"
    host_url: str = ""
    api_url: str = ""
    auto_host: bool = True
    local_config_dir: Path | None = None
    android_runtime_dir: Path | None = None
    no_android_runtime_profile: bool = False
    android_runtime_profile: AndroidRuntimeProfile | None = None
    bundle_version: str = ""
    client_version: str = ""
    access_ip: str = ""
    ngsm_token: str = ""
    allow_session_token_as_ngsm: bool = False
    allow_empty_ngsm_token: bool = False
    no_native_login: bool = False
    pc_native_login: bool = False
    toy_login_json: Path | None = None
    toy_overrides: ToyLoginOverrides = field(default_factory=ToyLoginOverrides)
    launch_platform_type: int = 3
    store_type: str = "google"
    package_name: str = ""
    security_token: str = ""
    native_agree_mode: str = "ticket"
    native_sign_in_with_ticket: bool = False
    native_sign_in_with_web_token: bool = False
    mobile_ticket: str = ""
    mobile_skip_enter_toy: bool = False
    mobile_create_np_token: bool = False
    mobile_skip_create_np_token: bool = False
    mobile_skip_user_info: bool = False
    android_device_id_source: str = "auto"
    android_uuid: str = ""
    android_uuid2: str = ""
    android_adid: str = ""
    android_model: str = "Pixel 7"
    android_os_version: str = "Android 13"
    android_app_version_code: int = 429659
    android_client_id: str = "2708"
    android_game_id: str = "toy2079"
    proxy: str = ""
    web_proxy: str = ""
    gateway_proxy: str = ""
    native_proxy_env: bool = False
    post: bool = False
    body_mode: str = "besthttp-multipart"
    account_check_key_mode: str = "rsa-oaep-sha1"
    account_check_url_mode: str = "api"
    account_check_field_mode: str = "android-minimal"
    queue_subchain: bool = False
    queue_subchain_url_mode: str = "gateway"
    queue_carry_crypto_forward: bool = False
    native_relay_queue: bool = True
    native_relay_battle_pass_id: int | None = None
    native_relay_account_link_reward: bool = False
    native_relay_continue_on_error: bool = False
    skip_proof_token: bool = False
    proof_token_stage: str = "after-account-check"
    proof_token_url_mode: str = "api"
    proof_token_max_attempts: int | None = None
    output_dir: Path = DEFAULT_OUTPUT_DIR
    device_id: str = ""
    device_system_memory_size: int | None = 8192
    game_option_language: str = ""
    account_auth_country: str = ""
    account_auth_locale: str = ""
    account_auth_advertisement_id: str = ""
    account_auth_idfv: str = ""
    account_auth_version: int | None = None
    account_auth_dev_id: str | None = None
    omit_account_auth_dev_id: bool = False
    account_auth_imei: int | None = 0
    omit_account_auth_imei: bool = False
    market_id: str = "GooglePlay"
    user_type: str = ""
    timeout: float = 60.0


@dataclass(frozen=True)
class IntegratedLoginResult:
    web_tokens: WebLoginTokens
    toy_login: ToySdkLoginResult
    credentials: NexonGameCredentials
    connection: RuntimeConnectionInfo | None
    android_runtime_profile: AndroidRuntimeProfile | None
    flow: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "web_tokens": self.web_tokens.raw or {
                "web_token": self.web_tokens.web_token,
                "hsid": self.web_tokens.hsid,
                "npp": self.web_tokens.npp,
                "query": self.web_tokens.query,
                "callback_url": self.web_tokens.callback_url,
                "source_path": self.web_tokens.source_path,
            },
            "toy_login": toy_login_to_dict(self.toy_login),
            "credentials": asdict(self.credentials),
            "connection": self.connection.to_dict() if self.connection else None,
            "android_runtime_profile": self.android_runtime_profile.to_dict() if self.android_runtime_profile else None,
            "flow": self.flow,
        }


def run_web_to_game_login(options: IntegratedLoginOptions) -> IntegratedLoginResult:
    """Run the full login chain with separable library stages."""

    out = Path(options.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    android_runtime_profile = resolve_android_runtime_profile(options, out)
    options = apply_android_runtime_profile_defaults(options, android_runtime_profile)
    options = apply_region_defaults(options)
    native_env_proxy = options.proxy or options.web_proxy or options.gateway_proxy
    if native_env_proxy and options.native_proxy_env:
        apply_proxy_env(native_env_proxy)

    web_tokens = resolve_web_tokens(options)
    write_json(out / "selected_web_token.json", web_tokens.raw or {"web_token": web_tokens.web_token})

    toy_login = resolve_toy_login(options, web_tokens.web_token, out)
    toy_login = apply_toy_overrides(toy_login, options.toy_overrides)
    write_json(out / "toy_login_summary.json", toy_login_to_dict(toy_login))

    credentials = build_credentials(
        toy_login,
        ngsm_token=options.ngsm_token,
        allow_session_token_as_ngsm=options.allow_session_token_as_ngsm,
        allow_empty_ngsm_token=options.allow_empty_ngsm_token,
    )
    host_url, api_url, connection = resolve_host_url(options)
    if connection is not None:
        write_json(out / "connection_info.json", connection.to_dict())

    client_version = (
        options.client_version
        or (options.android_runtime_profile.client_version if options.android_runtime_profile else "")
        or discover_client_version()
    )
    if not options.client_version:
        source = "android-runtime-profile" if options.android_runtime_profile and options.android_runtime_profile.client_version else "server_config"
        write_json(out / "client_version.json", {"client_version": client_version, "source": source})

    client = BAReplayClient(
        host_url=host_url,
        api_url=api_url,
        bundle_version=options.bundle_version or client_version or None,
        client_version=client_version,
        timeout=options.timeout,
        proxy=options.gateway_proxy or options.proxy,
    )
    flow = run_main_game_login(
        client,
        credentials,
        output_dir=out,
        post=options.post,
        body_mode=options.body_mode,
        client_version=client_version,
        access_ip=options.access_ip,
        advertisement_id=options.account_auth_advertisement_id,
        idfv=options.account_auth_idfv,
        country=options.account_auth_country or options.country,
        locale=options.account_auth_locale or options.locale,
        device_id=options.device_id,
        device_system_memory_size=options.device_system_memory_size,
        market_id=options.market_id,
        user_type=options.user_type,
        game_option_language=options.game_option_language,
        account_auth_version=options.account_auth_version,
        account_auth_dev_id=options.account_auth_dev_id,
        omit_account_auth_dev_id=options.omit_account_auth_dev_id,
        account_auth_imei=options.account_auth_imei,
        omit_account_auth_imei=options.omit_account_auth_imei,
        account_check_key_mode=options.account_check_key_mode,
        account_check_url_mode=options.account_check_url_mode,
        account_check_field_mode=options.account_check_field_mode,
        queue_subchain=options.queue_subchain,
        queue_subchain_url_mode=options.queue_subchain_url_mode,
        queue_carry_crypto_forward=options.queue_carry_crypto_forward,
        native_relay_queue=options.native_relay_queue,
        native_relay_battle_pass_id=options.native_relay_battle_pass_id,
        native_relay_account_link_reward=options.native_relay_account_link_reward,
        native_relay_continue_on_error=options.native_relay_continue_on_error,
        skip_proof_token=options.skip_proof_token,
        proof_token_stage=options.proof_token_stage,
        proof_token_url_mode=options.proof_token_url_mode,
        proof_token_max_attempts=options.proof_token_max_attempts,
    )
    if connection is not None:
        flow["connection_info_path"] = str((out / "connection_info.json").resolve())
    return IntegratedLoginResult(web_tokens, toy_login, credentials, connection, android_runtime_profile, flow)


def resolve_web_tokens(options: IntegratedLoginOptions) -> WebLoginTokens:
    if options.web_token:
        return WebLoginTokens(web_token=options.web_token)
    if options.web_login:
        return run_playwright_web_login(
            country=options.country,
            locale=options.locale,
            proxy=options.web_proxy or options.proxy,
            close_on_callback=True,
            no_redact=True,
        )
    return load_latest_tokens(options.latest_token_path)


def apply_region_defaults(options: IntegratedLoginOptions) -> IntegratedLoginOptions:
    if options.proxy:
        options = replace(options, proxy=normalize_proxy_url(options.proxy))
    if options.web_proxy:
        options = replace(options, web_proxy=normalize_proxy_url(options.web_proxy))
    if options.gateway_proxy:
        options = replace(options, gateway_proxy=normalize_proxy_url(options.gateway_proxy))
    if not options.region:
        return options
    profile = profile_for(options.region, gid=options.gid)
    country = options.country
    locale = options.locale
    if country in ("", "TW") and profile.region != "tw":
        country = profile.default_country
    if locale in ("", "zh-TW") and profile.region != "tw":
        locale = profile.default_locale
    return replace(options, region=profile.region, country=country, locale=locale)


def resolve_android_runtime_profile(
    options: IntegratedLoginOptions,
    output_dir: Path,
) -> AndroidRuntimeProfile | None:
    if options.no_android_runtime_profile:
        return None
    root = options.android_runtime_dir
    if root is None:
        root = find_latest_android_runtime_pull()
        if root is None:
            return None
    try:
        profile = options.android_runtime_profile or load_android_runtime_profile(root)
    except Exception as exc:
        write_json(
            output_dir / "android_runtime_profile_error.json",
            {"type": type(exc).__name__, "message": str(exc), "path": str(root)},
        )
        if options.android_runtime_dir is not None:
            raise
        return None
    write_json(output_dir / "android_runtime_profile.json", profile.to_dict())
    return profile


def apply_android_runtime_profile_defaults(
    options: IntegratedLoginOptions,
    profile: AndroidRuntimeProfile | None,
) -> IntegratedLoginOptions:
    if profile is None:
        return options
    device_id = options.device_id or select_android_runtime_device_id(profile, options.android_device_id_source)
    return replace(
        options,
        android_runtime_profile=profile,
        region=options.region or profile.region,
        package_name=options.package_name or profile.app_id,
        android_uuid=options.android_uuid or profile.uuid,
        android_uuid2=options.android_uuid2 or profile.uuid2,
        android_adid=options.android_adid or profile.advertising_id,
        android_model=profile.device_model if options.android_model == "Pixel 7" and profile.device_model else options.android_model,
        android_os_version=(
            profile.android_os_version
            if options.android_os_version == "Android 13" and profile.android_os_version
            else options.android_os_version
        ),
        android_app_version_code=(
            profile.app_version_code
            if options.android_app_version_code == 429659 and profile.app_version_code is not None
            else options.android_app_version_code
        ),
        android_client_id=(
            profile.service_client_id
            if options.android_client_id == "2708" and profile.service_client_id
            else options.android_client_id
        ),
        device_id=device_id,
        game_option_language=options.game_option_language or profile.language,
        account_auth_dev_id=options.account_auth_dev_id,
        account_auth_country=options.account_auth_country or profile.user_country or profile.country,
        account_auth_locale=options.account_auth_locale or profile.locale,
        account_auth_advertisement_id=options.account_auth_advertisement_id or profile.advertising_id,
        account_auth_idfv=options.account_auth_idfv or profile.idfv,
    )


def resolve_toy_login(options: IntegratedLoginOptions, web_token: str, output_dir: Path) -> ToySdkLoginResult:
    if options.toy_login_json:
        return toy_login_from_file(options.toy_login_json)
    if options.no_native_login:
        return ToySdkLoginResult(
            np_sn=None,
            np_token="",
            npa_code="",
            session_token="",
            guid="",
            member_id="",
            member_type="",
            game_token="",
            ngsm_token="",
            callback=None,
        )
    if options.pc_native_login:
        from modules.auth.nexon_login import toy_callback_to_dict, toy_ticket_to_dict
        from modules.auth.toysdk_native import DEFAULT_NATIVE_DLL, ToySdkNative

        values = {
            "gid": options.gid,
            "serviceId": options.gid,
            "clientId": options.gid,
            "country": options.country,
            "locale": options.locale,
            "packageName": options.package_name,
        }

        def stage_callback(stage: str, value: Any) -> None:
            if stage == "toy_initialize_result":
                inface_result, game_auth_result = value
                write_json(
                    output_dir / "toy_initialize_result.json",
                    {
                        "inface": toy_callback_to_dict(inface_result),
                        "game_auth": toy_callback_to_dict(game_auth_result),
                    },
                )
                return
            if stage == "toy_ticket_result":
                write_json(output_dir / "toy_ticket_result.json", toy_ticket_to_dict(value))
                return
            if stage in ("toy_partial_login_result", "toy_sign_in_with_ticket_result"):
                write_json(output_dir / f"{stage}.json", toy_login_to_dict(value))
                return
            if stage in ("toy_game_token_result", "toy_agree_terms_result"):
                write_json(output_dir / f"{stage}.json", toy_callback_to_dict(value))

        if not web_token:
            raise ValueError("web_token is required for PC native TOYSDK login")
        with ToySdkNative(
            dll_path=DEFAULT_NATIVE_DLL,
            env=options.env,
            country=options.country,
            locale=options.locale,
            values=values,
        ) as sdk:
            ticket, login = sdk.login_with_web_token(
                web_token,
                launch_platform_type=options.launch_platform_type,
                store_type=options.store_type,
                package_name=options.package_name,
                security_token=options.security_token,
                timeout=options.timeout,
                stage_callback=stage_callback,
                agree_mode=options.native_agree_mode,
                sign_in_with_ticket=options.native_sign_in_with_ticket,
                sign_in_with_web_token=options.native_sign_in_with_web_token,
            )
        save_toy_results(output_dir, ticket_result=ticket, login_result=login)
        return login

    client = build_android_toy_client(options)
    ticket_result = None
    ticket = options.mobile_ticket
    if not ticket:
        if not web_token:
            raise ValueError("web_token or mobile_ticket is required for Android TOYSDK login")
        ticket_result = client.issue_ticket_by_web_token(web_token)
        ticket = ticket_result.ticket
    else:
        write_json(output_dir / "toy_ticket_result.json", {"ticket": ticket, "source": "provided"})
    session = client.login_with_ticket_flow(
        ticket,
        enter_toy=not options.mobile_skip_enter_toy,
        create_np_token=bool(options.mobile_create_np_token and not options.mobile_skip_create_np_token),
        get_user_info=not options.mobile_skip_user_info,
    )
    login = session.to_toy_login_result()
    write_json(
        output_dir / "toy_android_login_result.json",
        {
            "session": android_session_to_dict(session),
            "toyLogin": toy_login_to_dict(login),
            "device": asdict(client.device),
            "config": asdict(client.config),
        },
    )
    write_json(output_dir / "toy_android_requests.json", client.last_requests)
    save_toy_results(output_dir, ticket_result=ticket_result, login_result=login)
    return login


def build_android_toy_client(options: IntegratedLoginOptions) -> AndroidToySdkClient:
    package_name = options.package_name or "com.nexon.bluearchive"
    runtime_profile = options.android_runtime_profile
    runtime_country = options.country
    runtime_locale = options.locale
    initial_country = options.country
    device_country = options.country
    if runtime_profile is not None:
        runtime_country = runtime_profile.user_country or runtime_profile.country or runtime_country
        runtime_locale = runtime_profile.locale or runtime_locale
        initial_country = runtime_profile.initial_country or runtime_profile.country or runtime_country
        device_country = runtime_profile.country or runtime_country
    config = AndroidToyConfig(
        service_id=str(options.gid),
        client_id=str(options.android_client_id),
        game_id=str(options.android_game_id),
        package_name=package_name,
        store_type=options.store_type or "google",
        app_version_code=int(options.android_app_version_code),
    )
    device = AndroidDeviceProfile(
        country=runtime_country,
        locale=runtime_locale,
        initial_country=initial_country,
        device_country=device_country,
        uuid=options.android_uuid,
        uuid2=options.android_uuid2,
        os="A",
        os_version=options.android_os_version,
        device_model=options.android_model,
        advertising_id=options.android_adid,
    )
    return AndroidToySdkClient(
        config=config,
        device=device,
        proxy=options.web_proxy or options.proxy,
        timeout=options.timeout,
    )


def apply_toy_overrides(login: ToySdkLoginResult, overrides: ToyLoginOverrides) -> ToySdkLoginResult:
    game_token = overrides.game_token or login.game_token
    np_token = overrides.np_token or login.np_token
    ngsm_token = overrides.ngsm_token or login.ngsm_token
    if overrides.game_token_as_np_token and not np_token:
        np_token = game_token
    return ToySdkLoginResult(
        np_sn=overrides.np_sn if overrides.np_sn is not None else login.np_sn,
        np_token=np_token,
        npa_code=overrides.npa_code or login.npa_code,
        session_token=overrides.session_token or login.session_token,
        guid=overrides.guid or login.guid,
        member_id=overrides.member_id or login.member_id,
        member_type=overrides.member_type or login.member_type,
        um_key=login.um_key,
        game_token=game_token,
        ngsm_token=ngsm_token,
        callback=login.callback,
    )


def resolve_host_url(options: IntegratedLoginOptions) -> tuple[str, str, RuntimeConnectionInfo | None]:
    if options.host_url:
        return options.host_url, options.api_url, None
    if not options.auto_host:
        return "", options.api_url, None
    if options.android_runtime_profile and options.android_runtime_profile.gateway_url:
        profile = options.android_runtime_profile
        return profile.gateway_url, options.api_url or profile.api_url, None
    connection = discover_connection_info(
        country=options.country,
        region=options.region,
        local_low_dir=options.local_config_dir or Path.home() / "AppData" / "LocalLow" / "Nexon Games" / "Blue Archive",
    )
    return connection.gateway_url, options.api_url or connection.api_url, connection


def toy_login_from_file(path: str | Path) -> ToySdkLoginResult:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return ToySdkLoginResult(
        np_sn=to_int(data.get("npSN") or data.get("np_sn")),
        np_token=str(data.get("npToken") or data.get("np_token") or ""),
        npa_code=str(data.get("npaCode") or data.get("npa_code") or ""),
        session_token=str(data.get("sessionToken") or data.get("session_token") or ""),
        guid=str(data.get("guid") or ""),
        member_id=str(data.get("memberId") or data.get("member_id") or ""),
        member_type=str(data.get("memberType") or data.get("member_type") or ""),
        um_key=str(data.get("umKey") or data.get("um_key") or ""),
        game_token=str(data.get("gameToken") or data.get("game_token") or ""),
        ngsm_token=str(data.get("ngsmToken") or data.get("ngsm_token") or ""),
        callback=None,
    )


def write_json(path: str | Path, obj: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")


def to_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return dict(value)
    return str(value)

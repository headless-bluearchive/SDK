from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GameDefaults:
    service_id: str = "2079"
    client_id: str = "2708"
    game_id: str = "toy2079"
    package_name: str = "com.nexon.bluearchive"
    galaxy_store_package_name: str = "com.nexon.bluearchivegalaxy"
    service_title: str = "Blue Archive"
    store_type: str = "google"
    market_id: str = "GooglePlay"
    sdk_version: str = "1.3.132"
    app_version_code: int = 0
    client_version: str = ""
    android_model: str = ""
    android_os_version: str = ""
    android_account_auth_os_version: str = ""
    android_os_code: str = "A"
    country: str = "TW"
    locale: str = "zh-TW"
    env: str = "live"
    body_mode: str = "besthttp-multipart"
    toy_bolt_url: str = "https://m-api.nexon.com"
    toy_gw_bolt_url: str = "https://public.api.nexon.com/toy"
    ip_lookup_url: str = "https://api.ipify.org"
    replay_user_agent: str = "BAReplay/1.0"
    besthttp_user_agent: str = "BestHTTP/2 v2.4.0"
    besthttp_boundary_prefix: str = "BestHTTP_HTTPMultiPartForm_"
    main_game_profile: str = "android"


DEFAULTS = GameDefaults()

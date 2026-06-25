from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


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
    student_data_url: str = "https://blue-archive.io/config/json/students.json"
    student_data_fallback_url: str = "https://schaledb.com/data/cn/students.min.json"
    student_data_user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    student_data_cache_ttl_seconds: int = 86400
    official_resource_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.50.87 Safari/537.36"
    official_global_patch_url: str = "https://api-pub.nexon.com/patch/v1.1/version-check"
    official_global_market_game_id: str = "com.nexon.bluearchive"
    official_global_market_code: str = "playstore"
    official_global_table_targets: ClassVar[tuple[str, ...]] = (
        "Preload/TableBundles/ExcelDB.db",
        "Preload/TableBundles/Excel.zip",
    )
    official_download_workers: int = 8
    official_download_chunk_size: int = 8 * 1024 * 1024
    daily_reset_region: str = "global"
    daily_reset_utc_hour: int = 19
    daily_reset_utc_minute: int = 0
    daily_reset_local_timezone: str = "Asia/Shanghai"
    daily_reset_local_hour: int = 3
    daily_reset_local_minute: int = 0
    session_daily_reset_guard_enabled: bool = True
    session_lifecycle_key: str = "session_lifecycle"


DEFAULTS = GameDefaults()

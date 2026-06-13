import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.runtime.android_mobile_profile import (
    app_version_code_from_client_version,
    generate_android_mobile_profile,
    load_or_create_android_mobile_profile,
    save_android_mobile_profile,
    with_client_version,
)


def test_generate_android_mobile_profile_is_self_contained():
    profile = generate_android_mobile_profile(seed="stable-seed", country="TW", locale="zh-TW")

    assert profile.profile_kind == "android-mobile-synthetic"
    assert profile.country == "TW"
    assert profile.locale == "zh-TW"
    assert profile.device_model
    assert profile.os_version.startswith("Android ")
    assert profile.system_memory_mb >= 4096
    assert profile.device_unique_id
    assert profile.advertisement_id
    assert profile.idfv
    assert profile.app_set_id
    assert profile.mcc > 0


def test_android_mobile_profile_persists_generated_identity(tmp_path):
    profile_path = tmp_path / "android_mobile_profile.json"

    first = load_or_create_android_mobile_profile(profile_path, seed="stable-seed", country="TW", locale="zh-TW")
    second = load_or_create_android_mobile_profile(profile_path, seed="different-seed", country="TW", locale="zh-TW")

    assert second.device_unique_id == first.device_unique_id
    assert second.advertisement_id == first.advertisement_id
    assert second.idfv == first.idfv
    assert second.device_model
    assert second.os_version.startswith("Android ")
    assert second.system_memory_mb >= 4096


def test_android_mobile_profile_client_version_update_is_metadata_only(tmp_path):
    profile_path = tmp_path / "android_mobile_profile.json"
    profile = load_or_create_android_mobile_profile(profile_path, seed="stable-seed")
    updated = with_client_version(profile, "1.90.429659")
    save_android_mobile_profile(profile_path, updated)
    loaded = load_or_create_android_mobile_profile(profile_path)

    assert app_version_code_from_client_version("1.90.429659") == 429659
    assert loaded.client_version == "1.90.429659"
    assert loaded.app_version_code == 429659
    assert loaded.device_unique_id == profile.device_unique_id

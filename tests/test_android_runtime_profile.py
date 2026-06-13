import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.runtime.android_runtime_profile import (
    load_android_runtime_profile,
    read_shared_prefs_xml,
    select_android_runtime_device_id,
)
from modules.runtime.android_mobile_profile import (
    app_version_code_from_client_version,
    load_or_create_android_mobile_profile,
    save_android_mobile_profile,
    with_client_version,
)
from modules.runtime.runtime_profile_generator import generate_android_runtime_profile


def make_runtime_root(tmp_path: Path) -> Path:
    root = tmp_path / "ba_20260612_000000"
    external = root / "external_selected"
    prefs = root / "private_selected" / "shared_prefs"
    external.mkdir(parents=True)
    prefs.mkdir(parents=True)
    (root / "private_selected.tgz").write_bytes(b"")

    (external / "LocalConfig.json").write_text(
        json.dumps({"StringTable": {"LastRegion": "tw", "LastServer": "live"}}),
        encoding="utf-8",
    )
    (external / "Hosts").write_bytes(
        b"https://nxm-kr-bagl.nexon.com:5100\x00"
        b"https://nxm-tw-bagl.nexon.com:5100\x00"
        b"https://nxm-tw-bagl.nexon.com:5000\x00"
        b"https://nxm-th-bagl.nexon.com:5100\x00"
    )
    (external / "DeviceOption").write_text(
        json.dumps({"Language": "En", "VoiceLanguage": "JP"}),
        encoding="utf-8",
    )

    (prefs / "NPACommon.2079.xml").write_text(
        """<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
<map>
  <string name="country">US</string>
  <string name="initialCountry">US</string>
  <string name="userCountry">HK</string>
  <string name="locale">en_US</string>
  <string name="serviceClientId">MjcwOA</string>
  <string name="serviceTitle">Blue Archive</string>
  <string name="appId">com.nexon.bluearchive</string>
  <int name="appVersionCode" value="429659" />
  <int name="build_sdk_api_version" value="32" />
  <string name="userAgent">com.nexon.bluearchive/1.90.429659 (PGT-AN00; Android 12; Density/1.75; 1920x1080)</string>
  <string name="advertisingId">0905a578-1c40-4e34-863b-97f7477f1245</string>
  <string name="uuid">2392fff8-65d8-4aff-b075-5214c8cfb56f</string>
  <string name="uuid2">5f843fd4d0ac8615</string>
  <int name="lastLoginType" value="107" />
  <int name="useNgsx" value="1" />
  <int name="useNgsm" value="0" />
  <boolean name="useGbKrpc" value="true" />
  <boolean name="useGbNpsn" value="true" />
  <string name="loginUIType">1</string>
  <string name="nkMemberAccessCode">2000088010</string>
  <int name="termsApiVer" value="2" />
  <int name="policyApiVer" value="2" />
  <string name="mcc">460</string>
  <string name="mnc">000</string>
  <string name="carrierName">CHINA MOBILE</string>
</map>
""",
        encoding="utf-8",
    )
    (prefs / "NxAnalyticsPreference.xml").write_text(
        """<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
<map>
  <string name="adid">0905a578-1c40-4e34-863b-97f7477f1245</string>
  <string name="installcountryname">CN</string>
  <string name="mid">2392fff8-65d8-4aff-b075-5214c8cfb56f</string>
  <string name="idfv">f98ca9db-617c-3b21-7457-8488e3344881</string>
</map>
""",
        encoding="utf-8",
    )
    (prefs / "NPAccountGCMPref.xml").write_text(
        """<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
<map><int name="appVersion" value="429659" /></map>
""",
        encoding="utf-8",
    )
    (prefs / "com.nexon.bluearchive.v2.playerprefs.xml").write_text(
        """<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
<map><string name="SaveUID">17%20817%20937</string></map>
""",
        encoding="utf-8",
    )
    return root


def test_shared_prefs_parser_reads_text_and_value_attributes(tmp_path):
    root = make_runtime_root(tmp_path)
    data = read_shared_prefs_xml(root / "private_selected" / "shared_prefs" / "NPACommon.2079.xml")

    assert data["serviceClientId"] == "MjcwOA"
    assert data["appVersionCode"] == 429659
    assert data["useGbKrpc"] is True
    assert data["useNgsm"] == 0


def test_load_android_runtime_profile_extracts_auth_relevant_fields(tmp_path):
    root = make_runtime_root(tmp_path)
    profile = load_android_runtime_profile(root)

    assert profile.region == "tw"
    assert profile.server == "live"
    assert profile.gateway_url == "https://nxm-tw-bagl.nexon.com:5100/api/"
    assert profile.api_url == "https://nxm-tw-bagl.nexon.com:5000/api/"
    assert profile.service_client_id == "2708"
    assert profile.client_version == "1.90.429659"
    assert profile.app_version_code == 429659
    assert profile.use_ngsx == 1
    assert profile.use_ngsm == 0
    assert profile.device_model == "PGT-AN00"
    assert profile.android_os_version == "Android 12"
    assert profile.advertising_id == "0905a578-1c40-4e34-863b-97f7477f1245"
    assert profile.idfv == "f98ca9db-617c-3b21-7457-8488e3344881"
    assert profile.language == "En"
    assert profile.voice_language == "JP"
    assert select_android_runtime_device_id(profile, "auto") == "2392fff8-65d8-4aff-b075-5214c8cfb56f"
    assert select_android_runtime_device_id(profile, "save-uid") == "17 817 937"


def test_generate_android_runtime_profile_inherits_base_and_rotates_ids(tmp_path):
    base = make_runtime_root(tmp_path)
    out = tmp_path / "generated"

    generate_android_runtime_profile(out, seed="test-seed", base_runtime_dir=base)
    generated = load_android_runtime_profile(out)

    assert generated.device_model == "PGT-AN00"
    assert generated.android_os_version == "Android 12"
    assert generated.client_version == "1.90.429659"
    assert generated.app_version_code == 429659
    assert generated.uuid != "2392fff8-65d8-4aff-b075-5214c8cfb56f"
    assert generated.advertising_id != "0905a578-1c40-4e34-863b-97f7477f1245"
    assert generated.idfv != "f98ca9db-617c-3b21-7457-8488e3344881"


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


if __name__ == "__main__":
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as d:
        test_shared_prefs_parser_reads_text_and_value_attributes(Path(d))
    with TemporaryDirectory() as d:
        test_load_android_runtime_profile_extracts_auth_relevant_fields(Path(d))
    with TemporaryDirectory() as d:
        test_generate_android_runtime_profile_inherits_base_and_rotates_ids(Path(d))
    with TemporaryDirectory() as d:
        test_android_mobile_profile_persists_generated_identity(Path(d))
    with TemporaryDirectory() as d:
        test_android_mobile_profile_client_version_update_is_metadata_only(Path(d))
    print("test_android_runtime_profile ok")

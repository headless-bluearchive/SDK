import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from headlessba.modules.auth.equivalence import compare_login_artifact_sources, load_login_artifact_source, token_kind


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def base_login(*, np_token: str) -> dict:
    return {
        "npSN": 20790000000000000,
        "npToken": np_token,
        "npaCode": "0E50ZZZ10F02I",
        "sessionToken": "",
        "guid": "20790000000000000",
        "memberId": "73529028",
        "memberType": "107",
        "umKey": "107:73529028",
        "gameToken": np_token,
        "ngsmToken": "",
    }


def test_token_kind_classification():
    assert token_kind("") == "empty"
    assert token_kind("ias:wt:1") == "ias-web-token"
    assert token_kind("ias:gt:1") == "ias-game-token"
    assert token_kind("ias:t:1") == "ias-ticket"
    assert token_kind("TOUabcdef") == "toysdk-token"
    assert token_kind("a" * 128) == "hex128"


def test_compare_sources_same_identity_ignores_token_value_by_default(tmp_path):
    left = tmp_path / "left"
    right = tmp_path / "right"
    write_json(left / "toy_login_summary.json", base_login(np_token="ias:gt:1111111111@aaaaaaaa:ATW"))
    write_json(right / "toy_login_summary.json", base_login(np_token="ias:gt:2222222222@bbbbbbbb:ATW"))

    report = compare_login_artifact_sources(
        load_login_artifact_source(left),
        load_login_artifact_source(right),
    )

    assert report["summary"]["same_account_identity"] is True
    assert report["summary"]["pre_game_token_surface_match"] is True
    assert report["summary"]["game_surface_core_match"] is None
    assert report["summary"]["converges_in_game"] is None


def test_compare_sources_flags_token_kind_difference(tmp_path):
    left = tmp_path / "left"
    right = tmp_path / "right"
    write_json(left / "toy_login_summary.json", base_login(np_token="ias:gt:1111111111@aaaaaaaa:ATW"))
    write_json(right / "toy_login_summary.json", base_login(np_token="TOUabcdef1234567890"))

    report = compare_login_artifact_sources(
        load_login_artifact_source(left),
        load_login_artifact_source(right),
    )

    assert report["summary"]["same_account_identity"] is True
    assert report["summary"]["pre_game_token_surface_match"] is False


def test_compare_account_check_request_ignores_dynamic_ticket_and_crypto(tmp_path):
    left = tmp_path / "left"
    right = tmp_path / "right"
    write_json(left / "toy_login_summary.json", base_login(np_token="ias:gt:1111111111@aaaaaaaa:ATW"))
    write_json(right / "toy_login_summary.json", base_login(np_token="ias:gt:2222222222@bbbbbbbb:ATW"))
    write_json(
        left / "02_account_check_nexon.request.json",
        {
            "Protocol": 1014,
            "Hash": 1,
            "EnterTicket": "ticket-left",
            "ClientGeneratedKey": "QUFBQQ==",
            "ClientGeneratedIV": "QkJCQg==",
        },
    )
    write_json(
        right / "02_account_check_nexon.request.json",
        {
            "Protocol": 1014,
            "Hash": 2,
            "EnterTicket": "ticket-right",
            "ClientGeneratedKey": "Q0NDQw==",
            "ClientGeneratedIV": "RERERA==",
        },
    )

    report = compare_login_artifact_sources(
        load_login_artifact_source(left),
        load_login_artifact_source(right),
    )

    account_check = report["request_comparison"]["02_account_check_nexon"]
    assert account_check["available"] is True
    assert account_check["core_equal"] is True
    assert account_check["dynamic_equal"] is False
    assert report["summary"]["game_request_core_match"] is True


def test_compare_account_auth_environment_is_non_strict_by_default(tmp_path):
    left = tmp_path / "left"
    right = tmp_path / "right"
    write_json(left / "toy_login_summary.json", base_login(np_token="ias:gt:1111111111@aaaaaaaa:ATW"))
    write_json(right / "toy_login_summary.json", base_login(np_token="ias:gt:1111111111@aaaaaaaa:ATW"))
    request_common = {
        "Protocol": 1002,
        "SessionKey": {"AccountServerId": 12345678, "MxToken": "mx-token"},
        "AccountId": 12345678,
        "Resendable": True,
        "IsTest": False,
        "CountryCode": "TW",
        "DeviceLocaleCode": "zh-TW",
        "GameOptionLanguage": "Tw",
        "MarketId": "GooglePlay",
        "OSType": "Android",
        "IsTeenVersion": False,
        "DeviceModel": "Pixel 7",
        "OSVersion": "Android OS 13 / API-33",
        "DeviceSystemMemorySize": 8192,
        "AdvertisementId": "",
        "Idfv": "",
        "IMEI": 0,
    }
    left_request = dict(request_common, DeviceUniqueId="uuid-left", DevId="dev-left")
    right_request = dict(request_common, DeviceUniqueId="uuid-right", DevId="dev-right")
    write_json(left / "03_account_auth.request.json", left_request)
    write_json(right / "03_account_auth.request.json", right_request)

    report = compare_login_artifact_sources(
        load_login_artifact_source(left),
        load_login_artifact_source(right),
    )

    account_auth = report["request_comparison"]["03_account_auth"]
    assert account_auth["core_equal"] is True
    assert account_auth["environment_equal"] is True

    strict_report = compare_login_artifact_sources(
        load_login_artifact_source(left),
        load_login_artifact_source(right),
        strict_environment=True,
    )
    strict_auth = strict_report["request_comparison"]["03_account_auth"]
    assert strict_auth["core_equal"] is True
    assert strict_auth["environment_equal"] is False

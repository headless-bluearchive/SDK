import base64
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import main as cli_main

from headlessba.core.client import BAReplayClient, build_besthttp_multipart, decode_gateway_response
from headlessba.modules.auth.flows import IntegratedLoginOptions
from headlessba.modules.runtime.android_runtime_profile import AndroidRuntimeProfile, select_android_runtime_device_id
from headlessba.core.crypto import (
    ACCOUNT_CHECK_NEXON_RSA_PUBLIC_KEY_PEM,
    account_check_nexon_key_iv_fields,
    aes_cbc_pkcs7_decrypt,
    fast_crc,
    generated_key_iv_fields,
    ungzip_length_prefixed,
    xor_crypt,
)
from headlessba.core.packet import build_packet, create_hash, parse_packet
from headlessba.modules.auth.proof_token import proof_token_hash, proof_token_search_span, solve_proof_token
from headlessba.core.protocol import type_conversion
from headlessba.modules.auth.login import LoginReplay
from headlessba.utils.proxy import normalize_proxy_url, playwright_proxy_options, requests_proxy_map
from headlessba.modules.runtime.region_config import build_login_url, profile_for
from headlessba.modules.runtime.runtime_config import discover_connection_info, extract_urls_from_hosts, normalize_service_base
from headlessba.modules.auth.toysdk_android import (
    AndroidDeviceProfile,
    AndroidToySdkClient,
    LOGIN_TYPE_NXARENA,
    LOGIN_TYPE_NXCOM,
    ToySdkAndroidTurnstileRequired,
    _latin1_headers,
    npsn_aes128_key,
    toy_decrypt,
    toy_encrypt,
)
from headlessba.modules.auth.nexon_login import (
    NATIVE_LOGIN_SYNC_NO_PART_PROTOCOLS,
    _apply_account_check_state,
    build_account_auth_fields,
    build_account_check_nexon_fields,
    build_android_security_state,
    build_account_login_sync_no_part_fields,
    build_credentials,
    normalize_account_auth_os_type,
    run_native_relay_queue,
    _is_empty_success_response,
)
from headlessba.modules.auth.toysdk_models import ToySdkLoginResult
from headlessba.modules.runtime.runtime_config import RuntimeConnectionInfo


def test_protocol_converter_sample():
    assert type_conversion(4, 37000) == 0x21BA2799


def test_fast_crc_check_value():
    # MSB-first CRC-32, poly 0x04C11DB7, init 0, xorout 0.
    assert fast_crc(b"123456789") == 0x89A1897F


def test_create_hash_high_bits():
    assert create_hash(1002, counter=7) == (1002 << 32) | 7


def test_proof_token_solver_uses_hint_lowbit_span():
    hint = 40
    answer = 45
    question = proof_token_hash(answer)

    assert proof_token_search_span(hint) == 8
    assert solve_proof_token(question, hint) == answer


def test_packet_layout_and_roundtrip():
    packet, meta, request_bytes = build_packet(
        "ProofToken_Submit",
        {"Answer": 123},
        aes_encrypted_key=b"k",
        aes_encrypted_iv=b"iv",
        counter=1,
    )
    assert packet[:4] == meta.crc.to_bytes(4, "little")
    assert packet[8] == 1
    assert packet[9] == 2
    assert packet[10:11] == b"k"
    assert packet[11:13] == b"iv"

    parsed = parse_packet(packet)
    assert parsed.aes_encrypted_key == b"k"
    assert parsed.aes_encrypted_iv == b"iv"
    decoded = json.loads(parsed.request_bytes.decode("utf-8"))
    assert decoded["Protocol"] == 37001
    assert decoded["Answer"] == 123
    assert ungzip_length_prefixed(xor_crypt(parsed.payload)) == request_bytes


def test_packet_can_encrypt_request_payload_like_pc_session_lane():
    packet, meta, request_bytes = build_packet(
        "NetworkTime_Sync",
        {},
        session_key={"AccountServerId": 12345678, "MxToken": "mx-token"},
        aes_encrypted_key=b"k" * 32,
        aes_encrypted_iv=b"i" * 32,
        request_aes_key=b"a" * 16,
        request_aes_iv=b"b" * 16,
        include_base_defaults=True,
        counter=1,
    )

    parsed = parse_packet(packet)
    assert meta.request_payload_encrypted is True
    assert parsed.request_bytes == request_bytes
    assert len(request_bytes) % 16 == 0
    decoded = json.loads(aes_cbc_pkcs7_decrypt(request_bytes, b"a" * 16, b"b" * 16).decode("utf-8"))
    assert decoded["Protocol"] == 3
    assert decoded["AccountId"] == 12345678
    assert decoded["Resendable"] is True


def test_pc_post_account_check_request_lengths_match_dynamic_capture():
    client = BAReplayClient()
    client.session_key = {
        "AccountServerId": 12345678,
        "MxToken": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
    }
    client.set_crypto(
        aes_key=b"a" * 16,
        aes_iv=b"b" * 16,
        aes_encrypted_key=b"k" * 32,
        aes_encrypted_iv=b"i" * 32,
    )
    login = LoginReplay(client)

    proof = login.proof_token_question()
    network_time = login.native_relay_request("NetworkTimeSyncRequest", {}, include_base_defaults=True)

    assert proof.meta.serialized_request_len == 194
    assert len(proof.request_bytes) == 208
    assert proof.meta.request_payload_encrypted is True
    assert network_time.meta.serialized_request_len == 186
    assert len(network_time.request_bytes) == 192
    assert network_time.meta.request_payload_encrypted is True


def test_account_check_nexon_stays_unencrypted_even_with_carried_crypto():
    client = BAReplayClient()
    client.set_crypto(
        aes_key=b"a" * 16,
        aes_iv=b"b" * 16,
        aes_encrypted_key=b"k" * 32,
        aes_encrypted_iv=b"i" * 32,
    )

    built = LoginReplay(client).account_check_nexon(
        {
            "EnterTicket": "ticket",
            "ClientGeneratedKey": "key",
            "ClientGeneratedIV": "iv",
        }
    )

    assert built.meta.request_payload_encrypted is False
    assert built.request_bytes == built.serialized_request_bytes
    assert json.loads(built.request_bytes.decode("utf-8"))["Protocol"] == 1014


def test_besthttp_multipart_binary_body():
    body, content_type = build_besthttp_multipart("mx", b"\x00abc", boundary="fixed-boundary")
    assert content_type == "multipart/form-data; boundary=fixed-boundary"
    assert body == (
        b"--fixed-boundary\r\n"
        b'Content-Disposition: form-data; name="mx"; filename="mx.dat"\r\n'
        b"Content-Type: application/octet-stream\r\n"
        b"Content-Length: 4\r\n"
        b"\r\n"
        b"\x00abc\r\n"
        b"--fixed-boundary--\r\n"
    )


def test_runtime_hosts_gateway_discovery(tmp_path):
    local_config = tmp_path / "LocalConfig.json"
    hosts = tmp_path / "Hosts"
    local_config.write_text(
        json.dumps({"StringTable": {"LastRegion": "tw", "LastServer": "live"}}),
        encoding="utf-8",
    )
    hosts.write_bytes(
        b"\x00https://nxm-eu-bagl.nexon.com:5100\x00"
        b"https://nxm-tw-bagl.nexon.com:5100\x00"
        b"https://nxm-tw-bagl.nexon.com:5000\x00"
    )

    assert extract_urls_from_hosts(hosts) == [
        "https://nxm-eu-bagl.nexon.com:5100",
        "https://nxm-tw-bagl.nexon.com:5100",
        "https://nxm-tw-bagl.nexon.com:5000",
    ]
    assert normalize_service_base("https://nxm-tw-bagl.nexon.com:5100") == "https://nxm-tw-bagl.nexon.com:5100/api/"

    info = discover_connection_info(local_low_dir=tmp_path)
    assert info.region == "tw"
    assert info.gateway_url == "https://nxm-tw-bagl.nexon.com:5100/api/"
    assert info.gateway_endpoint == "https://nxm-tw-bagl.nexon.com:5100/api/gateway"
    assert info.api_url == "https://nxm-tw-bagl.nexon.com:5000/api/"


def test_region_profiles_and_fallback(tmp_path):
    (tmp_path / "LocalConfig.json").write_text(
        json.dumps({"StringTable": {"LastRegion": "tw", "LastServer": "live"}}),
        encoding="utf-8",
    )
    (tmp_path / "Hosts").write_bytes(b"https://nxm-tw-bagl.nexon.com:5100\x00")

    na = profile_for("na")
    assert na.api_url == "https://nxm-or-bagl.nexon.com:5000/api/"
    assert na.gateway_endpoint == "https://nxm-or-bagl.nexon.com:5100/api/gateway"
    assert "country=US" in build_login_url(na, hsid="00000000-0000-4000-8000-000000000000")

    info = discover_connection_info(region="na", local_low_dir=tmp_path)
    assert info.source == "static-server-profile"
    assert info.gateway_url == "https://nxm-or-bagl.nexon.com:5100/api/"


def test_proxy_normalization_and_maps():
    assert normalize_proxy_url("127.0.0.1:60808") == "http://127.0.0.1:60808"
    assert normalize_proxy_url("socks://127.0.0.1:60808") == "socks5://127.0.0.1:60808"
    assert requests_proxy_map("socks5://127.0.0.1:60808") == {
        "http": "socks5://127.0.0.1:60808",
        "https": "socks5://127.0.0.1:60808",
    }
    assert playwright_proxy_options("http://127.0.0.1:60808") == {
        "server": "http://127.0.0.1:60808",
        "bypass": "localhost,127.0.0.1,::1",
    }


def test_client_splits_gateway_and_api_urls():
    client = BAReplayClient(
        host_url="https://nxm-tw-bagl.nexon.com:5100/api/",
        api_url="https://nxm-tw-bagl.nexon.com:5000/api/",
    )
    assert client.gateway_url == "https://nxm-tw-bagl.nexon.com:5100/api/gateway"
    assert client.api_url == "https://nxm-tw-bagl.nexon.com:5000/api/"
    assert client.session_api_url == "https://nxm-tw-bagl.nexon.com:5000/api/"

    client = BAReplayClient(
        host_url="https://nxm-tw-bagl.nexon.com:5100/api/",
        api_url="https://nxm-tw-bagl.nexon.com:5000/api/",
        session_api_url="https://nxm-tw-bagl.nexon.com:5100/api/",
    )
    assert client.session_api_url == "https://nxm-tw-bagl.nexon.com:5100/api/"


def test_apply_account_check_state_records_o22_material():
    client = BAReplayClient()
    client.set_crypto(aes_key=b"a" * 16, aes_iv=b"b" * 16)
    parsed = {
        "Protocol": 1014,
        "EncryptedKey": base64.b64encode(b"k" * 32).decode("ascii"),
        "EncryptedIV": base64.b64encode(b"i" * 32).decode("ascii"),
        "SignedKey": base64.b64encode(b"s" * 256).decode("ascii"),
        "SignedIV": base64.b64encode(b"v" * 256).decode("ascii"),
        "ServerTimeTicks": 639169326780000000,
        "SessionKey": {"AccountServerId": 12345678, "MxToken": "mx-token"},
        "AccountId": 12345678,
    }

    state = _apply_account_check_state(client, parsed)

    assert client.account_id == 12345678
    assert client.server_time_ticks == 639169326780000000
    assert client.session_key == {"AccountServerId": 12345678, "MxToken": "mx-token"}
    assert client.aes_encrypted_key == b"k" * 32
    assert client.aes_encrypted_iv == b"i" * 32
    assert client.signed_key == b"s" * 256
    assert client.signed_iv == b"v" * 256
    assert state["encrypted_key"]["decoded_len"] == 32
    assert state["encrypted_iv"]["decoded_len"] == 32
    assert state["signed_key"]["decoded_len"] == 256
    assert state["signed_iv"]["decoded_len"] == 256
    assert state["local_crypto_lane"] == {"aes_key_len": 16, "aes_iv_len": 16}
    assert state["o22_semantics"]["applied_to_client"] is True
    assert state["o22_semantics"]["game_session_manager_0x78_len"] == 32
    assert state["o22_semantics"]["game_session_manager_0x80_len"] == 32


def test_empty_http_200_response_is_success_noop():
    assert _is_empty_success_response(
        {
            "http": {"status_code": 200},
            "raw": "",
            "payload": "",
            "parsed": None,
        }
    )
    assert not _is_empty_success_response(
        {
            "http": {"status_code": 500},
            "raw": "",
            "payload": "",
            "parsed": None,
        }
    )


def test_android_profile_is_the_only_main_game_profile():
    parser = cli_main.build_arg_parser()
    args = parser.parse_args(["--main-game-profile", "android"])

    assert args.main_game_profile == "android"
    try:
        parser.parse_args(["--main-game-profile", "pc-steam"])
    except SystemExit:
        pass
    else:
        raise AssertionError("pc-steam should not be an active main-game profile")


def test_android_session_api_defaults_to_api_url(monkeypatch, tmp_path):
    args = cli_main.build_arg_parser().parse_args([])
    args.output_dir = tmp_path
    info = RuntimeConnectionInfo(
        local_low_dir=str(tmp_path),
        local_config_path=str(tmp_path / "LocalConfig.json"),
        hosts_path=str(tmp_path / "Hosts"),
        region="tw",
        server="live",
        api_url="https://nxm-tw-bagl.nexon.com:5000/api/",
        gateway_url="https://nxm-tw-bagl.nexon.com:5100/api/",
        gateway_endpoint="https://nxm-tw-bagl.nexon.com:5100/api/gateway",
        source="test",
        discovered_urls=(),
    )

    monkeypatch.setattr(cli_main, "discover_connection_info", lambda **kwargs: info)

    host_url, api_url = cli_main.resolve_service_urls(args)
    session_api_url = cli_main.resolve_session_api_url(args, host_url, api_url)

    assert host_url == "https://nxm-tw-bagl.nexon.com:5100/api/"
    assert api_url == "https://nxm-tw-bagl.nexon.com:5000/api/"
    assert session_api_url == "https://nxm-tw-bagl.nexon.com:5000/api/"


def test_explicit_session_api_url_overrides_android_default(monkeypatch, tmp_path):
    args = cli_main.build_arg_parser().parse_args(
        ["--session-api-url", "https://example.invalid/api/"]
    )
    args.output_dir = tmp_path
    info = RuntimeConnectionInfo(
        local_low_dir=str(tmp_path),
        local_config_path=str(tmp_path / "LocalConfig.json"),
        hosts_path=str(tmp_path / "Hosts"),
        region="tw",
        server="live",
        api_url="https://nxm-tw-bagl.nexon.com:5000/api/",
        gateway_url="https://nxm-tw-bagl.nexon.com:5100/api/",
        gateway_endpoint="https://nxm-tw-bagl.nexon.com:5100/api/gateway",
        source="test",
        discovered_urls=(),
    )

    monkeypatch.setattr(cli_main, "discover_connection_info", lambda **kwargs: info)

    host_url, api_url = cli_main.resolve_service_urls(args)
    session_api_url = cli_main.resolve_session_api_url(args, host_url, api_url)

    assert host_url == "https://nxm-tw-bagl.nexon.com:5100/api/"
    assert api_url == "https://nxm-tw-bagl.nexon.com:5000/api/"
    assert session_api_url == "https://example.invalid/api/"


def test_pc_runtime_profile_json_override_loads_profile_and_cid(tmp_path):
    profile_path = tmp_path / "steam_runtime_profile.json"
    profile_path.write_text(
        json.dumps(
            {
                "pcRuntimeProfile": {
                    "computer_name": "DESKTOP-TEST",
                    "device_model": "Test PC Model",
                    "os_version": "Microsoft Windows 11 Pro (10.0.22631)",
                    "system_memory_mb": 16384,
                    "source": "test",
                },
                "launcherState": {
                    "cid": "20790000000000001",
                    "cid_pool": ["20790000000000001", "20790000000000002"],
                    "token_infos": [],
                },
            }
        ),
        encoding="utf-8",
    )

    pc_profile, launcher_state, _raw = cli_main.load_pc_runtime_profile_override(profile_path)

    assert pc_profile.device_model == "Test PC Model"
    assert pc_profile.os_version == "Microsoft Windows 11 Pro (10.0.22631)"
    assert pc_profile.system_memory_mb == 16384
    assert launcher_state is not None
    assert launcher_state.cid == "20790000000000001"
    assert launcher_state.cid_pool == ("20790000000000001", "20790000000000002")


def test_integrated_login_options_expose_queue_subchain_controls():
    options = IntegratedLoginOptions(
        queue_subchain=True,
        queue_subchain_url_mode="api",
        queue_carry_crypto_forward=True,
        native_relay_queue=False,
        native_relay_battle_pass_id=42,
        native_relay_account_link_reward=True,
        native_relay_continue_on_error=True,
    )

    assert options.queue_subchain is True
    assert options.queue_subchain_url_mode == "api"
    assert options.queue_carry_crypto_forward is True
    assert options.native_relay_queue is False
    assert options.native_relay_battle_pass_id == 42
    assert options.native_relay_account_link_reward is True
    assert options.native_relay_continue_on_error is True


def test_account_login_sync_no_part_protocols_match_native_list():
    fields = build_account_login_sync_no_part_fields()

    assert fields["SkillCutInOption"] == "All"
    assert fields["SyncProtocols"] == NATIVE_LOGIN_SYNC_NO_PART_PROTOCOLS
    assert fields["SyncProtocols"] == [
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


def test_native_relay_queue_builds_offline_and_skips_inactive_battle_pass(tmp_path):
    client = BAReplayClient(
        host_url="https://nxm-tw-bagl.nexon.com:5100/api/",
        api_url="https://nxm-tw-bagl.nexon.com:5000/api/",
    )
    client.session_key = {"AccountServerId": 1, "MxToken": "mx"}
    client.set_crypto(
        aes_key=b"k" * 16,
        aes_iv=b"i" * 16,
        aes_encrypted_key=b"ek",
        aes_encrypted_iv=b"iv",
    )
    flow = {"steps": []}

    state = run_native_relay_queue(
        client,
        LoginReplay(client),
        output_dir=tmp_path,
        flow=flow,
        post=False,
        body_mode="besthttp-multipart",
        skill_cut_in_option="All",
        battle_pass_id=None,
        include_account_link_reward=False,
        continue_on_error=False,
    )

    assert [task["request_class"] for task in state["tasks"][:6]] == [
        "NetworkTimeSyncRequest",
        "AcademyGetInfoRequest",
        "AccountLoginSyncRequest",
        "ItemListRequest",
        "ContentSaveGetRequest",
        "ShopBeforehandGachaGetRequest",
    ]
    assert state["tasks"][2]["sync_protocols"] == NATIVE_LOGIN_SYNC_NO_PART_PROTOCOLS
    assert state["tasks"][-1]["status"] == "skipped"
    assert state["tasks"][-1]["request_class"] == "BattlePassGetInfoRequest"


def test_client_default_headers_fallback_to_client_version():
    client = BAReplayClient(client_version="1.90.429659")
    assert client.default_headers()["Bundle-Version"] == "1.90.429659"
    assert client.default_headers()["User-Agent"] == "BestHTTP/2 v2.4.0"

    client = BAReplayClient(bundle_version="1.91.000000", client_version="1.90.429659")
    assert client.default_headers()["Bundle-Version"] == "1.91.000000"


def test_client_post_packet_records_http_exchange(monkeypatch):
    class FakeResponse:
        def __init__(self):
            self.status_code = 200
            self.reason = "OK"
            self.text = "ok"
            self.url = "https://example.invalid/api/gateway"
            self.headers = {"Set-Cookie": "sid=abc"}
            self.cookies = {"sid": "abc"}
            self.history = []
            self.request = type(
                "Req",
                (),
                {
                    "method": "POST",
                    "url": "https://example.invalid/api/gateway",
                    "headers": {"mx": "2", "Bundle-Version": "1.90.429659"},
                },
            )()

    class FakeSession:
        def __init__(self):
            self.cookies = {"sid": "abc"}

        def post(self, url, **kwargs):
            assert kwargs["headers"]["Bundle-Version"] == "1.90.429659"
            return FakeResponse()

    class FakeRequestsModule:
        class exceptions:
            class InvalidSchema(Exception):
                pass

        class utils:
            @staticmethod
            def dict_from_cookiejar(jar):
                return dict(jar)

        @staticmethod
        def Session():
            return FakeSession()

    monkeypatch.setitem(sys.modules, "requests", FakeRequestsModule())
    client = BAReplayClient(
        host_url="https://example.invalid/api/",
        client_version="1.90.429659",
    )
    assert client.post_packet(b"payload") == "ok"
    assert client.last_exchange["request_headers"]["Bundle-Version"] == "1.90.429659"
    assert client.last_exchange["response_cookies"] == {"sid": "abc"}
    assert client.last_exchange["session_cookies"] == {"sid": "abc"}


def test_gateway_wrapper_plain_error_packet_is_not_aes_decrypted():
    raw = '{"protocol":"Error","packet":"{\\"Protocol\\":-1,\\"ErrorCode\\":5}"}'
    decoded = decode_gateway_response(raw, aes_key=b"0" * 16, aes_iv=b"1" * 16)
    assert decoded.protocol == "Error"
    assert json.loads(decoded.payload)["ErrorCode"] == 5


def test_android_toysdk_common_and_npsn_crypto_roundtrip():
    plain = b'{"hello":"world"}'
    assert toy_decrypt("COMMON", toy_encrypt("COMMON", plain)) == plain
    assert len(npsn_aes128_key(123456789)) == 16
    assert toy_decrypt("NPSN", toy_encrypt("NPSN", plain, 123456789), 123456789) == plain


def test_android_toysdk_headers_are_latin1_safe():
    headers = _latin1_headers({"osVersion": "Microsoft Windows 11 专业版 (10.0.26200)", "npsn": 123})

    assert headers["osVersion"] == "Microsoft Windows 11  (10.0.26200)"
    assert headers["npsn"] == "123"


def test_account_check_nexon_key_iv_fields_are_rsa_encrypted():
    assert len(ACCOUNT_CHECK_NEXON_RSA_PUBLIC_KEY_PEM) == 451

    key = b"k" * 16
    iv = b"i" * 16
    queue_fields, _, _ = generated_key_iv_fields(key, iv)
    account_fields, raw_key, raw_iv = account_check_nexon_key_iv_fields(key, iv)

    assert raw_key == key
    assert raw_iv == iv
    assert len(base64.b64decode(queue_fields["ClientGeneratedKey"])) == 16
    assert len(base64.b64decode(account_fields["ClientGeneratedKey"])) == 256
    assert len(base64.b64decode(account_fields["ClientGeneratedIV"])) == 256
    assert account_fields["ClientGeneratedKey"] != queue_fields["ClientGeneratedKey"]


def test_account_check_nexon_key_iv_diagnostic_modes():
    key = b"k" * 16
    iv = b"i" * 16

    raw_fields, _, _ = account_check_nexon_key_iv_fields(key, iv, mode="raw-base64")
    assert base64.b64decode(raw_fields["ClientGeneratedKey"]) == key
    assert base64.b64decode(raw_fields["ClientGeneratedIV"]) == iv

    for mode in ("rsa-base64-text", "rsa-hex-text"):
        fields, raw_key, raw_iv = account_check_nexon_key_iv_fields(key, iv, mode=mode)
        assert raw_key == key
        assert raw_iv == iv
        assert len(base64.b64decode(fields["ClientGeneratedKey"])) == 256
        assert len(base64.b64decode(fields["ClientGeneratedIV"])) == 256


def test_account_check_nexon_android_minimal_fields():
    toy_login = ToySdkLoginResult(
        np_sn=123456789,
        np_token="game-token",
        npa_code="npa-code",
        session_token="",
        guid="123456789",
        member_id="abc",
        member_type="107",
        um_key="107:abc",
        game_token="game-token",
        callback=None,
    )
    credentials = build_credentials(toy_login, allow_empty_ngsm_token=True)
    minimal = build_account_check_nexon_fields(
        credentials,
        enter_ticket="ticket",
        client_generated_key="key",
        client_generated_iv="iv",
    )
    assert minimal == {
        "ClientGeneratedIV": "iv",
        "ClientGeneratedKey": "key",
        "EnterTicket": "ticket",
    }

    full = build_account_check_nexon_fields(
        credentials,
        enter_ticket="ticket",
        client_generated_key="key",
        client_generated_iv="iv",
        mode="full",
    )
    assert full["NpSN"] == 123456789
    assert full["NpToken"] == "game-token"
    assert full["PassCheckNexonServer"] is True


def test_account_auth_fields_include_runtime_adid_and_idfv():
    fields = build_account_auth_fields(
        advertisement_id="0905a578-1c40-4e34-863b-97f7477f1245",
        idfv="f98ca9db-617c-3b21-7457-8488e3344881",
        device_id="2392fff8-65d8-4aff-b075-5214c8cfb56f",
    )

    assert fields["AdvertisementId"] == "0905a578-1c40-4e34-863b-97f7477f1245"
    assert fields["Idfv"] == "f98ca9db-617c-3b21-7457-8488e3344881"
    assert fields["DeviceUniqueId"] == "2392fff8-65d8-4aff-b075-5214c8cfb56f"
    assert "DevId" not in fields


def test_account_auth_os_type_matches_runtime_platform_short_codes():
    assert normalize_account_auth_os_type("Android") == "A"
    assert normalize_account_auth_os_type("WindowsPlayer") == "W"
    assert normalize_account_auth_os_type("iPhonePlayer") == "I"

    fields = build_account_auth_fields(device_id="device-id", os_type="Android")
    assert fields["OSType"] == "A"
    assert fields["OSVersion"] == "Android OS 13 / API-33"


def test_account_auth_fields_include_explicit_dev_id_only():
    fields = build_account_auth_fields(device_id="device-id", dev_id="account-dev-id")

    assert fields["DeviceUniqueId"] == "device-id"
    assert fields["DevId"] == "account-dev-id"


def test_android_runtime_device_id_auto_prefers_uuid_over_uuid2():
    profile = AndroidRuntimeProfile(
        source_root="",
        external_dir="",
        shared_prefs_dir="",
        uuid="2392fff8-65d8-4aff-b075-5214c8cfb56f",
        uuid2="5f843fd4d0ac8615",
        save_uid="17 817 937",
        mid="2392fff8-65d8-4aff-b075-5214c8cfb56f",
        idfv="f98ca9db-617c-3b21-7457-8488e3344881",
    )

    assert select_android_runtime_device_id(profile, "auto") == "2392fff8-65d8-4aff-b075-5214c8cfb56f"


def test_android_security_state_records_missing_ngsx_side_effect():
    toy_login = ToySdkLoginResult(
        np_sn=123456789,
        np_token="game-token",
        npa_code="npa-code",
        session_token="",
        guid="123456789",
        member_id="abc",
        member_type="107",
        um_key="107:abc",
        game_token="game-token",
        callback=None,
    )
    credentials = build_credentials(toy_login, allow_empty_ngsm_token=True)
    state = build_android_security_state(credentials)

    assert state["security"] == "NgsX"
    assert state["status"] == "missing-ngsx-side-effect"
    assert state["requiredNativeSideEffect"]["nativeCall"] == "NgsX.Run(guid, npaCode)"
    assert state["requiredNativeSideEffect"]["args"] == {"guid": "123456789", "npaCode": "npa-code"}


def test_android_toysdk_npparams_header_is_encrypted_json():
    client = AndroidToySdkClient(
        device=AndroidDeviceProfile(
            country="TW",
            locale="zh-TW",
            uuid="uuid-a",
            uuid2="uuid-b",
            advertising_id="",
        )
    )
    headers = client._bolt_headers(guid="", np_token="", np_sn=0, encrypt_type="COMMON")
    decoded = toy_decrypt("COMMON", bytes.fromhex(headers["npparams"])).decode("utf-8")
    parsed = json.loads(decoded)
    assert parsed["svcID"] == "2079"
    assert parsed["sdkVer"] == "1.3.132"
    assert headers["uuid"] == "uuid-a"


def test_android_ticket_login_infers_npsn_from_guid():
    client = AndroidToySdkClient()
    session = client._session_from_login(
        {"errorCode": 0, "result": {"guid": "123456789", "npaCode": "npa", "umKey": "107:abc"}},
        existing=client.session,
    )
    assert session.np_sn == 123456789
    assert session.guid == "123456789"
    assert session.member_type == "107"
    assert session.member_id == "abc"


def test_android_web_token_ticket_issue_uses_ias_v2_http():
    class CapturingClient(AndroidToySdkClient):
        def _post_ias(self, path, body, *, headers=None):
            assert path == "/v2/issue/ticket/by-web-token"
            assert json.loads(body.decode("utf-8")) == {"gid": "2079"}
            assert headers == {"Content-Type": "application/json", "x-ias-web-token": "web-token"}
            return {"ticket": "ias:t:test"}

    result = CapturingClient().issue_ticket_by_web_token("web-token")
    assert result.ticket == "ias:t:test"
    assert result.callback.parsed == {"ticket": "ias:t:test"}


def test_android_nx_login_uses_sdk_user_id_field():
    class CapturingClient(AndroidToySdkClient):
        def _post_bolt_bytes(self, path, body, *, decrypt_type, credential, encrypt_type="COMMON"):
            decoded = toy_decrypt("COMMON", body).decode("utf-8")
            parsed = json.loads(decoded)
            assert path == "/sdk/signIn.nx"
            assert "userID" in parsed
            assert "user_id" not in parsed
            assert parsed["passwd"] == "<redacted>"
            return {"errorCode": 0, "result": {"guid": "123456789", "npaCode": "npa"}}

    client = CapturingClient()
    client.login_with_nx("not-email-id", "<redacted>")


def test_android_nx_login_preflight_get_nexon_sn():
    class CapturingClient(AndroidToySdkClient):
        def __init__(self):
            super().__init__()
            self.calls = []

        def enter_toy(self, *, mnc=None, mcc=None):
            self.calls.append("enter")
            return {"errorCode": 0}

        def _post_bolt_bytes(self, path, body, *, decrypt_type, credential, encrypt_type="COMMON"):
            decoded = toy_decrypt("COMMON", body).decode("utf-8")
            parsed = json.loads(decoded)
            self.calls.append(path)
            if path == "/sdk/getNexonSNByNXKLogin.nx":
                assert parsed["userID"] == "user@example.com"
                assert parsed["uuid"] == self.device.uuid
                assert parsed["optional"] == {}
                return {"errorCode": 0, "result": {"nexonSN": 123, "guid": "123"}}
            if path == "/sdk/signIn.nx":
                return {"errorCode": 0, "result": {"guid": "123456789", "npaCode": "npa"}}
            raise AssertionError(path)

        def get_user_info(self, *, mem_token="", session_token=""):
            self.calls.append("user")
            return {"errorCode": 0}

    client = CapturingClient()
    client.login_with_nx_flow("user@example.com", "pw")
    assert client.calls == ["enter", "/sdk/getNexonSNByNXKLogin.nx", "/sdk/signIn.nx", "user"]


def test_android_arena_login_uses_sha512_hex_password():
    class CapturingClient(AndroidToySdkClient):
        def _post_bolt_bytes(self, path, body, *, decrypt_type, credential, encrypt_type="COMMON"):
            decoded = toy_decrypt("COMMON", body).decode("utf-8")
            parsed = json.loads(decoded)
            assert path == "/sdk/signIn.nx"
            assert parsed["userID"] == "user@example.com"
            assert parsed["memType"] == LOGIN_TYPE_NXARENA
            assert parsed["passwd"] == hashlib.sha512(b"pw").hexdigest()
            assert parsed["optional"]["email"] == "user@example.com"
            return {"errorCode": 0, "result": {"guid": "123456789", "npaCode": "npa", "umKey": "107:abc"}}

    client = CapturingClient()
    client.login_with_nx("user@example.com", "pw", login_type=LOGIN_TYPE_NXARENA)


def test_android_nx_login_flow_auto_prefers_arena_when_membership_has_107_only():
    class CapturingClient(AndroidToySdkClient):
        def __init__(self):
            super().__init__()
            self.calls = []

        def enter_toy(self, *, mnc=None, mcc=None):
            self.calls.append("enter")
            self.available_login_types = [LOGIN_TYPE_NXARENA, 9999]
            return {"errorCode": 0, "result": {"service": {"useMemberships": [LOGIN_TYPE_NXARENA, 9999]}}}

        def get_nexon_sn_by_nx_login(self, user_id: str, password: str, *, cf_token: str = ""):
            self.calls.append("preflight")
            raise AssertionError("Arena auto mode should not call NXCom preflight")

        def _post_bolt_bytes(self, path, body, *, decrypt_type, credential, encrypt_type="COMMON"):
            decoded = toy_decrypt("COMMON", body).decode("utf-8")
            parsed = json.loads(decoded)
            self.calls.append(path)
            assert parsed["memType"] == LOGIN_TYPE_NXARENA
            assert parsed["passwd"] == hashlib.sha512(b"pw").hexdigest()
            return {"errorCode": 0, "result": {"guid": "123456789", "npaCode": "npa", "umKey": "107:abc"}}

        def get_user_info(self, *, mem_token="", session_token=""):
            self.calls.append("user")
            return {"errorCode": 0}

    client = CapturingClient()
    client.login_with_nx_flow("user@example.com", "pw", login_mode="auto")
    assert client.calls == ["enter", "/sdk/signIn.nx", "user"]


def test_android_nx_login_flow_auto_prefers_nxcom_when_membership_includes_1():
    class CapturingClient(AndroidToySdkClient):
        def __init__(self):
            super().__init__()
            self.calls = []

        def enter_toy(self, *, mnc=None, mcc=None):
            self.calls.append("enter")
            self.available_login_types = [LOGIN_TYPE_NXCOM, LOGIN_TYPE_NXARENA]
            return {"errorCode": 0, "result": {"service": {"useMemberships": [LOGIN_TYPE_NXCOM, LOGIN_TYPE_NXARENA]}}}

        def get_nexon_sn_by_nx_login(self, user_id: str, password: str, *, cf_token: str = ""):
            self.calls.append("preflight")
            return {"errorCode": 0, "result": {"nexonSN": 123, "guid": "123"}}

        def login_with_nx(self, user_id: str, password: str, *, login_type: int = LOGIN_TYPE_NXCOM, cf_token: str = "", cf_alt_token: str = ""):
            self.calls.append(f"sign:{login_type}")
            assert login_type == LOGIN_TYPE_NXCOM
            return self.session

    client = CapturingClient()
    client.login_with_nx_flow("user@example.com", "pw", login_mode="auto", get_user_info=False)
    assert client.calls == ["enter", "preflight", f"sign:{LOGIN_TYPE_NXCOM}"]


def test_android_nx_login_optional_turnstile_tokens():
    class CapturingClient(AndroidToySdkClient):
        def _post_bolt_bytes(self, path, body, *, decrypt_type, credential, encrypt_type="COMMON"):
            decoded = toy_decrypt("COMMON", body).decode("utf-8")
            parsed = json.loads(decoded)
            assert path == "/sdk/signIn.nx"
            assert parsed["optional"]["cfToken"] == "cf-token"
            assert parsed["optional"]["cfAltToken"] == "cf-alt"
            return {"errorCode": 0, "result": {"guid": "123456789", "npaCode": "npa"}}

    client = CapturingClient()
    client.login_with_nx("user@example.com", "pw", cf_token="cf-token", cf_alt_token="cf-alt")


def test_android_nx_login_raises_turnstile_required_and_extracts_alt_token():
    class CapturingClient(AndroidToySdkClient):
        def _post_bolt_bytes(self, path, body, *, decrypt_type, credential, encrypt_type="COMMON"):
            return {
                "errorCode": 2701,
                "errorText": "NeedTurnstileVerification",
                "result": {"cfAltToken": "cf-alt"},
            }

    client = CapturingClient()
    try:
        client.login_with_nx("user@example.com", "pw")
    except ToySdkAndroidTurnstileRequired as exc:
        assert exc.error_code == 2701
        assert exc.cf_alt_token == "cf-alt"
    else:
        raise AssertionError("ToySdkAndroidTurnstileRequired was not raised")


def test_android_get_user_info_does_not_send_np_token_as_mem_token():
    class CapturingClient(AndroidToySdkClient):
        def _post_bolt(self, path, body, *, encrypt_type, decrypt_type, credential):
            assert path == "/sdk/getUserInfo.nx"
            assert "memToken" not in body
            assert body == {"adid": ""}
            return {"errorCode": 0, "result": {"npSN": "123456789", "guid": "123456789"}}

    client = CapturingClient()
    client.session = client._session_from_login(
        {"errorCode": 0, "result": {"guid": "123456789", "npToken": "np-token"}},
        existing=client.session,
    )
    client.get_user_info()


def test_android_ticket_flow_uses_game_token_as_initial_np_token():
    class CapturingClient(AndroidToySdkClient):
        def __init__(self):
            super().__init__()
            self.calls = []

        def enter_toy(self, *, mnc=None, mcc=None):
            self.calls.append("enter")
            return {"errorCode": 0}

        def sign_in_with_ticket(self, ticket):
            self.calls.append("sign")
            self.session = self._session_from_login(
                {"errorCode": 0, "result": {"guid": "123456789", "npaCode": "npa", "umKey": "107:abc"}},
                existing=self.session,
            )
            return self.session

        def create_np_token(self):
            self.calls.append("create")
            self.session = self._session_from_login(
                {"errorCode": 0, "result": {"guid": "123456789", "npToken": "np-token"}},
                existing=self.session,
            )
            return {"errorCode": 0, "result": {"npToken": "np-token"}}

        def issue_game_token_by_ticket(self, ticket):
            self.calls.append("game")
            self.session = type(self.session)(
                np_sn=self.session.np_sn,
                guid=self.session.guid,
                np_token=self.session.np_token,
                npa_code=self.session.npa_code,
                session_token=self.session.session_token,
                um_key=self.session.um_key,
                member_id=self.session.member_id,
                member_type=self.session.member_type,
                game_token="game-token",
                session_np_token="game-token",
                raw_login=self.session.raw_login,
                raw_game_token={"game_token": "game-token"},
                raw_user_info=self.session.raw_user_info,
            )
            return "game-token"

        def get_user_info(self, *, mem_token="", session_token=""):
            self.calls.append("user")
            return {"errorCode": 0}

    client = CapturingClient()
    client.login_with_ticket_flow("ticket")
    assert client.calls == ["enter", "sign", "game", "user"]
    assert client.session.session_np_token == "game-token"
    assert client.session.to_toy_login_result().np_token == "game-token"


def test_build_credentials_can_explicitly_allow_empty_ngsm_token():
    toy_login = ToySdkLoginResult(
        np_sn=123456789,
        np_token="game-token",
        npa_code="npa-code",
        session_token="",
        guid="123456789",
        member_id="abc",
        member_type="107",
        um_key="107:abc",
        game_token="game-token",
        callback=None,
    )
    credentials = build_credentials(toy_login, allow_empty_ngsm_token=True)
    assert credentials.ngsm_token == ""


def test_build_credentials_uses_toy_login_ngsm_token():
    toy_login = ToySdkLoginResult(
        np_sn=123456789,
        np_token="game-token",
        npa_code="npa-code",
        session_token="",
        guid="123456789",
        member_id="abc",
        member_type="107",
        um_key="107:abc",
        game_token="game-token",
        ngsm_token="ngsm-token",
        callback=None,
    )
    credentials = build_credentials(toy_login)
    assert credentials.ngsm_token == "ngsm-token"


def test_ngsm_token_from_bridge_result_prefers_top_level():
    assert cli_main.ngsm_token_from_bridge_result(
        {"ngsmToken": "bridge-token", "events": [{"event": "ngsm-token", "ngsmToken": "event-token"}]}
    ) == "bridge-token"


def test_toy_login_from_file_loads_adjacent_bridge_ngsm_token(tmp_path):
    toy_login_path = tmp_path / "toy_login_summary.json"
    bridge_path = tmp_path / "ngsx_bridge_result.json"
    toy_login_path.write_text(
        json.dumps(
            {
                "npSN": 123456789,
                "npToken": "np-token",
                "npaCode": "npa-code",
                "guid": "123456789",
                "memberId": "73529028",
                "memberType": "107",
                "umKey": "107:73529028",
            }
        ),
        encoding="utf-8",
    )
    bridge_path.write_text(
        json.dumps(
            {
                "status": "ngsm-token",
                "events": [
                    {"event": "run-callback", "isOK": True, "code": 0},
                    {"event": "ngsm-token", "errorCode": 0, "ngsmToken": "bridge-ngsm-token"},
                ],
            }
        ),
        encoding="utf-8",
    )

    login = cli_main.toy_login_from_file(toy_login_path)
    assert login.ngsm_token == "bridge-ngsm-token"


def test_build_android_bridge_command_uses_explicit_device_settings(tmp_path):
    args = cli_main.build_arg_parser().parse_args([])
    args.gid = "2079"
    args.bridge_package = "com.nexon.bluearchive"
    args.bridge_device_id = "127.0.0.1:16448"
    args.bridge_adb_path = "E:/adb-tool/adb.exe"
    args.bridge_frida_address = ""
    args.bridge_pid = 8777
    args.bridge_timeout = 45.0
    args.bridge_attach_timeout = 12.0
    args.bridge_init_wait_ms = 7000
    args.bridge_no_init = True
    args.bridge_output = tmp_path / "ngsx_bridge_result.json"

    login = ToySdkLoginResult(
        np_sn=123456789,
        np_token="np-token",
        npa_code="0E50ZZZ10F02I",
        session_token="",
        guid="20790000000000000",
        member_id="73529028",
        member_type="107",
        um_key="107:73529028",
        callback=None,
    )
    command = cli_main.build_android_bridge_command(args, login, args.bridge_output)
    assert command[:2] == [sys.executable, str(cli_main.DEFAULT_NGSX_BRIDGE)]
    assert "--package" in command and "com.nexon.bluearchive" in command
    assert "--device-id" in command and "127.0.0.1:16448" in command
    assert "--adb-path" in command and "E:/adb-tool/adb.exe" in command
    assert "--pid" in command and "8777" in command
    assert "--guid" in command and "20790000000000000" in command
    assert "--npa-code" in command and "0E50ZZZ10F02I" in command
    assert "--no-init" in command


def test_build_pc_ngsx_bridge_command_defaults_to_init_run(tmp_path):
    args = cli_main.build_arg_parser().parse_args([])
    args.gid = "2079"
    args.pc_ngsx_dll = tmp_path / "grap64.dll"
    args.pc_ngsx_timeout = 9.0
    args.pc_ngsx_getversion_only = False
    args.pc_ngsx_no_init = False
    args.pc_ngsx_no_close = False

    login = ToySdkLoginResult(
        np_sn=123456789,
        np_token="np-token",
        npa_code="0E50ZZZ10F02I",
        session_token="",
        guid="20790000000000000",
        member_id="73529028",
        member_type="107",
        um_key="107:73529028",
        callback=None,
    )
    output = tmp_path / "ngsx_pc_bridge_result.json"
    command = cli_main.build_pc_ngsx_bridge_command(args, login, output)
    assert command[:2] == [sys.executable, str(cli_main.DEFAULT_NGSX_PC_PROBE)]
    assert "--dll" in command and str(args.pc_ngsx_dll) in command
    assert "--guid" in command and "20790000000000000" in command
    assert "--npa-code" in command and "0E50ZZZ10F02I" in command
    assert "--init" in command
    assert "--run" in command
    assert "--no-close" not in command


def test_build_pc_ngsx_bridge_command_can_getversion_only(tmp_path):
    args = cli_main.build_arg_parser().parse_args([])
    args.gid = "2079"
    args.pc_ngsx_dll = tmp_path / "grap64.dll"
    args.pc_ngsx_timeout = 9.0
    args.pc_ngsx_getversion_only = True
    args.pc_ngsx_no_init = False
    args.pc_ngsx_no_close = False

    login = ToySdkLoginResult(
        np_sn=123456789,
        np_token="np-token",
        npa_code="",
        session_token="",
        guid="",
        member_id="73529028",
        member_type="107",
        um_key="107:73529028",
        callback=None,
    )
    command = cli_main.build_pc_ngsx_bridge_command(args, login, tmp_path / "ngsx_pc_bridge_result.json")
    assert "--run" not in command
    assert "--init" not in command
    assert "--guid" not in command
    assert "--npa-code" not in command


def test_toy_login_from_file_loads_adjacent_pc_bridge_ngsm_token(tmp_path):
    toy_login_path = tmp_path / "toy_login_summary.json"
    bridge_path = tmp_path / "ngsx_pc_bridge_result.json"
    toy_login_path.write_text(
        json.dumps(
            {
                "npSN": 123456789,
                "npToken": "np-token",
                "npaCode": "npa-code",
                "guid": "123456789",
                "memberId": "73529028",
                "memberType": "107",
                "umKey": "107:73529028",
            }
        ),
        encoding="utf-8",
    )
    bridge_path.write_text(json.dumps({"ngsmToken": "pc-ngsm-token"}), encoding="utf-8")

    login = cli_main.toy_login_from_file(toy_login_path)
    assert login.ngsm_token == "pc-ngsm-token"


if __name__ == "__main__":
    test_protocol_converter_sample()
    test_fast_crc_check_value()
    test_create_hash_high_bits()
    test_packet_layout_and_roundtrip()
    test_packet_can_encrypt_request_payload_like_pc_session_lane()
    test_pc_post_account_check_request_lengths_match_dynamic_capture()
    test_account_check_nexon_stays_unencrypted_even_with_carried_crypto()
    test_besthttp_multipart_binary_body()
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as d:
        test_runtime_hosts_gateway_discovery(Path(d))
    with TemporaryDirectory() as d:
        test_region_profiles_and_fallback(Path(d))
    test_proxy_normalization_and_maps()
    test_client_splits_gateway_and_api_urls()
    test_gateway_wrapper_plain_error_packet_is_not_aes_decrypted()
    test_android_toysdk_common_and_npsn_crypto_roundtrip()
    test_android_toysdk_headers_are_latin1_safe()
    test_account_check_nexon_key_iv_fields_are_rsa_encrypted()
    test_account_check_nexon_key_iv_diagnostic_modes()
    test_account_check_nexon_android_minimal_fields()
    test_account_auth_fields_include_runtime_adid_and_idfv()
    test_account_auth_fields_include_explicit_dev_id_only()
    test_android_toysdk_npparams_header_is_encrypted_json()
    test_android_ticket_login_infers_npsn_from_guid()
    test_android_web_token_ticket_issue_uses_ias_v2_http()
    test_android_nx_login_uses_sdk_user_id_field()
    test_android_get_user_info_does_not_send_np_token_as_mem_token()
    test_android_ticket_flow_uses_game_token_as_initial_np_token()
    test_build_credentials_can_explicitly_allow_empty_ngsm_token()
    test_build_credentials_uses_toy_login_ngsm_token()
    test_ngsm_token_from_bridge_result_prefers_top_level()
    with TemporaryDirectory() as d:
        test_toy_login_from_file_loads_adjacent_bridge_ngsm_token(Path(d))
    with TemporaryDirectory() as d:
        test_build_android_bridge_command_uses_explicit_device_settings(Path(d))
    with TemporaryDirectory() as d:
        test_build_pc_ngsx_bridge_command_defaults_to_init_run(Path(d))
    with TemporaryDirectory() as d:
        test_build_pc_ngsx_bridge_command_can_getversion_only(Path(d))
    with TemporaryDirectory() as d:
        test_toy_login_from_file_loads_adjacent_pc_bridge_ngsm_token(Path(d))
    print("test_ba_replay ok")

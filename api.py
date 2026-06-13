"""headless-bluearchive public Python API."""

from core.client import BAReplayClient, GatewayResponse, decode_gateway_response
from core.crypto import (
    account_check_nexon_key_iv_fields,
    account_check_nexon_rsa_encrypt_base64,
    decrypt_response_base64,
    encrypt_response_json,
    fast_crc,
    generated_key_iv_fields,
    generate_aes128_key_iv,
    gzip_length_prefixed,
    ungzip_length_prefixed,
    xor_crypt,
)
from core.packet import PacketMeta, ParsedPacket, build_packet, create_hash, parse_packet
from core.protocol import protocol_value, request_protocol, type_conversion
from modules.auth.flows import IntegratedLoginOptions, IntegratedLoginResult, ToyLoginOverrides, run_web_to_game_login
from modules.auth.login import LoginReplay
from modules.auth.nexon_login import (
    NexonGameCredentials,
    build_account_auth_fields,
    build_account_check_nexon_fields,
    build_credentials,
    build_queuing_get_ticket_fields,
    run_main_game_login,
)
from modules.auth.nexon_web import WebLoginTokens, load_latest_tokens, run_playwright_web_login
from modules.auth.proof_token import proof_token_hash, proof_token_search_span, solve_proof_token
from modules.auth.toysdk_android import AndroidDeviceProfile, AndroidToyConfig, AndroidToySdkClient, AndroidToySession
from modules.auth.toysdk_models import NativeCallbackResult, ToySdkLoginResult, ToySdkTicketResult
from modules.runtime.android_runtime_profile import (
    AndroidRuntimeProfile,
    load_android_runtime_profile,
    select_android_runtime_device_id,
)
from modules.runtime.region_config import ServerProfile, build_login_url, list_profiles, profile_for
from modules.runtime.runtime_config import (
    DEFAULT_NXINFACE_CONFIG_PATH,
    NxInfaceConfigInfo,
    NxInfaceTokenInfo,
    PcRuntimeProfile,
    RuntimeConnectionInfo,
    discover_connection_info,
    discover_nxinface_config,
    discover_pc_runtime_profile,
)
from utils.proxy import apply_proxy_env, normalize_proxy_url, playwright_proxy_options, requests_proxy_map

__all__ = [
    "BAReplayClient",
    "AndroidDeviceProfile",
    "AndroidToyConfig",
    "AndroidToySdkClient",
    "AndroidToySession",
    "AndroidRuntimeProfile",
    "GatewayResponse",
    "IntegratedLoginOptions",
    "IntegratedLoginResult",
    "LoginReplay",
    "NativeCallbackResult",
    "NexonGameCredentials",
    "NxInfaceConfigInfo",
    "NxInfaceTokenInfo",
    "PacketMeta",
    "ParsedPacket",
    "PcRuntimeProfile",
    "RuntimeConnectionInfo",
    "ServerProfile",
    "ToyLoginOverrides",
    "ToySdkLoginResult",
    "ToySdkTicketResult",
    "WebLoginTokens",
    "apply_proxy_env",
    "account_check_nexon_key_iv_fields",
    "account_check_nexon_rsa_encrypt_base64",
    "build_account_auth_fields",
    "build_account_check_nexon_fields",
    "build_credentials",
    "build_login_url",
    "build_packet",
    "build_queuing_get_ticket_fields",
    "create_hash",
    "decode_gateway_response",
    "decrypt_response_base64",
    "DEFAULT_NXINFACE_CONFIG_PATH",
    "discover_connection_info",
    "discover_nxinface_config",
    "discover_pc_runtime_profile",
    "encrypt_response_json",
    "fast_crc",
    "generate_aes128_key_iv",
    "generated_key_iv_fields",
    "gzip_length_prefixed",
    "list_profiles",
    "load_android_runtime_profile",
    "load_latest_tokens",
    "normalize_proxy_url",
    "parse_packet",
    "playwright_proxy_options",
    "profile_for",
    "proof_token_hash",
    "proof_token_search_span",
    "protocol_value",
    "request_protocol",
    "requests_proxy_map",
    "run_main_game_login",
    "run_playwright_web_login",
    "run_web_to_game_login",
    "select_android_runtime_device_id",
    "solve_proof_token",
    "type_conversion",
    "ungzip_length_prefixed",
    "xor_crypt",
]

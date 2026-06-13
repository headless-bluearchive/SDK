from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api import BAReplayClient, decode_gateway_response, generated_key_iv_fields, parse_packet, type_conversion
from core.crypto import decrypt_response_base64, encrypt_response_json, fast_crc
from core.packet import create_hash


def main() -> int:
    assert type_conversion(4, 37000) == 0x21BA2799
    assert fast_crc(b"123456789") == 0x89A1897F
    assert create_hash(1002, counter=7) == (1002 << 32) | 7

    client = BAReplayClient(
        session_key={"AccountServerId": 1, "MxToken": "tok"},
        aes_encrypted_key=b"ek",
        aes_encrypted_iv=b"iv",
    )
    built = client.build(
        "AccountAuthRequest",
        {"Version": 1, "DevId": "dev", "MarketId": "m"},
        counter=9,
    )
    parsed = parse_packet(built.packet)
    decoded = json.loads(parsed.request_bytes.decode("utf-8"))
    assert decoded["Protocol"] == 1002
    assert decoded["SessionKey"]["MxToken"] == "tok"
    assert decoded["Hash"] == (1002 << 32) | 9
    assert decoded["DevId"] == "dev"

    queue_req = client.build(
        "QueuingGetCryptoKeysRequest",
        {"ClientGeneratedKey": b"1234567890abcdef", "ClientGeneratedIV": b"fedcba0987654321"},
        counter=10,
    )
    queue_decoded = json.loads(parse_packet(queue_req.packet).request_bytes.decode("utf-8"))
    assert queue_decoded["Protocol"] == 50001
    assert queue_decoded["ClientGeneratedKey"] == "MTIzNDU2Nzg5MGFiY2RlZg=="
    generated_fields, generated_key, generated_iv = generated_key_iv_fields()
    assert len(generated_key) == 16
    assert len(generated_iv) == 16
    assert set(generated_fields) == {"ClientGeneratedKey", "ClientGeneratedIV"}

    key = bytes.fromhex("00112233445566778899aabbccddeeff")
    iv = bytes.fromhex("0102030405060708090a0b0c0d0e0f10")
    encrypted = encrypt_response_json(key, iv, '{"ok":true}')
    assert decrypt_response_base64(key, iv, encrypted) == '{"ok":true}'
    wrapped_packet = '{"protocol":"Account_Auth","packet":"' + encrypted + '"}'
    assert decode_gateway_response(wrapped_packet, aes_key=key, aes_iv=iv).payload == '{"ok":true}'
    encrypted_wrapper = encrypt_response_json(key, iv, '{"protocol":"Account_Auth","packet":"{\\"ok\\":true}"}')
    assert decode_gateway_response(encrypted_wrapper, aes_key=key, aes_iv=iv).payload == '{"ok":true}'

    print("ba_replay verification ok")
    print(f"sample packet: protocol={built.meta.protocol_name} crc=0x{built.meta.crc:08X} bucket={built.meta.bucket}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

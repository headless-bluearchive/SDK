
from __future__ import annotations

import itertools
import json
import struct
import base64
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Mapping

from core.crypto import aes_cbc_pkcs7_encrypt, fast_crc, gzip_length_prefixed, ungzip_length_prefixed, xor_crypt
from core.protocol import protocol_name, protocol_value, type_conversion


PROTOCOL_HEAD_RESERVE = 0x0A
_hash_counter = itertools.count(1)


@dataclass(frozen=True)
class PacketMeta:
    protocol: int
    protocol_name: str
    crc: int
    bucket: int
    converted_protocol: int
    aes_encrypted_key_len: int
    aes_encrypted_iv_len: int
    payload_len: int
    request_hash: int | None = None
    request_payload_encrypted: bool = False
    serialized_request_len: int = 0
    request_bytes_len: int = 0


@dataclass(frozen=True)
class ParsedPacket:
    meta: PacketMeta
    aes_encrypted_key: bytes
    aes_encrypted_iv: bytes
    payload: bytes
    compressed_payload: bytes
    request_bytes: bytes


def create_hash(protocol: int | str, counter: int | None = None) -> int:

    proto = protocol_value(protocol) & 0xFFFFFFFF
    if counter is None:
        counter = next(_hash_counter)
    return ((proto << 32) | (counter & 0xFFFFFFFF)) & 0xFFFFFFFFFFFFFFFF


def serialize_request(
    fields: Mapping[str, Any] | bytes | bytearray | str,
    *,
    protocol: int | str | None = None,
    inject_hash: bool = True,
    session_key: Mapping[str, Any] | None = None,
    include_base_defaults: bool = False,
    include_protocol_field: bool = True,
    omit_none: bool = True,
    counter: int | None = None,
) -> tuple[bytes, int | None]:

    if isinstance(fields, bytes):
        return fields, None
    if isinstance(fields, bytearray):
        return bytes(fields), None
    if isinstance(fields, str):
        return fields.encode("utf-8"), None

    obj: OrderedDict[str, Any] = OrderedDict()
    if include_protocol_field and protocol is not None and "Protocol" not in fields:
        obj["Protocol"] = protocol_value(protocol)
    if session_key is not None and "SessionKey" not in fields:
        obj["SessionKey"] = _jsonable(dict(session_key))

    request_hash: int | None = None
    if inject_hash:
        if protocol is None:
            raise ValueError("protocol is required when inject_hash=True")
        request_hash = int(fields.get("Hash", create_hash(protocol, counter)))
        obj["Hash"] = request_hash

    if include_base_defaults:
        if "AccountId" not in obj and session_key and "AccountServerId" in session_key:
            obj["AccountId"] = session_key["AccountServerId"]
        obj.setdefault("Resendable", bool(fields.get("Resendable", True)))
        obj.setdefault("IsTest", bool(fields.get("IsTest", False)))

    for key, value in fields.items():
        if key not in obj:
            if not (omit_none and value is None):
                obj[key] = _jsonable(value)

    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return text.encode("utf-8"), request_hash


def _jsonable(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray, memoryview)):
        return base64.b64encode(bytes(value)).decode("ascii")
    if isinstance(value, Mapping):
        return OrderedDict((str(k), _jsonable(v)) for k, v in value.items())
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def build_packet(
    protocol: int | str,
    request: Mapping[str, Any] | bytes | bytearray | str,
    *,
    aes_encrypted_key: bytes = b"",
    aes_encrypted_iv: bytes = b"",
    session_key: Mapping[str, Any] | None = None,
    inject_hash: bool = True,
    include_base_defaults: bool = False,
    include_protocol_field: bool = True,
    omit_none: bool = True,
    counter: int | None = None,
    gzip_level: int = 1,
    gzip_mtime: int | None = 0,
    request_aes_key: bytes | None = None,
    request_aes_iv: bytes | None = None,
    encrypt_request: bool | None = None,
) -> tuple[bytes, PacketMeta, bytes]:

    packet, meta, request_bytes, _serialized_request_bytes = build_packet_detailed(
        protocol,
        request,
        aes_encrypted_key=aes_encrypted_key,
        aes_encrypted_iv=aes_encrypted_iv,
        session_key=session_key,
        inject_hash=inject_hash,
        include_base_defaults=include_base_defaults,
        include_protocol_field=include_protocol_field,
        omit_none=omit_none,
        counter=counter,
        gzip_level=gzip_level,
        gzip_mtime=gzip_mtime,
        request_aes_key=request_aes_key,
        request_aes_iv=request_aes_iv,
        encrypt_request=encrypt_request,
    )
    return packet, meta, request_bytes


def build_packet_detailed(
    protocol: int | str,
    request: Mapping[str, Any] | bytes | bytearray | str,
    *,
    aes_encrypted_key: bytes = b"",
    aes_encrypted_iv: bytes = b"",
    session_key: Mapping[str, Any] | None = None,
    inject_hash: bool = True,
    include_base_defaults: bool = False,
    include_protocol_field: bool = True,
    omit_none: bool = True,
    counter: int | None = None,
    gzip_level: int = 1,
    gzip_mtime: int | None = 0,
    request_aes_key: bytes | None = None,
    request_aes_iv: bytes | None = None,
    encrypt_request: bool | None = None,
) -> tuple[bytes, PacketMeta, bytes, bytes]:

    proto = protocol_value(protocol)
    serialized_request_bytes, request_hash = serialize_request(
        request,
        protocol=proto,
        inject_hash=inject_hash,
        session_key=session_key,
        include_base_defaults=include_base_defaults,
        include_protocol_field=include_protocol_field,
        omit_none=omit_none,
        counter=counter,
    )
    if len(aes_encrypted_key) > 0xFF or len(aes_encrypted_iv) > 0xFF:
        raise ValueError("aes encrypted key/iv blobs must each fit in one byte length")

    should_encrypt_request = _should_encrypt_request(
        encrypt_request=encrypt_request,
        request_aes_key=request_aes_key,
        request_aes_iv=request_aes_iv,
        aes_encrypted_key=aes_encrypted_key,
        aes_encrypted_iv=aes_encrypted_iv,
    )
    if should_encrypt_request:
        if request_aes_key is None or request_aes_iv is None:
            raise ValueError("request AES key/iv are required when encrypt_request=True")
        request_bytes = aes_cbc_pkcs7_encrypt(serialized_request_bytes, request_aes_key, request_aes_iv)
    else:
        request_bytes = serialized_request_bytes

    compressed = gzip_length_prefixed(request_bytes, compresslevel=gzip_level, mtime=gzip_mtime)
    payload = xor_crypt(compressed)
    crc = fast_crc(payload)
    converted = type_conversion(crc, proto)
    packet = b"".join(
        (
            struct.pack("<I", crc),
            struct.pack("<i", converted),
            struct.pack("<B", len(aes_encrypted_key)),
            struct.pack("<B", len(aes_encrypted_iv)),
            bytes(aes_encrypted_key),
            bytes(aes_encrypted_iv),
            payload,
        )
    )
    meta = PacketMeta(
        protocol=proto,
        protocol_name=protocol_name(proto),
        crc=crc,
        bucket=crc % 99,
        converted_protocol=converted,
        aes_encrypted_key_len=len(aes_encrypted_key),
        aes_encrypted_iv_len=len(aes_encrypted_iv),
        payload_len=len(payload),
        request_hash=request_hash,
        request_payload_encrypted=should_encrypt_request,
        serialized_request_len=len(serialized_request_bytes),
        request_bytes_len=len(request_bytes),
    )
    return packet, meta, request_bytes, serialized_request_bytes


def _should_encrypt_request(
    *,
    encrypt_request: bool | None,
    request_aes_key: bytes | None,
    request_aes_iv: bytes | None,
    aes_encrypted_key: bytes,
    aes_encrypted_iv: bytes,
) -> bool:
    if encrypt_request is not None:
        return bool(encrypt_request)
    return bool(request_aes_key and request_aes_iv and aes_encrypted_key and aes_encrypted_iv)


def parse_packet(packet: bytes) -> ParsedPacket:
    if len(packet) < PROTOCOL_HEAD_RESERVE:
        raise ValueError("packet shorter than 10-byte header")
    crc, converted = struct.unpack_from("<Ii", packet, 0)
    key_len = packet[8]
    iv_len = packet[9]
    offset = PROTOCOL_HEAD_RESERVE
    end_key = offset + key_len
    end_iv = end_key + iv_len
    if end_iv > len(packet):
        raise ValueError("packet key/iv lengths exceed packet length")
    key_blob = packet[offset:end_key]
    iv_blob = packet[end_key:end_iv]
    payload = packet[end_iv:]
    computed_crc = fast_crc(payload)
    if computed_crc != crc:
        raise ValueError(f"CRC mismatch: header=0x{crc:08x}, computed=0x{computed_crc:08x}")
    compressed = xor_crypt(payload)
    request_bytes = ungzip_length_prefixed(compressed)
    meta = PacketMeta(
        protocol=0,
        protocol_name="",
        crc=crc,
        bucket=crc % 99,
        converted_protocol=converted,
        aes_encrypted_key_len=key_len,
        aes_encrypted_iv_len=iv_len,
        payload_len=len(payload),
        request_hash=None,
    )
    return ParsedPacket(meta, key_blob, iv_blob, payload, compressed, request_bytes)

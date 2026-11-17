from __future__ import annotations

import base64
import gzip
import io
import os
import struct
import zlib
from functools import lru_cache


CRC_POLY = 0x04C11DB7
CRC_HIGH_BIT = 0x80000000
XOR_KEY = 0xAFB7E3D9
XOR_BYTE = XOR_KEY & 0xFF
# Global client 1.96.474931: RSA-4096, OAEP-SHA1 (raw AES key/IV).
ACCOUNT_CHECK_NEXON_RSA_PUBLIC_KEY_PEM = (
    b'-----BEGIN PUBLIC KEY-----\n'
    b'MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAz1oODtVINPQsTIbFDiL2\n'
    b'IIj3YqDGxZ1WqJWfJrpo7ZqdnSIMXaVqVyM07Zguc9wczPrluDNowheP8NXe8uTR\n'
    b'prO7jpF9bOcrrit9Xyxf57NA5rIMqOj6/XgWzzptvvt3oUrOQJRTvEjusQCX79Ds\n'
    b'fhhbPRfdPzZUOPYa49MM385Z05ndNiTB9/yhxP5+5zm7TS3f6/o1Ntw9yXoRYmgR\n'
    b'8+JYGL6TpqtZHkqPTp6kIJrnsLyT1wRteh3oQKJaze0CM0DUUzFiqieRE8c8JAoV\n'
    b'jk/yRQUqVMoKbdpINYlWhF+GFE/ccSpqQymepHxfR0alspynqJwJgODCeHtwuno5\n'
    b'HEOwdbA8NanLVnE9qlvdeNkbODdt/XTHKOaXx+SUMHezUY0rEXp8WMim0i9IQTGa\n'
    b'YWeW25RjXIZswKdg0gLRJXYZXUgF3nVcqr0hi4kv1pgrFPsjI7yIThxLY0UfomkR\n'
    b'oe6sSBBtQUDI85s+1pZRcl8xygxOxMfFSk5RB3EntFmcf/AKaLYQbXN9RxgrvqRS\n'
    b'9koBBEnnrIN0zXDBioZUDOWVBeBZwAydpPGKu2mkqu3BI/Al92noEHc6fmkG5+Qm\n'
    b'b237xSh1DFbbQO6lxg4ABdsqgvZskYS+7BcQPjs1z2zftrnesFkqD7BhbqXUBuDY\n'
    b'D80B8Be5I483qSSy8DsW458CAwEAAQ==\n'
    b'-----END PUBLIC KEY-----'
)


@lru_cache(maxsize=1)
def _crc_table() -> tuple[int, ...]:
    table: list[int] = []
    for index in range(256):
        crc = (index << 24) & 0xFFFFFFFF
        for _ in range(8):
            if crc & CRC_HIGH_BIT:
                crc = ((crc << 1) ^ CRC_POLY) & 0xFFFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFFFF
        table.append(crc)
    return tuple(table)


def fast_crc(data: bytes | bytearray | memoryview, offset: int = 0, length: int | None = None) -> int:

    view = memoryview(data)
    if offset < 0:
        raise ValueError("offset must be >= 0")
    if length is None:
        end = len(view)
    else:
        if length < 0:
            raise ValueError("length must be >= 0")
        end = offset + length
    if end > len(view):
        raise ValueError("offset + length exceeds input length")

    table = _crc_table()
    crc = 0
    for b in view[offset:end]:
        crc = (((crc << 8) & 0xFFFFFFFF) ^ table[((crc >> 24) ^ b) & 0xFF]) & 0xFFFFFFFF
    return crc


def xor_crypt(data: bytes | bytearray | memoryview, key_byte: int = XOR_BYTE) -> bytes:

    key_byte &= 0xFF
    return bytes((b ^ key_byte) for b in bytes(data))


def xor_crypt_inplace(data: bytearray, key_byte: int = XOR_BYTE) -> bytearray:
    key_byte &= 0xFF
    for i, b in enumerate(data):
        data[i] = b ^ key_byte
    return data


def gzip_bytes(data: bytes, *, compresslevel: int = 1, mtime: int | None = 0) -> bytes:

    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb", compresslevel=compresslevel, mtime=mtime) as gz:
        gz.write(data)
    return out.getvalue()


def gzip_length_prefixed(data: bytes, *, compresslevel: int = 1, mtime: int | None = 0) -> bytes:

    if len(data) > 0x7FFFFFFF:
        raise ValueError("request body too large for signed int32 length prefix")
    return struct.pack("<i", len(data)) + gzip_bytes(data, compresslevel=compresslevel, mtime=mtime)


def _try_decompress_gzip_zlib_raw(payload: bytes) -> bytes:
    errors: list[Exception] = []
    for func in (
        gzip.decompress,
        lambda b: zlib.decompress(b),
        lambda b: zlib.decompress(b, -zlib.MAX_WBITS),
    ):
        try:
            return func(payload)
        except Exception as exc:
            errors.append(exc)
    raise ValueError(f"unable to decompress payload; tried gzip, zlib, raw deflate: {errors!r}")


def ungzip_length_prefixed(data: bytes) -> bytes:

    if len(data) < 4:
        raise ValueError("compressed payload is shorter than the 4-byte length prefix")
    expected_len = struct.unpack_from("<i", data, 0)[0]
    if expected_len < 0:
        raise ValueError(f"negative original length prefix: {expected_len}")
    plain = _try_decompress_gzip_zlib_raw(data[4:])
    if len(plain) != expected_len:
        raise ValueError(f"decompressed length mismatch: expected {expected_len}, got {len(plain)}")
    return plain


def _pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes:
    if not data or len(data) % block_size:
        raise ValueError("invalid PKCS7 padded data length")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("invalid PKCS7 padding length")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("invalid PKCS7 padding bytes")
    return data[:-pad_len]


def _pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len]) * pad_len


def aes_cbc_pkcs7_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    if len(iv) != 16:
        raise ValueError("AES-CBC IV must be 16 bytes")
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except Exception:
        from Crypto.Cipher import AES

        return _pkcs7_unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ciphertext))

    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    return _pkcs7_unpad(decryptor.update(ciphertext) + decryptor.finalize())


def aes_cbc_pkcs7_encrypt(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    if len(iv) != 16:
        raise ValueError("AES-CBC IV must be 16 bytes")
    padded = _pkcs7_pad(plaintext)
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except Exception:
        from Crypto.Cipher import AES

        return AES.new(key, AES.MODE_CBC, iv).encrypt(padded)

    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return encryptor.update(padded) + encryptor.finalize()


def decrypt_response_base64(aes_key: bytes | None, aes_iv: bytes | None, encrypted_base64: str) -> str:

    if not aes_key or not aes_iv:
        return encrypted_base64
    ciphertext = base64.b64decode(encrypted_base64)
    return aes_cbc_pkcs7_decrypt(ciphertext, aes_key, aes_iv).decode("utf-8")


def decode_sqlcipher_material(
    encrypted_sqlcipher_key: str,
    encrypted_sqlcipher_license: str,
    *,
    aes_key: bytes,
    aes_iv: bytes,
) -> tuple[bytes, str]:
    sql_key_b64 = decrypt_response_base64(aes_key, aes_iv, encrypted_sqlcipher_key)
    license_code = decrypt_response_base64(aes_key, aes_iv, encrypted_sqlcipher_license)
    return base64.b64decode(sql_key_b64), license_code


def encrypt_response_json(aes_key: bytes, aes_iv: bytes, plaintext_json: str | bytes) -> str:
    if isinstance(plaintext_json, str):
        plaintext_json = plaintext_json.encode("utf-8")
    return base64.b64encode(aes_cbc_pkcs7_encrypt(plaintext_json, aes_key, aes_iv)).decode("ascii")


def decode_bytes(value: bytes | bytearray | memoryview | str | None, *, encoding: str = "hex") -> bytes:

    if value is None:
        return b""
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value)
    text = value.strip()
    if not text:
        return b""
    if encoding == "base64":
        return base64.b64decode(text)
    if encoding == "auto":
        try:
            return bytes.fromhex(text)
        except ValueError:
            return base64.b64decode(text)
    if encoding == "utf8":
        return text.encode("utf-8")
    return bytes.fromhex(text)


def generate_aes128_key_iv() -> tuple[bytes, bytes]:

    return os.urandom(16), os.urandom(16)


@lru_cache(maxsize=1)
def _account_check_nexon_rsa_public_key():
    try:
        from cryptography.hazmat.primitives import serialization
    except Exception:
        from Crypto.PublicKey import RSA

        return RSA.import_key(ACCOUNT_CHECK_NEXON_RSA_PUBLIC_KEY_PEM)

    return serialization.load_pem_public_key(ACCOUNT_CHECK_NEXON_RSA_PUBLIC_KEY_PEM)


def account_check_nexon_rsa_encrypt_base64(
    data: bytes | bytearray | memoryview,
    *,
    padding_mode: str = "oaep-sha1",
) -> str:

    raw = bytes(data)
    normalized_padding = padding_mode.strip().lower().replace("_", "-")
    try:
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import hashes
    except Exception:
        from Crypto.Cipher import PKCS1_v1_5
        from Crypto.Cipher import PKCS1_OAEP
        from Crypto.Hash import SHA1, SHA256

        public_key = _account_check_nexon_rsa_public_key()
        if normalized_padding in ("pkcs1", "pkcs1v15", "pkcs1-v1.5"):
            encrypted = PKCS1_v1_5.new(public_key).encrypt(raw)
        elif normalized_padding in ("oaep", "oaep-sha1"):
            encrypted = PKCS1_OAEP.new(public_key, hashAlgo=SHA1).encrypt(raw)
        elif normalized_padding == "oaep-sha256":
            encrypted = PKCS1_OAEP.new(public_key, hashAlgo=SHA256).encrypt(raw)
        else:
            raise ValueError("unsupported RSA padding mode")
        return base64.b64encode(encrypted).decode("ascii")

    if normalized_padding in ("pkcs1", "pkcs1v15", "pkcs1-v1.5"):
        rsa_padding = padding.PKCS1v15()
    elif normalized_padding in ("oaep", "oaep-sha1"):
        rsa_padding = padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None,
        )
    elif normalized_padding == "oaep-sha256":
        rsa_padding = padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
    else:
        raise ValueError("unsupported RSA padding mode")
    encrypted = _account_check_nexon_rsa_public_key().encrypt(raw, rsa_padding)
    return base64.b64encode(encrypted).decode("ascii")


def generated_key_iv_fields(key: bytes | None = None, iv: bytes | None = None) -> tuple[dict[str, str], bytes, bytes]:

    if key is None or iv is None:
        generated_key, generated_iv = generate_aes128_key_iv()
        key = generated_key if key is None else key
        iv = generated_iv if iv is None else iv
    if len(key) != 16 or len(iv) != 16:
        raise ValueError("client generated key and IV must both be 16 bytes")
    fields = {
        "ClientGeneratedKey": base64.b64encode(key).decode("ascii"),
        "ClientGeneratedIV": base64.b64encode(iv).decode("ascii"),
    }
    return fields, key, iv


def account_check_nexon_key_iv_fields(
    key: bytes | None = None,
    iv: bytes | None = None,
    *,
    mode: str = "rsa-raw",
) -> tuple[dict[str, str], bytes, bytes]:

    if key is None or iv is None:
        generated_key, generated_iv = generate_aes128_key_iv()
        key = generated_key if key is None else key
        iv = generated_iv if iv is None else iv
    if len(key) != 16 or len(iv) != 16:
        raise ValueError("client generated key and IV must both be 16 bytes")
    normalized_mode = mode.strip().lower()
    if normalized_mode in ("rsa-raw", "rsa-oaep-sha1"):
        fields = {
            "ClientGeneratedKey": account_check_nexon_rsa_encrypt_base64(key, padding_mode="oaep-sha1"),
            "ClientGeneratedIV": account_check_nexon_rsa_encrypt_base64(iv, padding_mode="oaep-sha1"),
        }
    elif normalized_mode in ("rsa-pkcs1", "rsa-pkcs1v15", "rsa-pkcs1-v1.5"):
        fields = {
            "ClientGeneratedKey": account_check_nexon_rsa_encrypt_base64(key, padding_mode="pkcs1"),
            "ClientGeneratedIV": account_check_nexon_rsa_encrypt_base64(iv, padding_mode="pkcs1"),
        }
    elif normalized_mode == "rsa-oaep-sha256":
        fields = {
            "ClientGeneratedKey": account_check_nexon_rsa_encrypt_base64(key, padding_mode="oaep-sha256"),
            "ClientGeneratedIV": account_check_nexon_rsa_encrypt_base64(iv, padding_mode="oaep-sha256"),
        }
    elif normalized_mode == "raw-base64":
        fields = {
            "ClientGeneratedKey": base64.b64encode(key).decode("ascii"),
            "ClientGeneratedIV": base64.b64encode(iv).decode("ascii"),
        }
    elif normalized_mode == "rsa-base64-text":
        fields = {
            "ClientGeneratedKey": account_check_nexon_rsa_encrypt_base64(base64.b64encode(key)),
            "ClientGeneratedIV": account_check_nexon_rsa_encrypt_base64(base64.b64encode(iv)),
        }
    elif normalized_mode == "rsa-hex-text":
        fields = {
            "ClientGeneratedKey": account_check_nexon_rsa_encrypt_base64(key.hex().encode("ascii")),
            "ClientGeneratedIV": account_check_nexon_rsa_encrypt_base64(iv.hex().encode("ascii")),
        }
    else:
        raise ValueError(
            "unsupported Account_CheckNexon key mode; "
            "expected rsa-oaep-sha1, rsa-pkcs1, raw-base64, rsa-base64-text, or rsa-hex-text"
        )
    return fields, key, iv

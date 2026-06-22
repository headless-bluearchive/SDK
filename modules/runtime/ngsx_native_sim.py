from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Mapping

from modules.runtime.ngsm_token import generate_ngsm_token, with_ngsm_fingerprint_defaults


def simulate_ngsx_native_run(payload: Mapping[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    simulation = build_ngsx_native_simulation(payload, now=now)
    return {
        "ok": True,
        "status": "native-sim",
        "code": 0,
        "message": "pure-static-native-sim",
        "ngsmTokenPresent": bool(simulation["request"].get("ngsm_token", "")),
    }


def build_ngsx_native_simulation(payload: Mapping[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    request = dict(payload or {})
    device = _mapping(request.get("device"))
    issued_at = now or datetime.now(timezone.utc)
    issued_at_iso = issued_at.isoformat().replace("+00:00", "Z")
    issued_at_ms = int(issued_at.timestamp() * 1000)

    service_id = _text(request.get("service_id"))
    package_name = _text(request.get("package_name")) or _text(device.get("package_name")) or "com.nexon.bluearchive"
    client_version = _text(request.get("client_version")) or _text(device.get("client_version")) or "0.0.0"
    guid = _text(request.get("guid")) or _uuid_like("guid", package_name, _text(device.get("uuid")), _text(device.get("device_unique_id")))
    npa_code = _text(request.get("npa_code"))
    ngsm_token = _text(request.get("ngsm_token"))
    if not ngsm_token:
        ngsm_token = _derive_ngsm_token(device)
    model = _text(device.get("device_model")) or _text(device.get("model")) or "Android"
    os_version = _text(device.get("os_version")) or "Android"
    app_package = package_name
    app_version = client_version
    module_version = _text(device.get("module_version")) or "grap-core-sim-0"
    engine = _text(device.get("engine")) or "unity"
    language = _text(device.get("locale")) or _text(device.get("language")) or "en-US"
    client_field = _text(device.get("client")) or client_version

    platform_id = 1
    process_id = _u32("process_id", package_name, client_version, guid) % 900000 + 100000
    gid = _u63("gid", service_id, package_name, guid, _text(device.get("mcc")), _text(device.get("mnc")))
    lid = _u63("lid", guid, npa_code, _text(request.get("np_sn")), _text(device.get("device_unique_id")))
    hwid = _digest(
        "hwid",
        service_id,
        package_name,
        guid,
        _text(device.get("device_unique_id")),
        _text(device.get("advertisement_id")),
        _text(device.get("uuid")),
        _text(device.get("uuid2")),
        _text(device.get("mac")),
        length=40,
    )
    lifetoken = _uuid_like("lifetoken", service_id, guid, npa_code, package_name)
    csauthtoken = _digest("csauthtoken", service_id, package_name, guid, str(gid), str(lid), hwid, npa_code, client_version, length=48)
    signature_id = _uuid_like("signature_id", guid, hwid, client_version, module_version)
    log_id = _digest("log_id", guid, npa_code, signature_id, length=24)
    file_hash = _digest("fileHash", package_name, client_version, "libgrap-core.so", guid, length=64)
    piece_hash = _digest("pieceHash", file_hash, signature_id, length=64)

    file_signature = {
        "fileHash": file_hash,
        "fileSizeByte": 0,
        "fileName": "libgrap-core.so",
        "ext": "so",
        "pieceHash": piece_hash,
        "pieceSizeKb": 4,
        "gid": gid,
        "hwid": hwid,
        "guid": guid,
        "signature_id": signature_id,
        "timestamp": issued_at_ms,
        "options": [],
    }

    return {
        "protocol_version": "ngsx-native-sim-v1",
        "generated_at": issued_at_iso,
        "request": {
            "service_id": service_id,
            "package_name": package_name,
            "client_version": client_version,
            "guid": guid,
            "npa_code": npa_code,
            "np_sn": request.get("np_sn"),
            "np_token_present": bool(request.get("np_token_present")),
            "ngsm_token": ngsm_token,
        },
        "derived": {
            "platform_id": platform_id,
            "process_id": process_id,
            "gid": gid,
            "lid": lid,
            "hwid": hwid,
            "lifetoken": lifetoken,
            "csauthtoken": csauthtoken,
            "signature_id": signature_id,
            "log_id": log_id,
            "fileHash": file_hash,
            "pieceHash": piece_hash,
        },
        "payloads": {
            "issue": {"endpoint": "/v1/issue", "body": {"lifetoken": lifetoken, "process_id": process_id, "guid": guid, "model": model}},
            "config": {
                "endpoint": "/v1",
                "body": {
                    "lifetoken": lifetoken,
                    "gid": gid,
                    "lid": lid,
                    "hwid": hwid,
                    "platform_id": platform_id,
                    "process_id": process_id,
                    "guid": guid,
                    "npacode": npa_code,
                    "model": model,
                    "app_package": app_package,
                    "app_version": app_version,
                    "client": client_field,
                    "module_version": module_version,
                    "engine": engine,
                    "os_version": os_version,
                    "language": language,
                },
            },
            "v2": {
                "endpoint": "/v2",
                "body": {
                    "lifetoken": lifetoken,
                    "gid": gid,
                    "lid": lid,
                    "hwid": hwid,
                    "process_id": process_id,
                    "guid": guid,
                    "npacode": npa_code,
                    "csauthtoken": csauthtoken,
                    "app_package": app_package,
                    "app_version": app_version,
                    "client": client_field,
                    "module_version": module_version,
                    "engine": engine,
                    "os_version": os_version,
                    "language": language,
                },
            },
            "close": {
                "endpoint": "/v1/close",
                "body": {
                    "lifetoken": lifetoken,
                    "gid": gid,
                    "lid": lid,
                    "hwid": hwid,
                    "platform_id": platform_id,
                    "process_id": process_id,
                    "guid": guid,
                    "npacode": npa_code,
                    "model": model,
                },
            },
            "signature_session": {
                "lifetoken": lifetoken,
                "subfeature": [],
                "auth_cycle": 0,
                "terminate_message": "",
                "signature": [file_signature],
            },
        },
    }


def _derive_ngsm_token(device: Mapping[str, Any]) -> str:
    try:
        normalized_device = with_ngsm_fingerprint_defaults(device)
        if isinstance(normalized_device, Mapping):
            return generate_ngsm_token(normalized_device)
    except Exception:
        pass
    return _digest("ngsm_token", device.get("device_unique_id"), device.get("uuid"), device.get("uuid2"), device.get("advertisement_id"), length=32)


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _digest(label: str, *parts: Any, length: int = 32) -> str:
    blob = hashlib.sha256()
    blob.update(label.encode("utf-8"))
    for part in parts:
        blob.update(b"\x1f")
        blob.update(_text(part).encode("utf-8"))
    return blob.hexdigest()[:length]


def _uuid_like(label: str, *parts: Any) -> str:
    digest = bytearray(hashlib.md5("|".join([label, *(_text(part) for part in parts)]).encode("utf-8")).digest())
    digest[6] = (digest[6] & 0x0F) | 0x30
    digest[8] = (digest[8] & 0x3F) | 0x80
    return str(uuid.UUID(bytes=bytes(digest)))


def _u32(label: str, *parts: Any) -> int:
    return int(_digest(label, *parts, length=8), 16)


def _u63(label: str, *parts: Any) -> int:
    return int(_digest(label, *parts, length=16), 16) & ((1 << 63) - 1)


__all__ = [
    "build_ngsx_native_simulation",
    "simulate_ngsx_native_run",
]

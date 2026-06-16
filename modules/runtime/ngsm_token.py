from __future__ import annotations

import hashlib
import random
import uuid
from dataclasses import replace
from typing import Any, Mapping


NGSM_FINGERPRINT_VERSION = "10010"
NGSM_PROFILE_FIELDS = ("mac", "display_name", "volume_serial", "disk_serial", "filetime", "version")


def generate_ngsm_token(profile: Mapping[str, Any]) -> str:
    """Generate a stable UUID-v3-shaped NgsM token from local profile fields."""

    fingerprint = ngsm_fingerprint_bytes(profile)
    digest = bytearray(hashlib.md5(fingerprint).digest())
    digest[6] = (digest[6] & 0x0F) | 0x30
    digest[8] = (digest[8] & 0x3F) | 0x80
    return str(uuid.UUID(bytes=bytes(digest)))


def ngsm_fingerprint_bytes(profile: Mapping[str, Any]) -> bytes:
    missing = [field for field in NGSM_PROFILE_FIELDS if _text(profile.get(field)) == ""]
    if missing:
        raise ValueError(f"NgsmToken profile missing fields: {', '.join(missing)}")
    parts = []
    for field in NGSM_PROFILE_FIELDS:
        value = _text(profile.get(field))
        parts.append(f"{field}={value}")
    return "\n".join(parts).encode("utf-8")


def with_ngsm_fingerprint_defaults(profile: Any) -> Any:
    if profile is None:
        return None
    values = _profile_dict(profile)
    rng = random.Random(_seed_material(values))
    defaults = {
        "mac": _stable_mac(rng),
        "display_name": _stable_display_name(values),
        "volume_serial": _stable_hex(rng, 6),
        "disk_serial": _stable_hex(rng, 14),
        "filetime": str(132000000000000000 + rng.randrange(0, 80_000_000_000_000)),
        "version": NGSM_FINGERPRINT_VERSION,
    }
    updates = {key: _text(values.get(key)) or value for key, value in defaults.items()}
    if _is_dataclass_profile(profile):
        return replace(profile, **updates)
    merged = dict(values)
    merged.update(updates)
    return merged


def _profile_dict(profile: Any) -> dict[str, Any]:
    if hasattr(profile, "to_dict"):
        data = profile.to_dict()
        if isinstance(data, dict):
            return data
    if isinstance(profile, Mapping):
        return dict(profile)
    return {}


def _is_dataclass_profile(profile: Any) -> bool:
    return hasattr(profile, "__dataclass_fields__")


def _seed_material(profile: Mapping[str, Any]) -> str:
    for key in ("seed", "device_unique_id", "uuid", "uuid2", "advertisement_id", "idfv"):
        value = _text(profile.get(key))
        if value:
            return value
    stable_parts = [_text(profile.get(key)) for key in ("device_model", "os_version", "resolution", "country", "locale")]
    joined = "|".join(part for part in stable_parts if part)
    return joined or "headless-bluearchive-ngsm"


def _stable_mac(rng: random.Random) -> str:
    first = rng.randrange(0, 256) & 0xFC | 0x02
    data = [first, *(rng.randrange(0, 256) for _ in range(5))]
    return ":".join(f"{item:02X}" for item in data)


def _stable_display_name(profile: Mapping[str, Any]) -> str:
    model = _text(profile.get("device_model"))
    resolution = _text(profile.get("resolution"))
    if model and resolution:
        return f"{model} Display {resolution}"
    if model:
        return f"{model} Display"
    return "Headless BlueArchive Display"


def _stable_hex(rng: random.Random, length: int) -> str:
    return "".join(rng.choice("0123456789ABCDEF") for _ in range(length))


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


__all__ = [
    "NGSM_FINGERPRINT_VERSION",
    "NGSM_PROFILE_FIELDS",
    "generate_ngsm_token",
    "ngsm_fingerprint_bytes",
    "with_ngsm_fingerprint_defaults",
]

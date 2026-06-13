"""Protocol enum and ProtocolConverter.TypeConversion helpers."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from headlessba.config.paths import PROJECT_ROOT


PACKAGE_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_ROOT
DATA_DIR = PACKAGE_ROOT / "data"


def _read_json_from_candidates(*candidates: Path) -> Any:
    for path in candidates:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    joined = ", ".join(str(p) for p in candidates)
    raise FileNotFoundError(f"none of the JSON data files exists: {joined}")


@lru_cache(maxsize=1)
def protocol_converter_data() -> dict[str, Any]:
    return _read_json_from_candidates(
        DATA_DIR / "protocol_converter_bucket_map.json",
        WORKSPACE_ROOT / "analysis_reports" / "protocol_converter_bucket_map.json",
    )


@lru_cache(maxsize=1)
def protocols() -> dict[str, int]:
    try:
        data = _read_json_from_candidates(DATA_DIR / "protocols.json")
        return {str(k): int(v) for k, v in data.items()}
    except FileNotFoundError:
        catalog = protocol_converter_data().get("protocol_catalog", {})
        return {entry["name"]: int(value) for value, entry in catalog.items()}


@lru_cache(maxsize=1)
def protocol_names_by_value() -> dict[int, str]:
    return {value: name for name, value in protocols().items()}


@lru_cache(maxsize=1)
def request_protocols() -> dict[str, dict[str, Any]]:
    try:
        return _read_json_from_candidates(
            DATA_DIR / "request_protocols.json",
            WORKSPACE_ROOT / "analysis_reports" / "request_protocols.json",
        )
    except FileNotFoundError:
        # Fall back to the CSV generated during analysis.
        import csv

        path = WORKSPACE_ROOT / "analysis_reports" / "bluearchive_request_protocol_map.csv"
        rows: dict[str, dict[str, Any]] = {}
        if not path.exists():
            return rows
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                cls = row["RequestClass"]
                proto_value = int(row["ProtocolValue"])
                proto_name = row["ProtocolName"]
                rows[cls] = {
                    "request_class": cls,
                    "short_name": cls.removesuffix("Request"),
                    "protocol_name": proto_name,
                    "protocol_value": proto_value,
                    "source": row.get("Source", ""),
                }
                rows[cls.removesuffix("Request")] = rows[cls]
                rows[proto_name] = rows[cls]
        return rows


def protocol_value(protocol: int | str) -> int:
    if isinstance(protocol, int):
        return protocol
    text = protocol.strip()
    if not text:
        raise ValueError("empty protocol name")
    try:
        return int(text, 0)
    except ValueError:
        pass

    proto_map = protocols()
    if text in proto_map:
        return proto_map[text]
    req = request_protocols().get(text) or request_protocols().get(text.removesuffix("Request"))
    if req:
        return int(req["protocol_value"])
    raise KeyError(f"unknown protocol or request name: {protocol!r}")


def protocol_name(protocol: int | str) -> str:
    value = protocol_value(protocol)
    return protocol_names_by_value().get(value, str(value))


def request_protocol(request_class_or_short_name: str) -> tuple[str, int]:
    reqs = request_protocols()
    req = reqs.get(request_class_or_short_name)
    if req is None and not request_class_or_short_name.endswith("Request"):
        req = reqs.get(request_class_or_short_name + "Request")
    if req is None:
        raise KeyError(f"unknown request class: {request_class_or_short_name!r}")
    return str(req["protocol_name"]), int(req["protocol_value"])


def _to_signed_int32(value: int) -> int:
    value &= 0xFFFFFFFF
    return value - 0x100000000 if value & 0x80000000 else value


def type_conversion(crc: int, protocol: int | str) -> int:
    """ProtocolConverter.TypeConversion(crc, protocol)."""

    bucket = int(crc) % 99
    proto = protocol_value(protocol)
    data = protocol_converter_data()
    bucket_data = data["buckets"][str(bucket)]
    encoded = bucket_data["values"][str(proto)]["encoded_int32"]
    return _to_signed_int32(int(encoded))


def type_conversion_u32(crc: int, protocol: int | str) -> int:
    return type_conversion(crc, protocol) & 0xFFFFFFFF

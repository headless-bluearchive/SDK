from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
from typing import Any, Mapping

from flatbuffers import encode, number_types as N, packer
from flatbuffers.table import Table
from sqlcipher3 import dbapi2 as sqlcipher_dbapi

from config.official_data import OFFICIAL_DATA_DEFAULTS
from config.paths import CORE_DATA_DIR, OFFICIAL_DATA_DIR
from core.crypto import decode_bytes
from core.error import OfficialDataDependencyError, OfficialDataParseError

ACADEMY_MESSANGER_SCHEMA = "AcademyMessangerDBSchema"
ACADEMY_FAVOR_SCHEDULE_SCHEMA = "AcademyFavorScheduleDBSchema"


@dataclass(frozen=True)
class AcademyMessangerRow:
    message_group_id: int
    id: int
    character_id: int
    message_condition: int
    condition_value: int
    pre_condition_group_id: int
    pre_condition_favor_schedule_id: int
    favor_schedule_id: int
    next_group_id: int
    feedback_time_millisec: int
    message_type: int
    image_path: str | None
    message_kr: str | None
    message_jp: str | None
    message_th: str | None
    message_tw: str | None
    message_en: str | None


@dataclass(frozen=True)
class AcademyFavorScheduleRow:
    id: int
    character_id: int
    schedule_group_id: int
    order_in_group: int
    location: str | None
    localize_scenario_id: int
    favor_rank: int
    secret_stone_amount: int
    scenario_script_group_id: int
    reward_parcel_type: list[int]
    reward_parcel_id: list[int]
    reward_amount: list[int]


def parse_official_academy_tables(
    *,
    excel_db_path: Path | None = None,
    output_dir: Path | None = None,
    sqlcipher_key: bytes | str | None = None,
    session: Mapping[str, Any] | None = None,
    profile: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    database_path = Path(excel_db_path or find_latest_excel_db()).resolve()
    target_dir = Path(output_dir or CORE_DATA_DIR).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    resolved_key = resolve_sqlcipher_key(
        sqlcipher_key=sqlcipher_key,
        session=session,
        profile=profile,
    )

    messanger = [
        asdict(parse_academy_messanger_row(row))
        for row in read_schema_bytes(
            database_path,
            ACADEMY_MESSANGER_SCHEMA,
            sqlcipher_key=resolved_key,
        )
    ]
    favor_schedule = [
        asdict(parse_academy_favor_schedule_row(row))
        for row in read_schema_bytes(
            database_path,
            ACADEMY_FAVOR_SCHEDULE_SCHEMA,
            sqlcipher_key=resolved_key,
        )
    ]

    messanger_path = target_dir / "academy_messanger.json"
    favor_path = target_dir / "academy_favor_schedule.json"
    _write_json(messanger_path, messanger)
    _write_json(favor_path, favor_schedule)
    return {
        "ready": True,
        "source": str(database_path),
        "files": {
            "academy_messanger": str(messanger_path),
            "academy_favor_schedule": str(favor_path),
        },
        "counts": {
            "academy_messanger": len(messanger),
            "academy_favor_schedule": len(favor_schedule),
        },
    }


def find_latest_excel_db() -> Path:
    candidates = sorted(OFFICIAL_DATA_DIR.glob("global/*/ExcelDB.db"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not candidates:
        raise OfficialDataParseError(f"ExcelDB.db not found under {OFFICIAL_DATA_DIR}")
    return candidates[0]


def read_schema_bytes(
    database_path: Path,
    schema_name: str,
    *,
    sqlcipher_key: bytes | str | None = None,
    session: Mapping[str, Any] | None = None,
    profile: Mapping[str, Any] | None = None,
) -> list[bytes]:
    resolved_key = resolve_sqlcipher_key(
        sqlcipher_key=sqlcipher_key,
        session=session,
        profile=profile,
    )
    return _read_schema_bytes_dbapi(database_path, schema_name, resolved_key)


def resolve_sqlcipher_key(
    *,
    sqlcipher_key: bytes | str | None = None,
    session: Mapping[str, Any] | None = None,
    profile: Mapping[str, Any] | None = None,
) -> bytes:
    key_value = sqlcipher_key
    for source in (session, profile):
        if key_value:
            break
        key_value = _extract_sqlcipher_key(source)
    key_value = key_value or os.environ.get("HEADLESS_BLUEARCHIVE_SQLCIPHER_KEY")
    key_value = key_value or OFFICIAL_DATA_DEFAULTS.excel_db_sqlcipher_key

    key_bytes = _decode_sqlcipher_key(key_value)
    if not key_bytes:
        raise OfficialDataDependencyError(
            "SQLCipher key is missing. Configure the official data SQLCipher key "
            "or pass sqlcipher_key explicitly."
        )
    return key_bytes


def parse_academy_messanger_row(payload: bytes) -> AcademyMessangerRow:
    table = _root_table(payload)
    return AcademyMessangerRow(
        message_group_id=_int64(table, 4),
        id=_int64(table, 6),
        character_id=_int64(table, 8),
        message_condition=_int32(table, 10),
        condition_value=_int64(table, 12),
        pre_condition_group_id=_int64(table, 14),
        pre_condition_favor_schedule_id=_int64(table, 16),
        favor_schedule_id=_int64(table, 18),
        next_group_id=_int64(table, 20),
        feedback_time_millisec=_int64(table, 22),
        message_type=_int32(table, 24),
        image_path=_string(table, 26),
        message_kr=_string(table, 28),
        message_jp=_string(table, 30),
        message_th=_string(table, 32),
        message_tw=_string(table, 34),
        message_en=_string(table, 36),
    )


def parse_academy_favor_schedule_row(payload: bytes) -> AcademyFavorScheduleRow:
    table = _root_table(payload)
    return AcademyFavorScheduleRow(
        id=_int64(table, 4),
        character_id=_int64(table, 6),
        schedule_group_id=_int64(table, 8),
        order_in_group=_int64(table, 10),
        location=_string(table, 12),
        localize_scenario_id=_uint32(table, 14),
        favor_rank=_int64(table, 16),
        secret_stone_amount=_int64(table, 18),
        scenario_script_group_id=_int64(table, 20),
        reward_parcel_type=_int32_vector(table, 22),
        reward_parcel_id=_int64_vector(table, 24),
        reward_amount=_int64_vector(table, 26),
    )


def _read_schema_bytes_dbapi(
    database_path: Path,
    schema_name: str,
    sqlcipher_key: bytes,
) -> list[bytes]:
    connection = sqlcipher_dbapi.connect(str(database_path))
    try:
        _configure_sqlcipher_dbapi(connection, sqlcipher_key=sqlcipher_key)
        return [bytes(row[0]) for row in connection.execute(f"SELECT Bytes FROM {schema_name}")]
    except Exception as exc:
        raise OfficialDataParseError(f"failed to read {schema_name}: {exc}") from exc
    finally:
        connection.close()


def _configure_sqlcipher_dbapi(connection: Any, *, sqlcipher_key: bytes) -> None:
    connection.execute(f"PRAGMA key = \"x'{sqlcipher_key.hex()}'\"")
    connection.execute("PRAGMA cache_size = -100")
    connection.execute("SELECT count(*) FROM sqlite_master").fetchone()


def _root_table(payload: bytes) -> Table:
    data = bytearray(payload)
    offset = encode.Get(packer.uoffset, data, 0)
    return Table(data, offset)


def _int64(table: Table, slot: int) -> int:
    return int(table.GetSlot(slot, 0, N.Int64Flags))


def _int32(table: Table, slot: int) -> int:
    return int(table.GetSlot(slot, 0, N.Int32Flags))


def _uint32(table: Table, slot: int) -> int:
    return int(table.GetSlot(slot, 0, N.Uint32Flags))


def _string(table: Table, slot: int) -> str | None:
    offset = table.Offset(slot)
    if offset == 0:
        return None
    value = table.String(table.Pos + offset)
    return value.decode("utf-8") if isinstance(value, bytes) else value


def _int32_vector(table: Table, slot: int) -> list[int]:
    return [int(value) for value in _vector_values(table, slot, N.Int32Flags, 4)]


def _int64_vector(table: Table, slot: int) -> list[int]:
    return [int(value) for value in _vector_values(table, slot, N.Int64Flags, 8)]


def _vector_values(table: Table, slot: int, flags: Any, width: int) -> Iterable[int]:
    offset = table.Offset(slot)
    if offset == 0:
        return []
    start = table.Vector(offset)
    return [table.Get(flags, start + index * width) for index in range(table.VectorLen(offset))]


def _write_json(path: Path, data: Any) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def _extract_sqlcipher_key(source: Mapping[str, Any] | None) -> Any:
    if not isinstance(source, Mapping):
        return None
    nested = source.get("sqlcipher")
    if isinstance(nested, Mapping):
        key_value = _first_present(nested, "key", "sqlcipher_key", "SqlCipherKey")
        if key_value:
            return key_value
    return _first_present(source, "sqlcipher_key", "SqlCipherKey")


def _first_present(source: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        value = source.get(key)
        if value not in (None, ""):
            return value
    return None


def _decode_sqlcipher_key(value: bytes | str | None) -> bytes:
    if value in (None, ""):
        return b""
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value)
    text = str(value).strip()
    if text.lower().startswith("x'") and text.endswith("'"):
        text = text[2:-1]
    is_hex = len(text) % 2 == 0 and all(char in "0123456789abcdefABCDEF" for char in text)
    if is_hex:
        try:
            return decode_bytes(text, encoding="auto")
        except Exception:
            pass
    try:
        return decode_bytes(text, encoding="base64")
    except Exception:
        try:
            return decode_bytes(text, encoding="auto")
        except Exception as exc:
            raise OfficialDataDependencyError("SQLCipher key material is invalid") from exc


__all__ = [
    "AcademyFavorScheduleRow",
    "AcademyMessangerRow",
    "find_latest_excel_db",
    "parse_academy_favor_schedule_row",
    "parse_academy_messanger_row",
    "parse_official_academy_tables",
    "read_schema_bytes",
    "resolve_sqlcipher_key",
]

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
import ctypes
from ctypes import POINTER, byref, c_char_p, c_int, c_void_p
import json
import os
from pathlib import Path
from typing import Any, Mapping

from flatbuffers import encode, number_types as N, packer
from flatbuffers.table import Table

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
    sqlcipher_license: str | None = None,
    session: Mapping[str, Any] | None = None,
    profile: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    database_path = Path(excel_db_path or find_latest_excel_db()).resolve()
    target_dir = Path(output_dir or CORE_DATA_DIR).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    resolved_key, resolved_license = resolve_sqlcipher_material(
        sqlcipher_key=sqlcipher_key,
        sqlcipher_license=sqlcipher_license,
        session=session,
        profile=profile,
    )

    messanger = [
        asdict(parse_academy_messanger_row(row))
        for row in read_schema_bytes(
            database_path,
            ACADEMY_MESSANGER_SCHEMA,
            sqlcipher_key=resolved_key,
            sqlcipher_license=resolved_license,
        )
    ]
    favor_schedule = [
        asdict(parse_academy_favor_schedule_row(row))
        for row in read_schema_bytes(
            database_path,
            ACADEMY_FAVOR_SCHEDULE_SCHEMA,
            sqlcipher_key=resolved_key,
            sqlcipher_license=resolved_license,
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
    sqlcipher_license: str | None = None,
    session: Mapping[str, Any] | None = None,
    profile: Mapping[str, Any] | None = None,
) -> list[bytes]:
    resolved_key, resolved_license = resolve_sqlcipher_material(
        sqlcipher_key=sqlcipher_key,
        sqlcipher_license=sqlcipher_license,
        session=session,
        profile=profile,
    )
    for reader in (_read_schema_bytes_dbapi, _read_schema_bytes_ctypes):
        try:
            return reader(database_path, schema_name, resolved_key, resolved_license)
        except OfficialDataDependencyError:
            continue
    raise OfficialDataDependencyError(
        "SQLCipher backend is not available. Install a Python SQLCipher binding or set "
        "HEADLESS_BLUEARCHIVE_SQLCIPHER_DLL to a compatible sqlcipher.dll."
    )


def resolve_sqlcipher_material(
    *,
    sqlcipher_key: bytes | str | None = None,
    sqlcipher_license: str | None = None,
    session: Mapping[str, Any] | None = None,
    profile: Mapping[str, Any] | None = None,
) -> tuple[bytes, str]:
    key_value = sqlcipher_key
    license_value = sqlcipher_license
    for source in (session, profile):
        if key_value and license_value:
            break
        source_key, source_license = _extract_sqlcipher_material(source)
        key_value = key_value or source_key
        license_value = license_value or source_license
    key_value = key_value or OFFICIAL_DATA_DEFAULTS.excel_db_sqlcipher_key
    license_value = license_value or OFFICIAL_DATA_DEFAULTS.excel_db_sqlcipher_license

    key_bytes = _decode_sqlcipher_key(key_value)
    license_text = str(license_value or "")
    if not key_bytes or not license_text:
        raise OfficialDataDependencyError(
            "SQLCipher material is missing. Configure official data SQLCipher material "
            "or pass sqlcipher_key and sqlcipher_license explicitly."
        )
    return key_bytes, license_text


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
    sqlcipher_license: str,
) -> list[bytes]:
    module = _optional_sqlcipher_module()
    if module is None:
        raise OfficialDataDependencyError("Python SQLCipher binding is not installed")
    connection = module.connect(str(database_path))
    try:
        _configure_sqlcipher_dbapi(connection, sqlcipher_key=sqlcipher_key, sqlcipher_license=sqlcipher_license)
        return [bytes(row[0]) for row in connection.execute(f"SELECT Bytes FROM {schema_name}")]
    except Exception as exc:  # noqa: BLE001 - normalize optional backend errors
        raise OfficialDataParseError(f"failed to read {schema_name}: {exc}") from exc
    finally:
        connection.close()


def _read_schema_bytes_ctypes(
    database_path: Path,
    schema_name: str,
    sqlcipher_key: bytes,
    sqlcipher_license: str,
) -> list[bytes]:
    dll_path = os.environ.get("HEADLESS_BLUEARCHIVE_SQLCIPHER_DLL")
    if not dll_path:
        raise OfficialDataDependencyError("HEADLESS_BLUEARCHIVE_SQLCIPHER_DLL is not set")
    return _SqlCipherDll(Path(dll_path)).read_blobs(
        database_path,
        schema_name,
        sqlcipher_key=sqlcipher_key,
        sqlcipher_license=sqlcipher_license,
    )


def _optional_sqlcipher_module():
    for name in ("sqlcipher3.dbapi2", "pysqlcipher3.dbapi2"):
        try:
            module = __import__(name, fromlist=["connect"])
        except ImportError:
            continue
        return module
    return None


def _configure_sqlcipher_dbapi(connection: Any, *, sqlcipher_key: bytes, sqlcipher_license: str) -> None:
    connection.execute(f"PRAGMA cipher_license = '{_escape_pragma_text(sqlcipher_license)}'")
    connection.execute(f"PRAGMA key = \"x'{sqlcipher_key.hex()}'\"")
    connection.execute("PRAGMA cache_size = -100")
    connection.execute("SELECT count(*) FROM sqlite_master").fetchone()


class _SqlCipherDll:
    def __init__(self, dll_path: Path) -> None:
        if not dll_path.exists():
            raise OfficialDataDependencyError(f"sqlcipher.dll not found: {dll_path}")
        self._lib = ctypes.CDLL(str(dll_path))
        self._lib.sqlite3_open.argtypes = [c_char_p, POINTER(c_void_p)]
        self._lib.sqlite3_open.restype = c_int
        self._lib.sqlite3_close.argtypes = [c_void_p]
        self._lib.sqlite3_close.restype = c_int
        self._lib.sqlite3_exec.argtypes = [c_void_p, c_char_p, c_void_p, c_void_p, POINTER(c_char_p)]
        self._lib.sqlite3_exec.restype = c_int
        self._lib.sqlite3_prepare_v2.argtypes = [c_void_p, c_char_p, c_int, POINTER(c_void_p), POINTER(c_char_p)]
        self._lib.sqlite3_prepare_v2.restype = c_int
        self._lib.sqlite3_step.argtypes = [c_void_p]
        self._lib.sqlite3_step.restype = c_int
        self._lib.sqlite3_finalize.argtypes = [c_void_p]
        self._lib.sqlite3_finalize.restype = c_int
        self._lib.sqlite3_column_blob.argtypes = [c_void_p, c_int]
        self._lib.sqlite3_column_blob.restype = c_void_p
        self._lib.sqlite3_column_bytes.argtypes = [c_void_p, c_int]
        self._lib.sqlite3_column_bytes.restype = c_int
        self._lib.sqlite3_errmsg.argtypes = [c_void_p]
        self._lib.sqlite3_errmsg.restype = c_char_p

    def read_blobs(
        self,
        database_path: Path,
        schema_name: str,
        *,
        sqlcipher_key: bytes,
        sqlcipher_license: str,
    ) -> list[bytes]:
        database = c_void_p()
        rc = self._lib.sqlite3_open(str(database_path).encode("utf-8"), byref(database))
        if rc != 0:
            raise OfficialDataParseError(f"failed to open ExcelDB.db with SQLCipher: rc={rc}")
        try:
            self._configure(database, sqlcipher_key=sqlcipher_key, sqlcipher_license=sqlcipher_license)
            return self._select_blobs(database, schema_name)
        finally:
            self._lib.sqlite3_close(database)

    def _configure(self, database: c_void_p, *, sqlcipher_key: bytes, sqlcipher_license: str) -> None:
        self._exec(database, f"PRAGMA cipher_license = '{_escape_pragma_text(sqlcipher_license)}'")
        self._exec(database, f"PRAGMA key = \"x'{sqlcipher_key.hex()}'\"")
        self._exec(database, "PRAGMA cache_size = -100")
        self._exec(database, "SELECT count(*) FROM sqlite_master")

    def _select_blobs(self, database: c_void_p, schema_name: str) -> list[bytes]:
        if not schema_name.isidentifier():
            raise OfficialDataParseError(f"invalid schema name: {schema_name}")
        statement = c_void_p()
        tail = c_char_p()
        sql = f"SELECT Bytes FROM {schema_name}".encode("utf-8")
        rc = self._lib.sqlite3_prepare_v2(database, sql, -1, byref(statement), byref(tail))
        if rc != 0:
            raise OfficialDataParseError(self._errmsg(database))
        rows: list[bytes] = []
        try:
            while True:
                rc = self._lib.sqlite3_step(statement)
                if rc == 100:
                    size = self._lib.sqlite3_column_bytes(statement, 0)
                    pointer = self._lib.sqlite3_column_blob(statement, 0)
                    rows.append(ctypes.string_at(pointer, size))
                    continue
                if rc == 101:
                    return rows
                raise OfficialDataParseError(self._errmsg(database))
        finally:
            self._lib.sqlite3_finalize(statement)

    def _exec(self, database: c_void_p, sql: str) -> None:
        error = c_char_p()
        rc = self._lib.sqlite3_exec(database, sql.encode("utf-8"), None, None, byref(error))
        if rc != 0:
            message = error.value.decode("utf-8", "ignore") if error.value else self._errmsg(database)
            raise OfficialDataParseError(message)

    def _errmsg(self, database: c_void_p) -> str:
        return self._lib.sqlite3_errmsg(database).decode("utf-8", "ignore")


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


def _extract_sqlcipher_material(source: Mapping[str, Any] | None) -> tuple[Any, Any]:
    if not isinstance(source, Mapping):
        return None, None
    nested = source.get("sqlcipher")
    if isinstance(nested, Mapping):
        key_value = _first_present(nested, "key", "sqlcipher_key", "SqlCipherKey")
        license_value = _first_present(nested, "license", "sqlcipher_license", "SqlCipherLicense")
        if key_value or license_value:
            return key_value, license_value
    return (
        _first_present(source, "sqlcipher_key", "SqlCipherKey"),
        _first_present(source, "sqlcipher_license", "SqlCipherLicense"),
    )


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


def _escape_pragma_text(value: str) -> str:
    return value.replace("'", "''")


__all__ = [
    "AcademyFavorScheduleRow",
    "AcademyMessangerRow",
    "find_latest_excel_db",
    "parse_academy_favor_schedule_row",
    "parse_academy_messanger_row",
    "parse_official_academy_tables",
    "read_schema_bytes",
    "resolve_sqlcipher_material",
]

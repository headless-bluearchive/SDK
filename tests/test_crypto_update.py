"""Offline regression coverage for the global 1.96.474931 key rotation."""
import base64
import asyncio
import hashlib
import sys
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from sqlcipher3 import dbapi2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.official_data import OFFICIAL_DATA_DEFAULTS
from core import crypto
from core.error import OfficialDataDecryptionError, OfficialDataParseError
from core.official_table_parser import (
    _sqlcipher_key_candidates, parse_official_academy_tables, read_schema_bytes,
)


def test_current_rsa_public_key_matches_observed_client():
    pem = crypto.ACCOUNT_CHECK_NEXON_RSA_PUBLIC_KEY_PEM
    assert hashlib.sha256(pem).hexdigest() == "5fa6164df93d5cec6454a36c3b27b2d21a0efafc0f3438b30b6c7af9b8fbecf0"
    assert serialization.load_pem_public_key(pem).key_size == 4096


def test_account_check_still_encrypts_raw_bytes_with_oaep_sha1(monkeypatch):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    monkeypatch.setattr(crypto, "_account_check_nexon_rsa_public_key", lambda: key.public_key())
    fields, raw_key, raw_iv = crypto.account_check_nexon_key_iv_fields(b"k" * 16, b"i" * 16)
    oaep = padding.OAEP(mgf=padding.MGF1(hashes.SHA1()), algorithm=hashes.SHA1(), label=None)
    assert key.decrypt(base64.b64decode(fields["ClientGeneratedKey"]), oaep) == raw_key == b"k" * 16
    assert key.decrypt(base64.b64decode(fields["ClientGeneratedIV"]), oaep) == raw_iv == b"i" * 16


@pytest.fixture(autouse=True)
def clear_key_environment(monkeypatch):
    monkeypatch.delenv("HEADLESS_BLUEARCHIVE_SQLCIPHER_KEY", raising=False)


def make_database(path, key):
    connection = dbapi2.connect(str(path))
    try:
        connection.execute(f"PRAGMA key = \"x'{key.hex()}'\"")
        connection.execute("CREATE TABLE TestSchema (Bytes BLOB)")
        connection.execute("INSERT INTO TestSchema VALUES (?)", (b"sample",))
        connection.commit()
    finally:
        connection.close()


@pytest.mark.parametrize("key", [OFFICIAL_DATA_DEFAULTS.excel_db_sqlcipher_key, *OFFICIAL_DATA_DEFAULTS.legacy_excel_db_sqlcipher_keys])
def test_default_keyring_opens_current_and_legacy_read_only(tmp_path, key):
    path = tmp_path / "ExcelDB.db"
    make_database(path, key)
    before = path.read_bytes()
    assert read_schema_bytes(path, "TestSchema") == [b"sample"]
    assert path.read_bytes() == before


def test_key_precedence_and_no_fallback_for_explicit_material(monkeypatch):
    monkeypatch.setenv("HEADLESS_BLUEARCHIVE_SQLCIPHER_KEY", (b"e" * 32).hex())
    session = {"sqlcipher": {"key": (b"s" * 32).hex()}}
    profile = {"sqlcipher_key": (b"p" * 32).hex()}
    assert _sqlcipher_key_candidates(sqlcipher_key=b"x" * 32, session=session, profile=profile) == (b"x" * 32,)
    assert _sqlcipher_key_candidates(session=session, profile=profile) == (b"s" * 32,)
    assert _sqlcipher_key_candidates(profile=profile) == (b"p" * 32,)
    assert _sqlcipher_key_candidates() == (b"e" * 32,)


def test_wrong_explicit_key_is_not_silently_replaced(tmp_path):
    path = tmp_path / "ExcelDB.db"
    make_database(path, OFFICIAL_DATA_DEFAULTS.excel_db_sqlcipher_key)
    with pytest.raises(OfficialDataDecryptionError) as caught:
        read_schema_bytes(path, "TestSchema", sqlcipher_key=b"x" * 32)
    assert (b"x" * 32).hex() not in str(caught.value)
    assert "override" in str(caught.value)


def test_wrong_key_does_not_publish_parsed_outputs(tmp_path):
    path = tmp_path / "ExcelDB.db"
    make_database(path, b"u" * 32)
    output = tmp_path / "parsed"
    output.mkdir()
    existing = output / "academy_messanger.json"
    existing.write_text("previous output")
    with pytest.raises(OfficialDataDecryptionError):
        parse_official_academy_tables(excel_db_path=path, output_dir=output)
    assert existing.read_text() == "previous output"
    assert not (output / "academy_favor_schedule.json").exists()


def test_schema_error_is_not_reported_as_key_error(tmp_path):
    path = tmp_path / "ExcelDB.db"
    make_database(path, OFFICIAL_DATA_DEFAULTS.excel_db_sqlcipher_key)
    with pytest.raises(OfficialDataParseError) as caught:
        read_schema_bytes(path, "MissingSchema")
    assert not isinstance(caught.value, OfficialDataDecryptionError)


def test_missing_input_is_not_created(tmp_path):
    path = tmp_path / "missing.db"
    with pytest.raises(dbapi2.OperationalError):
        read_schema_bytes(path, "TestSchema")
    assert not path.exists()


@pytest.mark.parametrize("decryption_failure", [False, True])
def test_prepare_data_preserves_key_sources_and_reports_key_failures(monkeypatch, tmp_path, decryption_failure):
    from core import official_data

    captured = {}
    session = {"sqlcipher": {"key": "session-key"}}
    profile = {"sqlcipher_key": "profile-key"}

    async def download(**kwargs):
        return {"output_dir": str(tmp_path), "files": []}

    def parse(**kwargs):
        captured.update(kwargs)
        if decryption_failure:
            raise OfficialDataDecryptionError("key/version mismatch")
        return {"ready": True}

    monkeypatch.setattr(official_data, "download_global_table_bundles", download)
    monkeypatch.setattr(official_data, "parse_official_academy_tables", parse)
    monkeypatch.setattr(official_data, "_save_manifest", lambda *args: None)
    monkeypatch.setattr(official_data, "_parsed_status", lambda: {"ready": False})
    result = asyncio.run(official_data.prepare_global_data(
        client_version="1.96.474931", session=session, profile=profile, cleanup_after_parse=False,
    ))
    assert captured["sqlcipher_key"] is None
    assert captured["session"] is session
    assert captured["profile"] is profile
    assert result["parsed"]["ready"] is not decryption_failure
    if decryption_failure:
        assert result["parser_error"]["type"] == "OfficialDataDecryptionError"
        assert "key overrides" in result["next_step"]
        assert "install" not in result["next_step"]

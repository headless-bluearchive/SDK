from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OfficialDataDefaults:
    excel_db_sqlcipher_key: bytes = bytes.fromhex(
        "efa143094711b6563ec2132d4d6bbe8533d4e291ed4820bdb515b26bb57bb3f0"
    )
    excel_db_sqlcipher_license: str = "4d8adfb30e03f9cf27f800a2c1ba3c48fb4ca1b08b0f5ed59a4d5ecbf45ealt1"


OFFICIAL_DATA_DEFAULTS = OfficialDataDefaults()

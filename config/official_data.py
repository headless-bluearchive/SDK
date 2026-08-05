from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OfficialDataDefaults:
    excel_db_sqlcipher_key: bytes = bytes.fromhex(
        "efa143094711b6563ec2132d4d6bbe8533d4e291ed4820bdb515b26bb57bb3f0"
    )


OFFICIAL_DATA_DEFAULTS = OfficialDataDefaults()

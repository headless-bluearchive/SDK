from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OfficialDataDefaults:
    # Verified against global 1.96.474931 Android ExcelDB.db.
    excel_db_sqlcipher_key: bytes = bytes.fromhex(
        "05f508236ff3dc4e5dc7cb6fcea0ede0d90a89753dc5e5d36c30393e9b072f48"
    )

    # Used only when no explicit/session/profile/environment key was supplied.
    legacy_excel_db_sqlcipher_keys: tuple[bytes, ...] = (
        bytes.fromhex("efa143094711b6563ec2132d4d6bbe8533d4e291ed4820bdb515b26bb57bb3f0"),  # Verified against 1.90.439170.
    )


OFFICIAL_DATA_DEFAULTS = OfficialDataDefaults()

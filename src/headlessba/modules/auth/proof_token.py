"""ProofToken solver used before the main account auth request."""

from __future__ import annotations

import base64
import hashlib


def proof_token_hash(value: int) -> str:
    """Match MX.Core.Crypto.ProofToken.ProofTokenHelper.GetHash(long)."""

    digest = hashlib.md5(str(int(value)).encode("utf-16le")).digest()
    return base64.b32encode(digest).decode("ascii").rstrip("=")


def proof_token_search_span(hint: int) -> int:
    """Return the low-bit span used by ProofTokenHelper.Solve."""

    value = int(hint)
    if value <= 0:
        raise ValueError("ProofToken hint must be a positive integer")
    return value & -value


def solve_proof_token(question: str, hint: int, *, max_attempts: int | None = None) -> int:
    """Solve the server ProofToken question.

    The client enumerates ``answer = hint | offset`` for offsets below the
    lowest set bit of ``hint`` and compares the custom Base32-MD5 hash.
    """

    wanted = (question or "").strip().upper()
    if not wanted:
        raise ValueError("ProofToken question is empty")
    span = proof_token_search_span(hint)
    if max_attempts is not None and span > int(max_attempts):
        raise ValueError(f"ProofToken span {span} exceeds max_attempts {max_attempts}")
    base = int(hint)
    for offset in range(span):
        candidate = base | offset
        if proof_token_hash(candidate) == wanted:
            return candidate
    raise ValueError(f"ProofToken answer not found in {span} candidates")

"""
VAJRA (SIH 26183) — Evidence Ledger Hash-Chain Engine
Deterministic canonical JSON serialization and SHA-256 hash chaining.

Formula:
record_hash = SHA256(canonical_json(record_without_hash) + previous_record_hash)
Genesis hash = "GENESIS"
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

GENESIS_HASH = "GENESIS"


def canonical_json(data: Any) -> str:
    """
    Serializes a Python dict/object to a canonical, deterministic JSON string.
    Keys are sorted recursively, no extra whitespace, ensuring bit-for-bit reproducibility.
    """
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_hex(data_str: str) -> str:
    """Computes SHA-256 hex digest of a string using UTF-8."""
    return hashlib.sha256(data_str.encode("utf-8")).hexdigest()


def compute_record_hash(record_without_hash: Dict[str, Any], previous_record_hash: str) -> str:
    """
    Computes the tamper-evident hash for an evidence record.
    record_hash = SHA256(canonical_json(record_without_hash) + previous_record_hash)
    """
    serialized_record = canonical_json(record_without_hash)
    combined = serialized_record + previous_record_hash
    return sha256_hex(combined)


def extract_record_without_hash(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strips content_hash and prev_hash from the record payload to produce
    the canonical record_without_hash payload.
    """
    exclude = {"content_hash", "prev_hash"}
    return {k: v for k, v in record.items() if k not in exclude}

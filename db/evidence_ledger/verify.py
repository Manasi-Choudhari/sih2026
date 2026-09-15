"""
VAJRA (SIH 26183) — Evidence Ledger Verification Algorithm
Validates tamper-evident hash-chains for cases.

verify():
    previous = "GENESIS"
    for record in ordered_case_records:
        expected = SHA256(canonical_json(record_without_hash) + previous)
        if expected != record.content_hash: return FAIL
        previous = record.content_hash
    return PASS
"""

from __future__ import annotations

from typing import Any, Dict, List
from db.evidence_ledger.hash_chain import (
    GENESIS_HASH,
    compute_record_hash,
    extract_record_without_hash,
)


def verify_evidence_chain(ordered_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Verifies the integrity of an ordered sequence of evidence records for a case.
    Returns:
        {"status": "PASS", "verified_count": int, "head_hash": str}
        or
        {"status": "FAIL", "reason": str, "failed_record_id": str, "index": int, "expected_hash": str, "actual_hash": str}
    """
    if not ordered_records:
        return {
            "status": "PASS",
            "verified_count": 0,
            "head_hash": GENESIS_HASH,
            "message": "Empty ledger is valid.",
        }

    previous = GENESIS_HASH

    for idx, record in enumerate(ordered_records):
        evidence_id = record.get("evidence_id", f"record_{idx}")
        prev_hash = record.get("prev_hash")
        content_hash = record.get("content_hash")

        # 1. Check parent linkage
        if prev_hash != previous:
            return {
                "status": "FAIL",
                "reason": "PREV_HASH_MISMATCH",
                "failed_record_id": evidence_id,
                "index": idx,
                "expected_prev": previous,
                "actual_prev": prev_hash,
            }

        # 2. Check content hash match
        record_without_hash = extract_record_without_hash(record)
        expected = compute_record_hash(record_without_hash, previous)

        if expected != content_hash:
            return {
                "status": "FAIL",
                "reason": "CONTENT_HASH_MISMATCH",
                "failed_record_id": evidence_id,
                "index": idx,
                "expected_hash": expected,
                "actual_hash": content_hash,
            }

        previous = content_hash

    return {
        "status": "PASS",
        "verified_count": len(ordered_records),
        "head_hash": previous,
    }


def run_tamper_test(original_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Simulates adversarial tampering:
    1. Verifies the original chain passes.
    2. Mutates content in a record.
    3. Verifies that the tampered chain is detected as FAIL.
    """
    # 1. Clean verification
    clean_result = verify_evidence_chain(original_records)
    if clean_result["status"] != "PASS":
        return {
            "tamper_test_passed": False,
            "error": "Original records did not verify clean.",
            "clean_result": clean_result,
        }

    if not original_records:
        return {
            "tamper_test_passed": True,
            "message": "Empty chain passed cleanly; no records to tamper.",
        }

    # 2. Clone and deliberately alter record 0 content
    import copy

    tampered_records = copy.deepcopy(original_records)
    target_record = tampered_records[0]
    if isinstance(target_record.get("content"), dict):
        target_record["content"]["adversarial_mutation"] = True
    else:
        target_record["content"] = {"tampered": True}

    # 3. Verify tampered chain fails
    tampered_result = verify_evidence_chain(tampered_records)
    detected = tampered_result["status"] == "FAIL"

    return {
        "tamper_test_passed": detected,
        "clean_verification": clean_result,
        "tampered_verification": tampered_result,
        "detected_tampering": detected,
    }

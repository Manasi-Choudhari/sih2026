"""
Tests for VAJRA Evidence Ledger
Validates deterministic hashing, SHA-256 chaining, genesis hashing, and tamper detection.
"""

from db.evidence_ledger.hash_chain import (
    GENESIS_HASH,
    canonical_json,
    compute_record_hash,
    extract_record_without_hash,
)
from db.evidence_ledger.verify import (
    run_tamper_test,
    verify_evidence_chain,
)


def test_canonical_json_sorting():
    # Unordered keys must produce identical canonical string
    d1 = {"z": 100, "a": "first", "m": {"b": 2, "a": 1}}
    d2 = {"a": "first", "m": {"a": 1, "b": 2}, "z": 100}
    assert canonical_json(d1) == canonical_json(d2)
    assert canonical_json(d1) == '{"a":"first","m":{"a":1,"b":2},"z":100}'


def test_genesis_chain_and_verify():
    # Build a 3-record chain starting from GENESIS
    r1_raw = {
        "evidence_id": "ev_001",
        "case_id": "case_test_1",
        "type": "victim_complaint",
        "source": "ncrp_portal",
        "content": {"victim": "alice", "loss_eth": 2.5},
        "software_version": "1.0.0",
    }
    h1 = compute_record_hash(r1_raw, GENESIS_HASH)
    r1 = {**r1_raw, "prev_hash": GENESIS_HASH, "content_hash": h1}

    r2_raw = {
        "evidence_id": "ev_002",
        "case_id": "case_test_1",
        "type": "blockchain_tx",
        "source": "eth_adapter",
        "content": {"tx_hash": "0xabc", "from": "alice", "to": "bob", "amount": 2.5},
        "software_version": "1.0.0",
    }
    h2 = compute_record_hash(r2_raw, h1)
    r2 = {**r2_raw, "prev_hash": h1, "content_hash": h2}

    r3_raw = {
        "evidence_id": "ev_003",
        "case_id": "case_test_1",
        "type": "vasp_attribution",
        "source": "attribution_engine",
        "content": {"vasp": "DemoExchange", "tier": "Strong"},
        "software_version": "1.0.0",
    }
    h3 = compute_record_hash(r3_raw, h2)
    r3 = {**r3_raw, "prev_hash": h2, "content_hash": h3}

    chain = [r1, r2, r3]

    res = verify_evidence_chain(chain)
    assert res["status"] == "PASS"
    assert res["verified_count"] == 3
    assert res["head_hash"] == h3


def test_tamper_detection_mutation():
    r1_raw = {
        "evidence_id": "ev_001",
        "case_id": "case_test_tamper",
        "type": "tx",
        "source": "rpc",
        "content": {"amount": 10.0},
        "software_version": "1.0.0",
    }
    h1 = compute_record_hash(r1_raw, GENESIS_HASH)
    r1 = {**r1_raw, "prev_hash": GENESIS_HASH, "content_hash": h1}

    r2_raw = {
        "evidence_id": "ev_002",
        "case_id": "case_test_tamper",
        "type": "tx",
        "source": "rpc",
        "content": {"amount": 9.9},
        "software_version": "1.0.0",
    }
    h2 = compute_record_hash(r2_raw, h1)
    r2 = {**r2_raw, "prev_hash": h1, "content_hash": h2}

    clean_chain = [r1, r2]

    # Deliberately modify content in r1
    tampered_chain = [
        {**r1, "content": {"amount": 1000000.0}},  # tampered
        r2,
    ]

    fail_res = verify_evidence_chain(tampered_chain)
    assert fail_res["status"] == "FAIL"
    assert fail_res["failed_record_id"] == "ev_001"
    assert fail_res["reason"] == "CONTENT_HASH_MISMATCH"


def test_tamper_detection_break_link():
    r1_raw = {"evidence_id": "ev_1", "content": {}, "case_id": "c1", "type": "t", "source": "s", "software_version": "1.0"}
    h1 = compute_record_hash(r1_raw, GENESIS_HASH)
    r1 = {**r1_raw, "prev_hash": GENESIS_HASH, "content_hash": h1}

    r2_raw = {"evidence_id": "ev_2", "content": {}, "case_id": "c1", "type": "t", "source": "s", "software_version": "1.0"}
    h2 = compute_record_hash(r2_raw, h1)
    # Corrupt prev_hash
    r2 = {**r2_raw, "prev_hash": "CORRUPTED_PARENT", "content_hash": h2}

    fail_res = verify_evidence_chain([r1, r2])
    assert fail_res["status"] == "FAIL"
    assert fail_res["reason"] == "PREV_HASH_MISMATCH"
    assert fail_res["failed_record_id"] == "ev_2"


def test_run_tamper_test_suite():
    r1_raw = {"evidence_id": "ev_1", "content": {"val": 42}, "case_id": "c1", "type": "t", "source": "s", "software_version": "1.0"}
    h1 = compute_record_hash(r1_raw, GENESIS_HASH)
    chain = [{**r1_raw, "prev_hash": GENESIS_HASH, "content_hash": h1}]

    test_res = run_tamper_test(chain)
    assert test_res["tamper_test_passed"] is True
    assert test_res["detected_tampering"] is True

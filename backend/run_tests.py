"""
Direct runner for T1 test suite without requiring pytest binary.
"""

import sys
from pathlib import Path

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient
from backend.main import app

def run_tests():
    client = TestClient(app)
    print("[1/10] Testing root endpoint...")
    res = client.get("/")
    assert res.status_code == 200 and res.json()["ncrp_mock_mode"] is True
    print("  -> PASS")

    print("[2/10] Testing auth login...")
    res = client.post("/auth/login", json={"username": "investigator_user", "password": "secure"})
    assert res.status_code == 200 and "access_token" in res.json()
    print("  -> PASS")

    print("[3/10] Testing case queue & case creation...")
    res = client.get("/cases")
    assert res.status_code == 200 and len(res.json()) >= 5
    c_res = client.post("/cases", json={"victim_address": "s1_victim", "chain": "ETH"})
    assert c_res.status_code == 201
    case_id = c_res.json()["case_id"]
    get_res = client.get(f"/cases/{case_id}")
    assert get_res.status_code == 200
    print("  -> PASS")

    print("[4/10] Testing trace graph extraction...")
    res = client.get("/cases/case_s1/graph")
    assert res.status_code == 200
    nodes = [n["id"] for n in res.json()["nodes"]]
    assert "s1_victim" in nodes and "s1_vasp" in nodes
    print("  -> PASS")

    print("[5/10] Testing VASP attribution & three-number framework...")
    res = client.get("/cases/case_s1/attribution")
    assert res.status_code == 200
    data = res.json()
    assert "rule_risk_score" in data and "attribution_confidence" in data and "ml_probability" in data
    assert data["ml"]["output_label"] == "model_output"
    assert data["candidates"][0]["evidence_tier"] == "Strong"
    print("  -> PASS")

    print("[6/10] Testing ATLAS counter-hypotheses & challenge engine...")
    res = client.get("/cases/case_s1/atlas")
    assert res.status_code == 200
    atlas_data = res.json()
    assert len(atlas_data["alternatives"]) >= 3
    assert len(atlas_data["contradictions"]) >= 1
    print("  -> PASS")

    print("[7/10] Testing Evidence Ledger & cryptographic verification...")
    res = client.get("/cases/case_s1/evidence")
    assert res.status_code == 200 and len(res.json()) >= 3
    v_res = client.get("/cases/case_s1/verify")
    assert v_res.status_code == 200 and v_res.json()["status"] == "PASS" and not v_res.json()["is_tampered"]
    print("  -> PASS")

    print("[8/10] Testing Recommendation engine & human approval gate...")
    res = client.get("/cases/case_s1/recommendations")
    recs = res.json()
    assert len(recs) > 0
    rec_id = recs[0]["rec_id"]
    act_res = client.post("/cases/case_s1/recommendations", json={"rec_id": rec_id, "action": "approve"})
    assert act_res.status_code == 200 and act_res.json()["approval_status"] == "approved"
    print("  -> PASS")

    print("[9/10] Testing Standardized PDF/HTML report generator...")
    res = client.post("/cases/case_s1/report")
    assert res.status_code == 200 and len(res.json()["report_hash"]) == 64
    print("  -> PASS")

    print("[10/10] Testing simulated NCRP/SAHYOG callback...")
    res = client.post("/external/case-update", json={
        "case_id": "case_s1", "external_ref": "NCRP-001", "status_update": "FIR Registered", "payload": {}
    })
    assert res.status_code == 200 and res.json()["simulation_mode"] is True
    print("  -> PASS")

    print("\n========================================================")
    print("ALL 10 T1 BACKEND & INVESTIGATION PIPELINE TESTS PASSED!")
    print("========================================================")

if __name__ == "__main__":
    run_tests()

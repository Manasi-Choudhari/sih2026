"""
End-to-end unit test suite for T1 backend endpoints and logic contracts.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["ncrp_mock_mode"] is True

def test_login():
    response = client.post("/auth/login", json={"username": "investigator_user", "password": "secure"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "investigator"

def test_cases_queue_and_create():
    # 1. Get queue
    res = client.get("/cases")
    assert res.status_code == 200
    cases = res.json()
    assert len(cases) >= 5

    # 2. Create case
    new_case = {
        "complaint_id": "TEST-NCRP-999",
        "victim_address": "s1_victim",
        "chain": "ETH",
        "reported_amount": 2.5
    }
    c_res = client.post("/cases", json=new_case)
    assert c_res.status_code == 201
    created = c_res.json()
    assert created["victim_address"] == "s1_victim"
    case_id = created["case_id"]

    # 3. Get single case
    get_res = client.get(f"/cases/{case_id}")
    assert get_res.status_code == 200
    assert get_res.json()["case_id"] == case_id

def test_trace_graph():
    res = client.get("/cases/case_s1/graph")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "edges" in data
    node_ids = [n["id"] for n in data["nodes"]]
    assert "s1_victim" in node_ids
    assert "s1_vasp" in node_ids

def test_attribution_and_three_numbers():
    res = client.get("/cases/case_s1/attribution")
    assert res.status_code == 200
    data = res.json()
    # Contract: 3 numbers never merged
    assert "rule_risk_score" in data
    assert "attribution_confidence" in data
    assert "ml_probability" in data
    assert "ml" in data
    assert data["ml"]["output_label"] == "model_output"
    assert data["ml"]["is_model_output"] is True
    
    # Evidence tier check on scenario 1
    candidates = data["candidates"]
    assert len(candidates) > 0
    assert candidates[0]["evidence_tier"] == "Strong"
    assert "DemoExchange" in candidates[0]["vasp_name"]

def test_atlas_challenge():
    res = client.get("/cases/case_s1/atlas")
    assert res.status_code == 200
    data = res.json()
    assert len(data["alternatives"]) >= 3
    assert len(data["contradictions"]) >= 1
    assert "robustness_score" in data

def test_evidence_ledger_and_verify():
    # 1. Fetch entries
    res = client.get("/cases/case_s1/evidence")
    assert res.status_code == 200
    entries = res.json()
    assert len(entries) >= 3

    # 2. Verify hash chain
    v_res = client.get("/cases/case_s1/verify")
    assert v_res.status_code == 200
    v_data = v_res.json()
    assert v_data["status"] == "PASS"
    assert v_data["is_tampered"] is False

def test_recommendation_and_approval_gate():
    res = client.get("/cases/case_s1/recommendations")
    assert res.status_code == 200
    recs = res.json()
    assert len(recs) > 0
    rec_id = recs[0]["rec_id"]
    assert recs[0]["approval_status"] == "pending"

    # Approve
    act_res = client.post("/cases/case_s1/recommendations", json={"rec_id": rec_id, "action": "approve"})
    assert act_res.status_code == 200
    assert act_res.json()["approval_status"] == "approved"

def test_information_gap_next_actions():
    res = client.get("/cases/case_s1/actions")
    assert res.status_code == 200
    actions = res.json()
    assert len(actions) >= 3
    assert "priority_score" in actions[0]
    assert actions[0]["priority_score"] >= actions[1]["priority_score"]
    assert "target_entity" in actions[0]

def test_report_generation():
    res = client.post("/cases/case_s1/report")
    assert res.status_code == 200
    data = res.json()
    assert "report_id" in data
    assert "report_hash" in data
    assert len(data["report_hash"]) == 64

def test_ncrp_mock_callback():
    payload = {
        "case_id": "case_s1",
        "external_ref": "NCRP-UPDATE-001",
        "status_update": "FIR Registered",
        "source": "NCRP_MOCK",
        "payload": {"fir_number": "FIR-2026-DL-9821"}
    }
    res = client.post("/external/case-update", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PROCESSED_SIMULATED"
    assert data["simulation_mode"] is True

if __name__ == "__main__":
    pytest.main(["-v", __file__])

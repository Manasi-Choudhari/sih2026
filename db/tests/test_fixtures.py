"""
Tests for Scenario Fixtures & Ground Truth Data
Validates all 5 scenario JSON fixtures and merged ground_truth.json.
"""

import json
from pathlib import Path
from scenarios.seed.seed import load_fixtures


def test_load_all_fixtures():
    fixtures = load_fixtures()
    assert len(fixtures) == 5, f"Expected 5 fixtures, loaded {len(fixtures)}"

    scenario_ids = [f["scenario_id"] for f in fixtures]
    assert "scenario_1_direct" in scenario_ids
    assert "scenario_2_peel" in scenario_ids
    assert "scenario_3_cross_chain" in scenario_ids
    assert "scenario_4_mixer" in scenario_ids
    assert "scenario_5_conflicting" in scenario_ids

    for fix in fixtures:
        assert "case" in fix, f"Missing case in {fix.get('scenario_id')}"
        assert "postgres" in fix, f"Missing postgres data in {fix.get('scenario_id')}"
        assert "neo4j" in fix, f"Missing neo4j data in {fix.get('scenario_id')}"


def test_ground_truth_matches_fixtures():
    gt_path = Path(__file__).parent.parent.parent / "scenarios" / "ground_truth.json"
    assert gt_path.exists(), "scenarios/ground_truth.json does not exist"

    with open(gt_path, "r", encoding="utf-8") as f:
        gt = json.load(f)

    scenarios = gt["scenarios"]
    assert len(scenarios) == 5

    # Check holdout default per T3 handoff
    assert gt.get("holdout_default_for_ml_eval") == "scenario_5_conflicting"

    # Check key expectations
    assert scenarios["scenario_1_direct"]["expected_terminal"] == "VASP"
    assert scenarios["scenario_2_peel"]["expected_pattern"] == "peel_chain"
    assert scenarios["scenario_3_cross_chain"]["expected_pattern"] == "cross_chain_bridge"
    assert scenarios["scenario_4_mixer"]["expected_termination"] == "mixer_boundary"
    assert scenarios["scenario_5_conflicting"]["expected_tier_pressure"] == "conflicting_labels_lower_reliability"

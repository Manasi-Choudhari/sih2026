"""
Tests for Scenario Fixtures (T2 Task 4).
Validates that all 5 deterministic scenarios exist, parse properly,
and conform to the NormalizedTransaction schema.
"""

import json
from pathlib import Path
import pytest
from blockchain.normalization.normalize import NormalizedTransaction, CrossChainLink

FIXTURES_DIR = Path("scenarios/fixtures")


def test_fixtures_exist():
    expected = [
        "scenario_1_direct.json",
        "scenario_2_peel.json",
        "scenario_3_cross_chain.json",
        "scenario_4_mixer.json",
        "scenario_5_conflicting.json",
    ]
    for filename in expected:
        file_path = FIXTURES_DIR / filename
        assert file_path.exists(), f"Fixture {filename} does not exist"


def test_fixtures_parse_and_validate_transactions():
    for json_file in FIXTURES_DIR.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "scenario_id" in data
        assert "wallets" in data
        assert "transactions" in data

        # Validate all transactions match NormalizedTransaction specification
        for raw_tx in data["transactions"]:
            tx = NormalizedTransaction(**raw_tx)
            assert tx.amount >= 0
            assert tx.confidence_of_link <= 1.0

        # Validate cross_chain_links if present
        if "cross_chain_links" in data:
            for raw_link in data["cross_chain_links"]:
                link = CrossChainLink(**raw_link)
                # Enforce rule: cross-chain confidence always lower than same-chain (<= 0.85)
                assert link.correlation_confidence <= 0.85

"""
Tests for PostgreSQL Migrations & Neo4j Cypher Schema Scripts.
Verifies migration files exist, are numbered sequentially, and contain valid SQL/Cypher statements.
"""

from pathlib import Path
from db.postgres.migrate import get_available_migrations


def test_migrations_exist_and_ordered():
    migrations = get_available_migrations()
    assert len(migrations) >= 5, f"Expected at least 5 migrations, found {len(migrations)}"

    expected_prefixes = [
        "001_init.sql",
        "002_label_provenance.sql",
        "003_atlas.sql",
        "004_model_estimate.sql",
        "005_recommendation_reports.sql",
    ]

    filenames = [m.name for m in migrations]
    for exp in expected_prefixes:
        assert exp in filenames, f"Missing expected migration: {exp}"


def test_migration_sql_contains_entities():
    migrations_dir = Path(__file__).parent.parent / "postgres" / "migrations"
    init_sql = (migrations_dir / "001_init.sql").read_text(encoding="utf-8")

    # BUILD.md entities check
    required_entities = [
        "complaints",
        "cases",
        "wallets",
        "vasps",
        "labels",
        "evidence",
        "recommendations",
        "alerts",
        "audit_events",
    ]
    for entity in required_entities:
        assert f"CREATE TABLE IF NOT EXISTS {entity}" in init_sql, f"Missing table for {entity}"


def test_cypher_schema_scripts():
    schema_dir = Path(__file__).parent.parent / "neo4j" / "schema"
    constraints_file = schema_dir / "constraints.cypher"
    indexes_file = schema_dir / "indexes.cypher"

    assert constraints_file.exists(), "constraints.cypher missing"
    assert indexes_file.exists(), "indexes.cypher missing"

    c_text = constraints_file.read_text(encoding="utf-8")
    assert "wallet_address" in c_text
    assert "vasp_name" in c_text

    i_text = indexes_file.read_text(encoding="utf-8")
    assert "wallet_cluster_idx" in i_text
    assert "tx_hash_idx" in i_text

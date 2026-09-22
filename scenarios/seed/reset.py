"""
VAJRA (SIH 26183) — Scenario Reset Pipeline
Clears all demo and scenario-seeded data from both PostgreSQL and Neo4j.
Ensures demo repeatability.
"""

from __future__ import annotations

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def reset_neo4j() -> dict[str, int]:
    """Wipes all demo-seeded nodes and relationships from Neo4j (NEO4J_DATABASE=sih2026)."""
    from ml.db.neo4j_client import get_session

    with get_session() as session:
        # Detach delete any node tagged with demo_seed=true or having a scenario_id
        res = session.run(
            """
            MATCH (n)
            WHERE n.demo_seed = true OR n.scenario_id IS NOT NULL
            DETACH DELETE n
            """
        )
        summary = res.consume()
        deleted_nodes = summary.counters.nodes_deleted
        deleted_rels = summary.counters.relationships_deleted
        return {"deleted_nodes": deleted_nodes, "deleted_relationships": deleted_rels}


def reset_postgres() -> dict[str, int]:
    """Wipes demo/scenario case and wallet records from PostgreSQL."""
    import psycopg

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://vajra_user:vajra_password@localhost:5432/vajra_db",
    )

    deleted = {}
    try:
        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cur:
                # We wipe scenario cases and test complaints
                cur.execute(
                    """
                    DELETE FROM cases WHERE case_id LIKE 'case_s%' OR case_id LIKE 'case_test%';
                    """
                )
                deleted["cases"] = cur.rowcount

                cur.execute(
                    """
                    DELETE FROM complaints WHERE complaint_id LIKE 'comp_s%' OR complaint_id LIKE 'comp_test%';
                    """
                )
                deleted["complaints"] = cur.rowcount

                cur.execute(
                    """
                    DELETE FROM wallets WHERE wallet_id LIKE 'w_s%' OR address LIKE 's1_%' OR address LIKE 's2_%' OR address LIKE 's3_%' OR address LIKE 's4_%' OR address LIKE 's5_%';
                    """
                )
                deleted["wallets"] = cur.rowcount

                cur.execute(
                    """
                    DELETE FROM vasps WHERE vasp_id LIKE 'vasp_demo%' OR name = 'DemoExchange';
                    """
                )
                deleted["vasps"] = cur.rowcount
            conn.commit()
    except Exception as exc:
        deleted["error"] = str(exc)

    return deleted


def reset_all() -> dict:
    print("--- Starting VAJRA Database Reset ---")
    pg_res = reset_postgres()
    print(f"PostgreSQL Reset: {pg_res}")

    neo_res = {}
    try:
        neo_res = reset_neo4j()
        print(f"Neo4j Reset: {neo_res}")
    except Exception as exc:
        neo_res["error"] = str(exc)
        print(f"Neo4j Reset Note: {exc}")

    return {"postgres": pg_res, "neo4j": neo_res}


if __name__ == "__main__":
    results = reset_all()
    print("Reset finished:", results)

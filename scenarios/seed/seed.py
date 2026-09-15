"""
VAJRA (SIH 26183) — Scenario Seed Pipeline
Loads the 5 scenario fixtures (/scenarios/fixtures/scenario_*.json) into
both PostgreSQL and Neo4j.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List
from dotenv import load_dotenv

load_dotenv()

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def load_fixtures() -> List[Dict[str, Any]]:
    """Loads all 5 scenario fixture JSON files."""
    fixtures = []
    for fixture_file in sorted(FIXTURES_DIR.glob("scenario_*.json")):
        with open(fixture_file, "r", encoding="utf-8") as f:
            fixtures.append(json.load(f))
    return fixtures


def seed_postgres(fixtures: List[Dict[str, Any]]) -> dict:
    """Inserts complaints, cases, wallets, vasps, labels from fixtures into Postgres."""
    import psycopg

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://vajra_user:vajra_password@localhost:5432/vajra_db",
    )

    stats = {"complaints": 0, "cases": 0, "wallets": 0, "vasps": 0, "labels": 0}
    try:
        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cur:
                for fix in fixtures:
                    case_info = fix.get("case", {})
                    # 1. Complaint
                    cur.execute(
                        """
                        INSERT INTO complaints (complaint_id, fraud_category, reported_amount, currency, victim_ref)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (complaint_id) DO UPDATE SET
                            fraud_category = EXCLUDED.fraud_category,
                            reported_amount = EXCLUDED.reported_amount;
                        """,
                        (
                            case_info["complaint_id"],
                            case_info["fraud_category"],
                            case_info["reported_amount"],
                            case_info["currency"],
                            case_info["victim_ref"],
                        ),
                    )
                    stats["complaints"] += 1

                    # 2. Case
                    cur.execute(
                        """
                        INSERT INTO cases (case_id, complaint_id, status, assigned_investigator)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (case_id) DO UPDATE SET
                            status = EXCLUDED.status,
                            assigned_investigator = EXCLUDED.assigned_investigator;
                        """,
                        (
                            case_info["case_id"],
                            case_info["complaint_id"],
                            case_info["status"],
                            case_info["assigned_investigator"],
                        ),
                    )
                    stats["cases"] += 1

                    # 3. Wallets
                    pg_data = fix.get("postgres", {})
                    for w in pg_data.get("wallets", []):
                        cur.execute(
                            """
                            INSERT INTO wallets (wallet_id, address, chain, cluster_id, entity_type)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (address) DO UPDATE SET
                                cluster_id = EXCLUDED.cluster_id,
                                entity_type = EXCLUDED.entity_type;
                            """,
                            (
                                w["wallet_id"],
                                w["address"],
                                w["chain"],
                                w.get("cluster_id"),
                                w.get("entity_type", "eoa"),
                            ),
                        )
                        stats["wallets"] += 1

                    # 4. VASPs
                    for v in pg_data.get("vasps", []):
                        cur.execute(
                            """
                            INSERT INTO vasps (vasp_id, name, known_addresses)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (name) DO UPDATE SET
                                known_addresses = EXCLUDED.known_addresses;
                            """,
                            (v["vasp_id"], v["name"], v.get("known_addresses", [])),
                        )
                        stats["vasps"] += 1

                    # 5. Labels
                    for lbl in pg_data.get("labels", []):
                        cur.execute(
                            """
                            INSERT INTO labels (label_id, wallet_id, source, label_text, confidence_tier, confidence)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (label_id) DO UPDATE SET
                                confidence_tier = EXCLUDED.confidence_tier,
                                confidence = EXCLUDED.confidence;
                            """,
                            (
                                lbl["label_id"],
                                lbl["wallet_id"],
                                lbl["source"],
                                lbl["label_text"],
                                lbl["confidence_tier"],
                                lbl.get("confidence", 1.0),
                            ),
                        )
                        stats["labels"] += 1
            conn.commit()
    except Exception as exc:
        stats["error"] = str(exc)

    return stats


def seed_neo4j(fixtures: List[Dict[str, Any]]) -> dict:
    """Inserts nodes and relationships into Neo4j database `sih2026`."""
    from ml.db.neo4j_client import get_session

    stats = {"nodes": 0, "relationships": 0}
    with get_session() as session:
        for fix in fixtures:
            neo_data = fix.get("neo4j", {})

            # Insert Nodes
            for node in neo_data.get("nodes", []):
                lbl = node["label"]
                props = node.get("properties", {})
                prop_keys = ", ".join(f"{k}: ${k}" for k in props.keys())
                query = f"MERGE (n:{lbl} {{{prop_keys}}})"
                session.run(query, **props)
                stats["nodes"] += 1

            # Insert Relationships
            for rel in neo_data.get("relationships", []):
                rel_type = rel["type"]
                from_addr = rel["from"]
                to_addr = rel["to"]
                from_lbl = rel.get("from_label", "Wallet")
                to_lbl = rel.get("to_label", "Wallet")
                props = rel.get("properties", {})

                # Match by address or name depending on label
                from_match = "w1.address = $from_addr" if from_lbl == "Wallet" else "w1.name = $from_addr"
                if to_lbl == "Wallet":
                    to_match = "w2.address = $to_addr"
                elif to_lbl == "VASP":
                    to_match = "w2.name = $to_addr"
                elif to_lbl == "Label":
                    to_match = "w2.label_text = $to_addr"
                else:
                    to_match = "w2.address = $to_addr"

                prop_assign = ", ".join(f"r.{k} = ${k}" for k in props.keys())
                query = f"""
                MATCH (w1:{from_lbl}), (w2:{to_lbl})
                WHERE {from_match} AND {to_match}
                MERGE (w1)-[r:{rel_type}]->(w2)
                ON CREATE SET {prop_assign}
                """
                session.run(query, from_addr=from_addr, to_addr=to_addr, **props)
                stats["relationships"] += 1

    return stats


def seed_all() -> dict:
    fixtures = load_fixtures()
    print(f"Loaded {len(fixtures)} scenario fixtures.")

    pg_stats = seed_postgres(fixtures)
    print(f"PostgreSQL Seeding: {pg_stats}")

    neo_stats = {}
    try:
        neo_stats = seed_neo4j(fixtures)
        print(f"Neo4j Seeding: {neo_stats}")
    except Exception as exc:
        neo_stats["error"] = str(exc)
        print(f"Neo4j Seeding Note: {exc}")

    return {"postgres": pg_stats, "neo4j": neo_stats}


if __name__ == "__main__":
    res = seed_all()
    print("Seed pipeline completed:", res)

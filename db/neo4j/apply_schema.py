"""
VAJRA (SIH 26183) — Neo4j Schema Applier
Executes Cypher constraints and indexes against NEO4J_DATABASE (default: sih2026).
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SCHEMA_DIR = Path(__file__).parent / "schema"


def apply_cypher_file(session, file_path: Path) -> list[str]:
    """Reads a .cypher file, splits into individual statements, and runs each."""
    content = file_path.read_text(encoding="utf-8")
    statements = []
    current_stmt = []

    for line in content.splitlines():
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("//"):
            continue
        current_stmt.append(line)
        if line_clean.endswith(";"):
            statements.append("\n".join(current_stmt).rstrip(";"))
            current_stmt = []

    if current_stmt:
        remaining = "\n".join(current_stmt).strip()
        if remaining:
            statements.append(remaining)

    results = []
    for stmt in statements:
        try:
            session.run(stmt)
            results.append(f"SUCCESS: {stmt[:60]}...")
        except Exception as exc:
            results.append(f"ERROR: {exc} | {stmt[:60]}...")
    return results


def apply_neo4j_schema() -> dict[str, list[str]]:
    """Applies constraints.cypher and indexes.cypher to the configured Neo4j instance."""
    from ml.db.neo4j_client import get_session

    results = {}
    with get_session() as session:
        for script_name in ["constraints.cypher", "indexes.cypher"]:
            script_path = SCHEMA_DIR / script_name
            if script_path.exists():
                print(f"Applying Neo4j schema: {script_name}...")
                results[script_name] = apply_cypher_file(session, script_path)
    return results


if __name__ == "__main__":
    try:
        res = apply_neo4j_schema()
        for script, logs in res.items():
            print(f"--- {script} ---")
            for log in logs:
                print(f"  {log}")
    except Exception as exc:
        print(f"Neo4j connection error: {exc}")

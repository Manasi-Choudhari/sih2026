"""Neo4j connection helpers for T3 feature extraction."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from neo4j import Driver, GraphDatabase

# Load repo-root .env
_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env")


def neo4j_settings() -> dict[str, str]:
    return {
        "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        "user": os.getenv("NEO4J_USER", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD", ""),
        "database": os.getenv("NEO4J_DATABASE", "sih2026"),
    }


@lru_cache(maxsize=1)
def get_driver() -> Driver:
    cfg = neo4j_settings()
    if not cfg["password"]:
        raise RuntimeError("NEO4J_PASSWORD missing — set it in .env")
    driver = GraphDatabase.driver(cfg["uri"], auth=(cfg["user"], cfg["password"]))
    driver.verify_connectivity()
    return driver


def get_session():
    cfg = neo4j_settings()
    return get_driver().session(database=cfg["database"])


def run_cypher(query: str, **params):
    with get_session() as session:
        return session.run(query, **params).data()


def ping() -> dict:
    cfg = neo4j_settings()
    with get_session() as session:
        row = session.run(
            "RETURN $db AS database, count { MATCH (n) } AS node_count",
            db=cfg["database"],
        ).single()
        return dict(row) if row else {}

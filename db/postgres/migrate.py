"""
VAJRA (SIH 26183) — PostgreSQL Migration Runner
Applies numbered SQL migrations in /db/postgres/migrations/ in sequential order.
Tracks applied versions in `schema_migrations`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv

load_dotenv()

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def get_connection():
    """Returns a psycopg connection using DATABASE_URL."""
    import psycopg

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://vajra_user:vajra_password@localhost:5432/vajra_db",
    )
    return psycopg.connect(database_url)


def init_migration_table(conn) -> None:
    """Ensure the schema_migrations tracking table exists."""
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
    conn.commit()


def get_applied_migrations(conn) -> set[str]:
    """Fetch all migration versions already applied."""
    with conn.cursor() as cur:
        cur.execute("SELECT version FROM schema_migrations ORDER BY version;")
        rows = cur.fetchall()
        return {r[0] for r in rows}


def get_available_migrations() -> List[Path]:
    """Find all .sql migration files ordered by filename."""
    if not MIGRATIONS_DIR.exists():
        return []
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def run_migrations(dry_run: bool = False) -> List[Tuple[str, str]]:
    """
    Applies all pending migrations.
    Returns list of (version, status).
    """
    available = get_available_migrations()
    if not available:
        print("No migration files found.")
        return []

    try:
        conn = get_connection()
    except Exception as exc:
        print(f"Failed to connect to PostgreSQL: {exc}")
        print("Set DATABASE_URL in .env or environment.")
        return []

    results = []
    with conn:
        init_migration_table(conn)
        applied = get_applied_migrations(conn)

        for migration_path in available:
            version = migration_path.name
            if version in applied:
                results.append((version, "ALREADY_APPLIED"))
                continue

            print(f"Applying migration: {version}...")
            if dry_run:
                results.append((version, "DRY_RUN"))
                continue

            sql_content = migration_path.read_text(encoding="utf-8")
            with conn.cursor() as cur:
                cur.execute(sql_content)
                cur.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s);",
                    (version,),
                )
            conn.commit()
            print(f"Successfully applied {version}.")
            results.append((version, "APPLIED"))

    return results


if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    print(f"Starting migrations (dry_run={is_dry})...")
    res = run_migrations(dry_run=is_dry)
    for v, st in res:
        print(f"  [{st}] {v}")

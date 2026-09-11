# VAJRA Docker Compose Stack (T6)

This directory contains the central multi-service container definition for the VAJRA system (SIH 26183).

## Services Included

| Service | Technology | Port(s) | Description | Owner |
|---|---|---|---|---|
| `postgres` | PostgreSQL 16 | 5432 | Relational DB: complaints, cases, evidence metadata, model estimates, audit events | T5 |
| `neo4j` | Neo4j Community 5.18 | 7474 (UI), 7687 (Bolt) | Transaction graph, wallet addresses, cross-chain links, VASP labels | T5 / T1 / T2 |
| `redis` | Redis 7 | 6379 | Job queue, caching, token rate limiting | T5 / T6 |
| `minio` | MinIO S3 | 9000 (API), 9001 (Console) | Evidence ledger files, reports, export bundles | T5 / T6 |
| `backend` | FastAPI (Python) | 8000 | Core REST APIs, trace engine, ATLAS, VASP attribution | T1 |
| `ml` | XGBoost/CUDA + Anomaly | 8001 | Risk scoring and anomaly signals | T3 |
| `frontend` | Next.js 14 | 3000 | Investigator UX, graph visualization, ATLAS panel | T4 |

## Quick Start

### 1. Copy Environment Configuration
```bash
cp .env.example .env
```

### 2. Start Full Stack
```bash
docker compose -f infra/docker/docker-compose.yml up -d
```

### 3. Check Service Health
```bash
docker compose -f infra/docker/docker-compose.yml ps
```

### 4. Stop Stack
```bash
docker compose -f infra/docker/docker-compose.yml down
```

## Credential Defaults (Local Development)
- **Postgres:** User: `vajra_user`, Password: `vajra_password`, DB: `vajra_db`
- **Neo4j:** User: `neo4j`, Password: `vajra_neo4j_password`, Database: `sih2026`
- **MinIO Console:** User: `vajra_minio_admin`, Password: `vajra_minio_secret_password`

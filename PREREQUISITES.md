# PREREQUISITES.md — VAJRA (SIH 26183) — Setup Before Day 1

Everyone should finish the **Shared** section before Day 1 stand-up. Do the account signups (API keys) at least a day early — some take hours to approve.

## Shared (every teammate, no exceptions)
- [ ] **Git + GitHub access** to the team repo, correct branch permissions.
- [ ] **Create your personal branch off `dev`** before Day 1 coding starts — one long-lived branch per teammate: `t1-backend`, `t2-blockchain`, `t3-ml`, `t4-frontend`, `t5-db`, `t6-infra`. Never commit directly to `main`, and don't commit directly to `dev` either — always via PR (see `INTEGRATION.md`'s Git Workflow section for the full branch/merge/review rules).
- [ ] **Docker Desktop** (or Docker Engine + Compose v2) installed and running — confirm with `docker compose version`.
- [ ] **Python 3.11+** installed — confirm with `python3 --version`.
- [ ] **Node.js 20 LTS + npm** installed — confirm with `node --version`.
- [ ] Clone the repo and run `docker compose up` once (even if empty/stub) to confirm your machine can run the full stack — flag immediately if it can't.
- [ ] Read `BUILD.md` fully (scope lock, shared contracts, file-ownership tree) before touching code.
- [ ] Read your own `BUILD_Tx_*.md` file fully.
- [ ] Agree on a shared `.env.example` — never commit a real `.env` (secrets go here, not in git).
- [ ] Install an API-testing tool: Postman, Insomnia, or `curl`/`httpie` comfort level.
- [ ] Join whatever stand-up/chat channel the team uses (Slack/Discord/WhatsApp) for the daily rhythm in `INTEGRATION.md`.

---

## T1 — Backend + Investigation Logic Lead
- [ ] Python virtual env tooling: `venv` or `poetry`/`uv`.
- [ ] **FastAPI + Uvicorn** familiarity — confirm you can run a "hello world" FastAPI app locally.
- [ ] **Neo4j Python driver** (`neo4j` package) and basic Cypher query literacy — you'll be querying T5's graph directly.
- [ ] **OpenAPI/Swagger** familiarity — you own `/backend/api/openapi.yaml`, the single most depended-on file in the repo.
- [ ] Local Postgres client (e.g. `psql`, or a GUI like TablePlus/DBeaver) to sanity-check T5's schema.
- [ ] Read T3's `T3_TEAM_HANDOFF.md` before Day 6 — you're integrating `predict.py` directly.
- [ ] Confirm with T3 whether ML integration is a direct Python import or an HTTP call, before you scaffold `/backend/api/`.

## T2 — Blockchain Engineer
- [ ] **Etherscan API key** — sign up at etherscan.io, free tier is enough for MVP volume; approval is usually instant but budget time.
- [ ] **Blockchair (or equivalent BTC explorer) API key** — sign up early, some plans have manual review.
- [ ] Basic familiarity with BTC UTXO model vs ETH account model — you're normalizing both into one schema, so know the difference going in.
- [ ] `requests` (Python) or equivalent HTTP client comfort, plus retry/backoff pattern knowledge (rate limits are real on free-tier explorer APIs).
- [ ] Neo4j Python driver — you write directly into T5's graph.
- [ ] A worked example of a real BTC and a real ETH address you can test adapters against before switching to synthetic fixtures.

## T3 — AI/ML + Analytics *(already assigned, ahead of the others)*
- [ ] Confirm **CUDA-capable GPU** availability for training — if you don't have one locally, arrange access (Colab, cloud instance, or a teammate's machine) before Day 6.
- [ ] `xgboost` (GPU build) and `scikit-learn` (Isolation Forest) installed and verified working.
- [ ] Neo4j Python driver, plus access to the actual `NEO4J_DATABASE=sih2026` instance.
- [ ] Confirm the **CPU fallback path** actually runs end-to-end on a non-GPU machine before Day 9 — don't assume, test it yourself once.
- [ ] Share your `feature_spec.py` contract with T1/T2 by Day 1 so they know what fields to supply.
- [ ] Have `T3_TEAM_HANDOFF.md` ready to share with T1/T5/T6 — they're already depending on it.

## T4 — Frontend / Investigator UX
- [ ] **Next.js** (React) project scaffolding familiarity — `npx create-next-app` comfort.
- [ ] TypeScript comfort — you maintain typed API client code generated from T1's OpenAPI spec.
- [ ] A graph-visualization library decision made early (e.g. `react-flow`, `vis-network`, `cytoscape.js`) — confirm with T1 what shape `/cases/{id}/graph` returns before picking one, so you don't have to re-plumb data later.
- [ ] Design/mockup tool of choice (Figma or similar) if you want to sketch the 8–9 screens before building — optional but saves rework.
- [ ] Node package manager preference (`npm`/`pnpm`/`yarn`) agreed with the team so lockfiles don't conflict.

## T5 — Database Engineer
- [ ] **PostgreSQL** installed locally (or via Docker) — confirm `psql` connects.
- [ ] **Neo4j** installed locally (Desktop or Docker) — confirm Cypher Browser or `cypher-shell` connects.
- [ ] A migration tool decision made with T1 (e.g. `alembic` for Python, or raw numbered SQL files as in the file tree) — pick one before Day 1's schema freeze.
- [ ] Familiarity with SHA-256 hashing in your chosen language, for the Evidence Ledger's hash-chain logic.
- [ ] Confirm you can load T3's `scenario_ground_truth.json` proposal and merge format before Day 2.

## T6 — DevOps / Security + QA-Demo Lead
- [ ] **Docker Compose** authoring experience — you own the single Compose file every teammate runs daily starting Day 1.
- [ ] Basic CI config experience (GitHub Actions or equivalent) for the lint/test-on-push pipeline.
- [ ] JWT library familiarity in your chosen backend language (works with T1's FastAPI stack).
- [ ] A plan for testing the **offline/no-internet demo path** on a genuinely disconnected machine before Day 9 — don't just simulate it, actually pull a network cable or use airplane mode once.
- [ ] Confirm you have (or can get) access to a machine **without a GPU** to validate T3's CPU fallback — this is your Day 9 responsibility, not T3's.
- [ ] Rate-limiting library/middleware decision made early (matches T1's FastAPI stack).

---

## Before Day 1 Stand-up — Final Checklist
- [ ] Everyone has run `docker compose up` successfully at least once.
- [ ] All required API keys (T2's explorer keys) are requested, even if not yet approved.
- [ ] T1 and T5 have a 15-minute call scheduled to freeze the schema/contract together (they're the Day 1 bottleneck for everyone else).
- [ ] T3 has shared `T3_TEAM_HANDOFF.md` with T1, T5, and T6.
- [ ] Everyone knows their owned file paths from `BUILD.md`'s file-structure tree and won't write outside them.
- [ ] Everyone has created their personal branch off `dev` and understands the PR/review rule in `INTEGRATION.md` (contract-file owner reviews any PR touching their file).

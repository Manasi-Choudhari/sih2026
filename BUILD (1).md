# BUILD.md — VAJRA (SIH 26183: Real-Time Crypto Fraud Attribution)
> ⚠️ AGENT INSTRUCTIONS: Build ONLY what is listed here. Do not add features, do not infer requirements, do not improve on the spec. If something is unclear, output a comment `// UNCLEAR: [question]` and stop. Do not proceed past unclear points.

Compressed from the team's existing 20-day / 5-person plan into a **10-day / 6-person** plan. All module numbers (M01–M21), evidence-tier logic, and algorithms below are carried over unchanged from the team's Master Blueprint and FINAL BUILD document — only the timeline and team split have been re-cut.

## Project Overview
Given one victim-reported wallet address, VAJRA traces the funds across a transaction graph, resolves cross-chain hops, and produces an **evidence-tiered VASP (exchange) attribution** — not a bare risk score — together with a tamper-evident evidence trail an investigator can act on. The system's differentiators are the **ATLAS** module (which tries to disprove its own leading attribution before showing it to the investigator) and the **hash-chained Evidence Ledger**.

## Tech Stack
| Layer | Technology |
|---|---|
| Frontend | React / Next.js |
| Backend | FastAPI / Python |
| Graph DB | Neo4j Community |
| Relational DB | PostgreSQL |
| Queue/cache | Redis + Celery/RQ |
| ML | XGBoost (GPU/CUDA, `ML_DEVICE=cuda`, with CPU/CSV fallback) for risk scoring; Isolation Forest (CPU) for anomaly signal |
| Blockchain access | Explorer APIs (Etherscan, Blockchair, etc.) — MVP only, no direct nodes |
| Object storage | MinIO / S3-compatible |
| Auth | JWT + RBAC |
| Deployment | Docker Compose (must run fully offline for the demo) |

## Scope Lock (do not deviate)
- **Live chains:** Bitcoin + Ethereum only.
- **Cross-chain:** exactly ONE bridge pattern, built and tested against synthetic fixtures (lock/burn ↔ mint/release), always carrying lower default confidence than a same-chain link.
- **NCRP/SAHYOG:** mock adapter only, visibly labeled "Simulated" everywhere it appears in UI/reports.
- **Explicitly out of scope (do not build, do not gold-plate):** multi-channel alert delivery, auto-executed freeze requests, 4+ live blockchains, Monero/privacy-chain tracing, LLM-driven decision logic, typology classification, cross-case memory, GNN models, full production node infrastructure.
- If a P0 item and a polish item compete for time, P0 wins. Simplify UI before cutting any P0 backend/logic item.

### Priority tiers (carried from Master Blueprint, unchanged)
- **P0 (cannot be dropped):** wallet validation, BTC+ETH ingestion, normalized graph, bounded trace, deterministic pattern rules, VASP attribution with evidence tiers, three-number confidence framework, one cross-chain bridge, mixer termination, ATLAS, Evidence Ledger, offline demo.
- **P1 (cut only if P0 at risk):** recommendation engine, VASP request compiler, standardized report, RBAC/auth, core dashboard, ML risk score, single alert channel.
- **P2/P3 (do not build in 10 days):** anything not listed above.

## Shared Contracts (ALL agents must honor these)

### Data Models — Neo4j (graph)
```
(:Wallet {address, chain, first_seen, last_seen, cluster_id, entity_type})
(:VASP {name, known_addresses, last_verified})
(:Label {source, label_text, confidence, first_seen, last_verified})

(:Wallet)-[:TRANSACTION {
    tx_hash, chain, block_height, timestamp, amount, asset,
    direction, is_bridge_leg, confidence_of_link
}]->(:Wallet)

(:Wallet)-[:CROSS_CHAIN_LINK {
    source_chain_tx, dest_chain_tx, bridge_contract,
    correlation_method, correlation_confidence
}]->(:Wallet)

(:Wallet)-[:LABELED_AS {confidence_tier}]->(:VASP)
```

### Data Models — PostgreSQL (relational)
| Entity | Key fields | Owner |
|---|---|---|
| Complaint | complaint_id, reported_at, fraud_category, reported_amount, currency, victim_ref | T5 |
| Case | case_id, complaint_id, status, assigned_investigator, created_at | T1/T5 |
| Wallet | wallet_id, address, chain, first_seen, cluster_id | T2/T5 |
| VASP | vasp_id, name | T1/T5 |
| Label | label_id, wallet_id, source, label_text, confidence_tier, first_seen, last_verified | T1/T5 |
| Evidence | evidence_id, case_id, type, source, content, content_hash, prev_hash, software_version | T5 |
| Recommendation | rec_id, case_id, finding, evidence_ids, confidence, action, approval_status | T1 |
| Alert | alert_id, case_id, triggered_at, rule_fired, delivered_at | T5/T6 |
| AuditEvent | event_id, actor_id, action, target_id, timestamp | T5/T6 |
| ModelEstimate | estimate_id, case_id, wallet_id, model_name, model_version, score, label, top_features (JSONB), generated_at, is_model_output (always true) | T5 (schema) / T3 (writer) |

### API Endpoints (minimum set)
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /auth/login | Authentication |
| POST | /cases | Create case from complaint/wallet |
| GET | /cases | Investigation queue |
| GET | /cases/{id} | Case overview |
| GET | /cases/{id}/graph | Graph/path visualization data |
| GET | /cases/{id}/attribution | VASP candidates + evidence tiers |
| GET | /cases/{id}/atlas | Alternatives, contradictions, robustness |
| GET | /cases/{id}/evidence | Evidence ledger entries |
| GET/POST | /cases/{id}/recommendations | View/create/approve recommendations |
| POST | /cases/{id}/report | Generate standardized report |
| GET | /cases/{id}/verify | Verify hash chain |
| GET | /cases/{id}/audit | Audit events |
| POST | /external/case-update | Simulated NCRP/SAHYOG callback |

### Evidence Tier Framework (VASP attribution — non-negotiable)
| Tier | Rule |
|---|---|
| Strong | Direct 0–1 hop to independently confirmed active VASP address, recent/reliable source, no obfuscation. |
| Medium | Single crowdsourced label OR clean multi-hop path to a strong label with good timing/amount correlation. |
| Weak | Stale/low-reputation label, conflicting labels, weak clustering, or indirect path. |
| Unknown | No reliable label at terminal point — must be shown explicitly, never hidden. |

Three numbers (risk score, attribution confidence, ML probability) are **never merged into one number** and are always shown together.

### Trace Engine Control Limits
- Max depth: hard ceiling, initial target 8 hops.
- Value cutoff: stop branches once cumulative value falls below ~1% of origin.
- Fan-out cap: large fan-out terminates as a mixer-scale/pattern event, not a normal branch.
- Termination states: VASP reached, mixer/privacy boundary, depth/value limit, unresolved/cold data.

### Environment Variables
| Var | Purpose | Owner |
|---|---|---|
| `DATABASE_URL` | Postgres connection | T5 |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | Graph DB connection | T5 |
| `REDIS_URL` | Queue/cache | T5/T6 |
| `JWT_SECRET` | Auth signing | T6 |
| `EXPLORER_API_KEY_BTC`, `EXPLORER_API_KEY_ETH` | Blockchain explorer access | T2 |
| `MODEL_ARTIFACT_PATH` | ML model versioning | T3 |
| `NEO4J_DATABASE` | Named Neo4j database (`sih2026`) | T3/T5 |
| `ML_DEVICE` | `cuda` for GPU training/serving, must have a documented CPU fallback for judge laptops without a GPU | T3/T6 |
| `NCRP_MOCK_MODE` | Always `true` in this build | T1 |

### File Structure (root, full tree, single-owner per path)
Every path below has exactly one owner. If two agents need to touch the same file, that file lives in a `shared/` folder instead and edits go through T1 (contracts) or T5 (schema) — never two agents editing the same non-shared file directly.

```
/backend                          [T1 — owner]
  /case_management/                  case.py, queue.py, status.py
  /trace/                            engine.py, limits.py, scoring.py
  /attribution/                      tiers.py, candidates.py, provenance_rules.py
  /patterns/                         peel_chain.py, fanout.py, structuring.py, mixer_boundary.py
  /atlas/                            alternatives.py, contradictions.py, robustness.py
  /information_gap/                  ranking.py
  /recommendation/                   engine.py, approval_gate.py
  /reporting/                        report_generator.py
  /external/                         ncrp_mock.py
  /api/                              routes/*.py, openapi.yaml   <- CONTRACT FILE, see below
  main.py, requirements.txt

/blockchain                       [T2 — owner]
  /chain_detection/                  detect.py
  /adapters/btc/                     client.py, parser.py
  /adapters/eth/                     client.py, parser.py
  /indexer/                          worker.py, scheduler.py
  /normalization/                    normalize.py            <- writes to shared NormalizedTransaction schema
  /cross_chain/                      correlator.py, bridge_registry.py
  requirements.txt

/ml                                [T3 — owner]
  /features/                         pipeline.py, feature_spec.py   <- CONTRACT FILE
                                      neo4j_extract.py
  /db/                                neo4j_client.py
  /data/                              seed_neo4j.py (demo-only, tagged demo_seed:true — retired once T2 fixtures land)
                                      scenario_ground_truth.json (proposal — T5 merges into /scenarios)
                                      generate_synthetic.py
                                      /synthetic/wallet_features.csv (fallback if Neo4j empty)
  /risk_model/                       train.py, predict.py (score_wallet, score_wallet_from_neo4j), evaluate.py
  /anomaly/                          detect.py
  /evaluation/                       metrics.py, versioning.py
  /artifacts/                        risk_scoring_xgb_gpu_latest.joblib, anomaly_isolation_forest_latest.joblib, risk_metrics.json (gitignored, baked into offline demo image by T6)
  requirements.txt

/frontend                          [T4 — owner]
  /app/                               (login)/, (queue)/, (case)/[id]/overview, graph, attribution, atlas, evidence, recommendations, report, audit
  /components/graph/                  GraphView.tsx, PathDetail.tsx
  /components/attribution/            AttributionCard.tsx, EvidenceTierBadge.tsx
  /components/atlas/                  AtlasPanel.tsx
  /components/evidence/               LedgerList.tsx, VerifyButton.tsx
  /components/shared/                 ThreeNumberCard.tsx, SimulatedBadge.tsx
  /lib/api/                           client.ts, types.ts        <- generated FROM /backend/api/openapi.yaml, never hand-edited out of sync
  package.json

/db                                [T5 — owner]
  /postgres/migrations/               001_init.sql, 002_evidence.sql, ...
  /neo4j/schema/                      constraints.cypher, indexes.cypher
  /evidence_ledger/                   hash_chain.py, verify.py
  requirements.txt

/infra                             [T6 — owner]
  /docker/                            docker-compose.yml, Dockerfile.backend, Dockerfile.frontend, Dockerfile.ml
  /auth/                              jwt.py, rbac.py
  /rate_limiting/                     middleware.py
  /audit/                             audit_middleware.py
  /demo/                              offline_bundle.sh, reset.sh, fallback.md
  ci.yml

/scenarios                        [shared — see rule below]
  /fixtures/                          scenario_1_direct.json ... scenario_5_conflicting.json
  /seed/                              seed.py, reset.py
  ground_truth.json

/docs                              [shared — see rule below]
  architecture_decision_record.md
  api_notes.md
  demo_script.md
```

**Shared-folder rule (`/scenarios`, `/docs`):** these are the only folders more than one agent writes to.
- `/scenarios/fixtures/`: T2 owns chain data per fixture, T3 owns ground-truth labels per fixture, T5 owns the seed/reset script mechanics — each edits their own sub-concern in the same JSON file, but **T5 merges**; T2/T3 propose via diff, don't push directly.
- `/docs/`: any agent may append, no agent may delete another's section.

**Two hard contract files everyone reads, only one agent writes:**
- `/backend/api/openapi.yaml` — T1 writes. Everyone else treats it as read-only and regenerates their own client/types from it (T4's `/lib/api/types.ts` is generated, never hand-edited).
- `/ml/features/feature_spec.py` — T3 writes. T1/T2 read it to know what feature fields to supply; they don't edit it.

**Conflict-avoidance rules for all agents:**
1. Never write outside your owned path (see per-agent BUILD_Tx.md file for your exact paths).
2. If you need a change in another agent's file, write the request as a comment in `/docs/api_notes.md` and wait — don't edit it yourself.
3. Contract files (`openapi.yaml`, `feature_spec.py`, DB migrations) only change with an explicit team decision, and only the listed owner commits the change.
4. Merge order on shared files: T5 has final merge authority on `/scenarios/fixtures/`, T1 has final merge authority on anything touching `/backend/api/`.

## 10-Day Build Timeline (compressed from the 20-day plan — each day below = 2 old days)
| Day | Goal | Lead | Work | Exit deliverable |
|---|---|---|---|---|
| 1 | Freeze | ALL, T1/T5 heaviest | Freeze module map, P0/P1/P2 scope, BTC+ETH live scope, one cross-chain scenario, simulated NCRP. Freeze Postgres + Neo4j schemas, API OpenAPI skeleton, Docker/repo/CI. | Repo live, schemas committed, branch rules set, architecture decision record written. |
| 2 | Synthetic world + ingestion | T2 lead; T3/T5 seed; T4 shell | Build the 5 deterministic scenarios (direct VASP, peel chain, cross-chain, mixer boundary, conflicting labels) with expected outputs. Implement BTC + ETH adapters (raw fetch, pagination, retries, caching) — no tracing yet. | Scenario fixtures + ground-truth cases + seed script. Raw data available via adapter interface. |
| 3 | Graph + Trace v1 | T1 lead; T2 graph support; T4 graph UI | Normalize raw data into common schema, write Neo4j graph, implement lookup/neighborhood query. Implement bounded priority/BFS trace with depth/value/time/fan-out limits and terminal states. | Neo4j populated; Scenario 1 trace passes with a stable path response. |
| 4 | Attribution + Patterns | T1 lead; T5 labels; T2 evidence paths; T3/T4 support | Implement label provenance/freshness/evidence tiers + branch-specific candidates. Run deterministic pattern rules over materialized subgraphs (peel chain, rapid forwarding, fan-out/fan-in, structuring, mixer boundary). | Direct + conflicting-label scenarios produce correct tiered outputs; Scenarios 2/4 pass with visible pattern explanations. |
| 5 | ATLAS + Cross-chain | T1 lead (ATLAS); T2 lead (cross-chain); T3 scoring; T4 UI; T5 persistence | Generate 3–4 competing hypotheses / contradictions / missing evidence / robustness result. Implement the one bridge pattern: lock/burn ↔ mint/release correlation by amount/time/asset. | ATLAS challenges Scenario 1's attribution. Scenario 3 shows a CROSS_CHAIN_LINK with explicit uncertainty. |
| 6 | Evidence Ledger + ML risk model | T5 lead (ledger); T3 lead (ML); T1 evidence service; T2 features | Canonicalize evidence, SHA-256 hash chain, verify endpoint, tamper test. Extract features, train Random Forest/Gradient Boosting risk model, held-out evaluation, model versioning. | Ledger PASS + deliberate FAIL demonstrated. Risk model metrics documented; API returns model estimate separately from rule output. |
| 7 | Info-gap + Frontend core | T3/T1 (info-gap); T4 lead (frontend); all API owners support | Implement information-gap and next-best-action ranking. Build all core screens (login, queue, overview, graph, attribution, ATLAS, evidence, recommendation, audit) against real APIs — no hard-coded demo JSON. | Medium-confidence case yields a reasoned next action. All core screens work against the real backend. |
| 8 | Full integration + Security/report/mock | ALL; T5 lead (security); T1 (report) | Run the full pipeline end-to-end, fix contracts/state/error handling. Add RBAC, audit, rate limiting; standardized report generator; simulated NCRP/SAHYOG callback; human approval gate. | Complaint → trace → attribution → ATLAS → recommendation → ledger works end-to-end. Unauthorized action blocked; report generated and auditable. |
| 9 | Scenario acceptance + Offline demo | ALL; T6 lead (demo packaging) | Run all 5 scenarios twice, measure correctness/latency, fix P0 defects only. Pre-index demo data, package Docker Compose, build fallback behavior, scripted data reset. | 5/5 scenarios pass. Fresh machine/local environment runs the demo with no internet required. |
| 10 | Adversarial testing + Freeze/rehearsal | ALL | Adversarial tests (poisoned/stale/conflicting labels, mixer, fan-out explosion, ML/rule disagreement, tampering, unauthorized action). Clean install, full smoke test, 3 timed rehearsals, judge Q&A prep, freeze code/data/models. | Adversarial test report, no unsupported claims. Competition-ready build; demo repeatedly succeeds within time budget. |

## Team Overview
| Member | Role | Owns | Integrates With |
|---|---|---|---|
| T1 | Backend + Investigation Logic Lead | Case mgmt, trace engine, VASP attribution, ATLAS, info-gap, recommendation engine, core APIs | Everyone (API contracts are the spine) |
| T2 | Blockchain Engineer | Chain detection, BTC/ETH adapters, indexer, normalization, cross-chain correlator | T1 (graph queries), T5 (schema) |
| T3 | AI/ML + Analytics *(already assigned)* | Feature engineering, risk scoring model, anomaly signal | T1 (API integration), T2 (features from graph) |
| T4 | Frontend / Investigator UX | All screens: queue, case overview, graph, attribution, ATLAS, evidence ledger, recommendations, report, audit | T1 (all API contracts) |
| T5 | Database Engineer | Postgres schema, Neo4j schema, migrations, evidence ledger persistence, label provenance DB | T1, T2, T6 |
| T6 | DevOps / Security + QA-Demo Lead | Docker Compose, RBAC/auth, rate limiting, audit logging, offline demo packaging, scenario acceptance testing, judge Q&A prep | Everyone (cross-cutting from Day 1) |

## DO NOT Section (applies to all agents)
- Do not add any feature not listed in this document.
- Do not change shared contract definitions without a whole-team decision (interfaces are frozen after Day 1–2).
- Do not rename files or folders.
- Do not install packages not listed in the tech stack.
- Do not use your own judgment to "improve" the code — flag `// UNCLEAR:` and stop instead.
- Do not build anything tagged P2/P3.
- Do not run live pattern detection mid-traversal — materialize the subgraph first, then run deterministic rules over it.
- Do not let the ML model output be treated as a fact or final attribution — it is always labeled `model_output` and the deterministic rules win on disagreement.

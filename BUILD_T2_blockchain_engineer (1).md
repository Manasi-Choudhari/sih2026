# BUILD_T2.md — Blockchain Engineer
> ⚠️ AGENT INSTRUCTIONS: You are building ONLY the items in this file. Nothing else. Build exactly as specified.

## Your Scope
Chain detection, BTC + ETH adapters, the background indexer, transaction normalization, and the cross-chain correlation engine (the one bridge pattern in scope). No Tron/other chains, no privacy chains.

## Your Files
- `/blockchain/chain_detection/` — address format/checksum-based chain detection
- `/blockchain/adapters/btc/`, `/blockchain/adapters/eth/` — explorer API adapters
- `/blockchain/indexer/` — background ingestion pipeline
- `/blockchain/normalization/` — raw → `NormalizedTransaction` schema
- `/blockchain/cross_chain/` — bridge correlator

## Your Tasks (ordered by priority)

### Task 1: Chain scope + adapter contract (Day 1)
- What to build: agree with T1 on the `NormalizedTransaction` shape; stub chain-detection function (address format + checksum → chain).
- Acceptance criteria: contract frozen and committed alongside T1's API contract.

### Task 2: BTC + ETH adapters (Day 2)
- What to build: raw fetch, pagination, retries, caching against explorer APIs (Etherscan, Blockchair, etc.). Do NOT build tracing yet.
- File(s): `/blockchain/adapters/btc/`, `/blockchain/adapters/eth/`
- Inputs: `EXPLORER_API_KEY_BTC`, `EXPLORER_API_KEY_ETH`
- Outputs: raw transaction data via a common adapter interface
- Acceptance criteria: raw data available and retriable through the common interface for both chains.

### Task 3: Normalization + graph writes (Day 3)
- What to build: convert raw adapter data into the common `NormalizedTransaction` schema; write into Neo4j per the TRANSACTION edge shape in BUILD.md; basic lookup/neighborhood query support for T1's trace engine.
- Inputs: raw data from Task 2, Neo4j schema from T5
- Outputs: populated Neo4j graph
- Acceptance criteria: wallet → tx → neighbor query works; BTC and ETH fixtures both map to the same `NormalizedTransaction` shape.

### Task 4: Synthetic scenario fixtures (Day 2, shared with T3/T5)
- What to build: the 5 deterministic scenarios' underlying chain data (direct VASP, peel chain, cross-chain, mixer boundary, conflicting labels) as fixtures.
- **Note:** T3 has already seeded a temporary demo graph via `ml/data/seed_neo4j.py` (tagged `demo_seed: true`) so they could start feature/model work without waiting on you. Your real fixtures are meant to **replace** this, not sit alongside it. Tell T3 when your fixtures are ready so they can retrain against real data, and make sure the demo_seed data is wiped **before Day 9** packaging — offline demo must run on your real fixtures, not T3's placeholder graph.
- Acceptance criteria: fixtures load via the shared seed script and produce the documented expected outputs; `demo_seed: true` data confirmed removed before Day 9.

### Task 5: Cross-chain correlator (Day 5)
- What to build: exactly one bridge pattern, correlating a source-side lock/burn event with a destination-side mint/release event using:
  - Bridge contract identity (structural signal)
  - Lock/burn ↔ mint/release event pairing
  - Amount correspondence (post fee/slippage)
  - Timestamp proximity window
  - Asset relationship (native/wrapped mapping)
  - Destination behavior continuation check
- Represent as a `CROSS_CHAIN_LINK` relationship — never as a fake same-chain `TRANSACTION` edge — and always give it lower default confidence than a same-chain link.
- File(s): `/blockchain/cross_chain/`
- Acceptance criteria: Scenario 3 shows a `CROSS_CHAIN_LINK` with explicit uncertainty in the response.

### Task 6: Pattern-engine graph query support (Day 4)
- What to build: graph queries T1's pattern rules need (fan-out/fan-in neighborhoods, timing windows) — supporting role only, T1 owns the rule logic itself.
- Acceptance criteria: T1's Scenario 2/4 pattern tests pass using your query support.

### Task 7: Integration hardening (Days 8–10)
- What to build: fix adapter/normalization/cross-chain issues found during full-pipeline integration and adversarial testing (e.g., API failure simulation, rate-limit handling).
- Acceptance criteria: pipeline survives explorer API timeouts/rate limits gracefully with a visible cached fallback, never blocking the demo critical path.

## Contracts You Must Honor
- `NormalizedTransaction` schema, Neo4j entity/relationship shapes from BUILD.md, cross-chain confidence-always-lower-than-same-chain rule.

## DO NOT
- Do not build anything outside your scope list.
- Do not modify files owned by other teammates.
- Do not add a 3rd live chain, Tron, or any privacy chain.
- Do not represent a cross-chain hop as a normal same-chain transaction edge.
- Do not put live explorer fetching on the demo's critical path — it must be optional/cached-fallback only.

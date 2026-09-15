# BUILD_T1.md — Backend + Investigation Logic Lead
> ⚠️ AGENT INSTRUCTIONS: You are building ONLY the items in this file. Nothing else. Build exactly as specified.

## Your Scope
The investigation lifecycle: case management, the bounded trace engine, VASP attribution, ATLAS (the challenge engine), the information-gap/next-best-action engine, the recommendation engine, and every core API endpoint. You own the API contracts everyone else builds against.

## Your Files
- `/backend/case_management/` — case creation, status, queue (POST/GET /cases)
- `/backend/trace/` — bounded priority/BFS trace engine
- `/backend/attribution/` — VASP attribution engine + evidence tiering
- `/backend/atlas/` — ATLAS challenge engine
- `/backend/information_gap/` — next-best-action ranking
- `/backend/recommendation/` — recommendation engine + approval gate
- `/backend/api/` — all FastAPI route definitions, OpenAPI skeleton

## Your Tasks (ordered by priority)

### Task 1: Freeze API contracts + case management (Day 1)
- What to build: OpenAPI skeleton for every endpoint in BUILD.md's API table; case creation/status/queue logic.
- File(s): `/backend/api/openapi.yaml`, `/backend/case_management/`
- Inputs: none (first mover on contracts, coordinate live with T5 on schema)
- Outputs: frozen API contract everyone builds against
- Acceptance criteria: `/cases` POST/GET work against a stub DB; contract committed to repo.

### Task 2: Trace engine v1 (Day 3)
- What to build: bounded priority/BFS trace exactly per this pseudocode:
```
function trace(root):
    queue = priority_queue(root)
    visited = {}
    results = []
    while queue and within_time_budget:
        path = pop_best(queue)
        node = path.last
        if known_service_boundary(node): results.append(finalize(path)); continue
        if depth_limit OR value_limit: results.append(terminate(path, "limit")); continue
        if mixer_or_privacy_boundary(node): results.append(terminate(path, "evidentiary_break")); continue
        edges = graph.outgoing(node)
        if fanout(edges) > CAP: results.append(terminate(path, "mixer_scale_fanout")); continue
        for edge in edges:
            if visited_better(node, path): continue
            new_path = extend(path, edge)
            score = update_path_priority(new_path)
            queue.push(new_path, score)
    return rank(results)
```
- Controls: max depth 8 hops (hard ceiling), value cutoff ~1% of origin, fan-out cap terminates as pattern event, visited memoization, priority = confidence + financial relevance + attribution potential.
- Inputs: Neo4j graph (from T2/T5, available by Day 2–3)
- Outputs: `TraceResult` object consumed by T2 (graph support), T4 (graph UI)
- Acceptance criteria: Scenario 1 trace returns the correct expected path.

### Task 3: VASP attribution engine (Day 4)
- What to build, in this exact order:
  1. Find terminal/service-boundary candidates on each materialized trace branch.
  2. Retrieve every label on the candidate address (source + freshness).
  3. Calculate path directness: hops, branch count, obfuscation events, value retained, temporal gap.
  4. Calculate corroboration: independent sources, current activity, consistent service behavior.
  5. Apply source/freshness caps so a weak/stale label cannot jump to a high-confidence tier.
  6. Generate candidate VASPs independently per branch — do not collapse fan-out branches.
  7. Create the attribution object with supporting evidence, contradicting evidence, unknowns.
  8. Pass to ATLAS before it becomes the investigator-facing leading attribution.
- Evidence tiers: Strong / Medium / Weak / Unknown exactly per BUILD.md's tier table.
- Inputs: `TraceResult`, `Label` records (T5)
- Outputs: `AttributionResult` (tiered, per-branch)
- Acceptance criteria: direct-VASP scenario and conflicting-labels scenario both produce the documented correct tier.

### Task 4: Pattern rules (Day 4, shared with T3 analytics support)
- What to build: deterministic rules run over the *materialized subgraph* (never mid-traversal): peel chain, rapid forwarding (>90% value moved in <10 min), fan-out, fan-in, structuring (flag only, never auto-conclude fraud), mixer/privacy boundary (terminates evidentiary continuity), bridge detection (hand off to T2's cross-chain module).
- File(s): `/backend/patterns/`
- Acceptance criteria: Scenarios 2 and 4 pass with visible, per-pattern explanations.

### Task 5: ATLAS (Day 5)
- What to build: for every leading VASP attribution, generate 3–4 competing hypotheses, contradictions, and missing-data gaps, then a robustness assessment.
- Flow: TRACE RESULT → VASP CANDIDATE → ATLAS(Alternatives, Contradictions, Missing Data) → ROBUSTNESS ASSESSMENT → INFORMATION GAP → NEXT BEST ACTION
- Inputs: `AttributionResult`
- Outputs: `AtlasResult` consumed by T4 (ATLAS UI), T5 (persistence)
- Acceptance criteria: ATLAS can challenge the Scenario 1 attribution with at least 3 alternatives.

### Task 5b: ML integration (Day 6–7, per T3's handoff)
- What to build: call `ml.risk_model.predict.score_wallet_from_neo4j(address)` (or `score_wallet(feature_dict)`) directly as a Python import — no HTTP wrapper needed unless you hit a reason to isolate the ML process. Confirm this call path with T3 first.
- Return `ml_probability` as its own field on case/attribution responses, alongside `rule_risk_score` and `attribution_confidence` — never merged. Use this response shape:
```json
{
  "rule_risk_score": 0.72,
  "attribution_confidence": 0.81,
  "ml_probability": 0.78,
  "ml": {
    "output_label": "model_output",
    "is_model_output": true,
    "model_name": "risk_scoring_xgb_gpu",
    "model_version": "risk_xgb_gpu-...",
    "device": "cuda",
    "top_features": [{"feature": "touches_known_mixer", "importance": 0.59}],
    "disclaimer": "Statistical prioritization signal only. Does not decide VASP attribution or prove facts."
  }
}
```
- Surface ML-vs-rules disagreement explicitly to the investigator (don't just pick one silently) — this is a hard rule from T3's spec, not optional polish.
- Never write an ML score into the Evidence Ledger as a proven fact — it stays in the `ml` field only.
- Acceptance criteria: attribution response includes all three numbers separately; a disagreement case shows both the rule verdict and the ML estimate with the disclaimer intact.

### Task 6: Information gap + recommendation engine (Days 7, 8)
- What to build: rank next investigative action by `financial relevance × attribution potential × evidence quality × expected information gain ÷ investigation cost`. Recommendation engine outputs finding + supporting evidence IDs + confidence + action + approval_status, gated by human approval.
- Acceptance criteria: a medium-confidence case produces a reasoned next action; approval gate blocks unapproved recommendations from appearing as final.

### Task 7: Report generator + mock NCRP callback (Day 8)
- What to build: standardized JSON→PDF/HTML report with hash/timestamp/version. `/external/case-update` mock endpoint simulating NCRP/SAHYOG, visibly labeled "Simulated" in all output.
- Acceptance criteria: report generated and auditable; mock callback round-trips a case update.

### Task 8: Full-pipeline integration + freeze support (Days 8–10)
- What to build: fix contracts/state/error handling found during integration. No new architecture changes after Day 8.
- Acceptance criteria: Complaint → trace → attribution → ATLAS → recommendation → ledger works end-to-end, twice, without manual intervention.

## Contracts You Must Honor
- Evidence tier table, three-number framework (risk / attribution confidence / ML probability — never merged), trace control limits, all API endpoint shapes, all Neo4j/Postgres entity shapes — exactly as defined in BUILD.md.
- ML output from T3 is always labeled `model_output`; on disagreement with deterministic rules, rules win and the disagreement is surfaced, never hidden.

## DO NOT
- Do not build anything outside your scope list.
- Do not modify files owned by other teammates.
- Do not change the shared contract definitions without a team-level decision.
- Do not add packages without updating the master BUILD.md first.
- Do not run pattern detection mid-traversal.
- Do not let attribution logic treat a positive address hit as proof of ownership — service attribution and customer identity stay distinct.

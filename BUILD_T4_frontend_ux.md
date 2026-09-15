# BUILD_T4.md — Frontend / Investigator UX
> ⚠️ AGENT INSTRUCTIONS: You are building ONLY the items in this file. Nothing else. Build exactly as specified.

## Your Scope
Every investigator-facing screen. You never invent backend response fields — API response schemas from T1 are the contract, always.

## Your Files
- `/frontend/app/` — Next.js app routes
- `/frontend/components/graph/` — graph/path visualization
- `/frontend/components/attribution/` — attribution + evidence-tier display
- `/frontend/components/atlas/` — ATLAS challenge view
- `/frontend/components/evidence/` — Evidence Ledger view + verify UI
- `/frontend/lib/api/` — typed API client

## Your Tasks (ordered by priority)

### Task 1: UX flow + routes + mock API (Days 1–2)
- What to build: route map for login, case intake, queue, case overview, graph, attribution, ATLAS, evidence, recommendation, report, audit screens. TypeScript contracts + a mock API matching T1's frozen OpenAPI skeleton so you can build ahead of the real backend.
- Acceptance criteria: all routes scaffolded; mock API returns shapes matching the frozen contract.

### Task 2: Scenario visual shell (Day 2)
- What to build: a shell UI that can load and display any of the 5 synthetic scenarios, for use in scenario-driven development and later the demo.
- Acceptance criteria: shell renders scenario metadata from the shared fixture set.

### Task 3: Graph component (Day 3)
- What to build: the graph/path visualization consuming `/cases/{id}/graph`, showing hop details from the trace engine.
- Acceptance criteria: Scenario 1's trace path renders correctly against the real API once available.

### Task 4: Attribution + pattern badges (Day 4)
- What to build: attribution screen showing VASP candidates with their evidence tier (Strong/Medium/Weak/Unknown) — never a bare score — plus pattern badges (peel chain, fan-out, etc.) with visible explanations.
- Acceptance criteria: conflicting-labels scenario correctly shows tier + explanation.

### Task 5: ATLAS + Cross-chain UI (Day 5)
- What to build: ATLAS view (alternatives, contradictions, missing evidence, robustness assessment); cross-chain UI showing `CROSS_CHAIN_LINK` with its explicit uncertainty, visually distinct from a same-chain hop.
- Acceptance criteria: Scenario 1 ATLAS challenge and Scenario 3 cross-chain link both render correctly.

### Task 6: Evidence Ledger UI (Day 6)
- What to build: evidence entries list + a "Verify" action calling `/cases/{id}/verify`, showing PASS/FAIL clearly (this is the killer differentiator's demo moment — make it visually unambiguous).
- Acceptance criteria: verify PASS and a deliberate tamper FAIL both display correctly.

### Task 7: Risk/confidence/evidence cards + recommendation UI (Days 6–7)
- What to build: cards showing the three numbers, using T1's actual response field names — `rule_risk_score`, `attribution_confidence`, `ml_probability` — always together, never merged into one. Pull `ml.top_features` and `ml.disclaimer` into the ML card so the model's scope limit is visible, not just its number.
- **New requirement (per T3's handoff → T1's integration):** when the rule-based verdict and `ml_probability` disagree, show both explicitly — e.g. a visible "rules vs. model disagree" state — rather than only displaying two calm numbers next to each other. Don't let the UI imply consensus that doesn't exist.
- Recommendation UI with approval gate.
- Acceptance criteria: all three numbers visible simultaneously on the case overview, labeled with their real field names/source; a disagreement case renders a clearly distinct visual state; recommendation requires explicit approval before showing as final.

### Task 8: All core screens against real backend (Day 7)
- What to build: swap every screen from mock API to the real backend. No hard-coded demo JSON anywhere.
- Acceptance criteria: every screen consumes the real API end-to-end.

### Task 9: Report/audit/security UI + demo polish (Days 8–9)
- What to build: report view/download, audit trail view, RBAC-aware UI states (blocked actions clearly shown, not just silently disabled). Final visual polish pass on graph and evidence screens for the demo.
- Acceptance criteria: unauthorized action attempt is visibly blocked in the UI; report is viewable/downloadable.

### Task 10: Judge-path testing (Day 10)
- What to build: nothing new — walk the exact demo path a judge will see and fix any rough UI edges found.
- Acceptance criteria: demo path runs clean in 3 timed rehearsals.

## Contracts You Must Honor
- All API response shapes exactly as T1 defines them — never invent fields.
- Three-number framework always shown together, never collapsed to one score.
- "Simulated" labeling must be visible anywhere NCRP/SAHYOG or Tron-adapter data appears.

## DO NOT
- Do not invent backend response fields.
- Do not merge the three confidence numbers into one displayed value.
- Do not hide Unknown-tier attributions — show them explicitly.
- Do not modify files owned by other teammates.

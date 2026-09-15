# UX_FLOWS.md — VAJRA Investigator Experience
> Companion to `vajra_ui_reference.html`. This describes the journey and states the static mockup can't show on its own — use it alongside the HTML file when building screens in Next.js.

## The Core Journey
```
Queue → Triage → Case Overview → Trace → Attribution → ATLAS → Evidence/Approval → Report
```
This is a trust-building sequence, not a set of equal tabs. An investigator should never be able to jump straight to "approve" without having seen the graph, the attribution, and ATLAS's challenge — the UI should make that path the natural one, even if all screens remain technically reachable.

### 1. Queue → Triage
- Sort by urgency/status (the colored dot), not just case age.
- Each queue item shows enough to triage without opening: pattern type, amount, tier signal.
- Clicking a case never loses your place in the queue — keep it visible/collapsed, don't navigate away from it.

### 2. Case Overview — the first read
- The three numbers (rule risk score, attribution confidence, ML probability) load first, above the fold, before the graph.
- If they disagree, that's the first thing the investigator sees — not something they discover by scrolling.

### 3. Trace → Attribution → ATLAS
- The trace graph is a **dedicated, full-width section on its own** — not sharing a row with attribution. It's the largest, most visually dominant element on the case overview, because it's where the human actually reasons about what happened; attribution and ATLAS are downstream interpretation of what the graph already showed.
- The overview version is a readable summary at a fixed size. An **"Expand" control opens a dedicated full-page/full-route view** (e.g. `/cases/[id]/graph`) for real exploration — pan, zoom, click into a specific hop's evidence, adjust depth/value filters. Keep the overview graph simple and the expanded view as the place for depth.
- Attribution (the claim) sits directly below the graph as a secondary row, paired with a compact Robustness teaser pulled from ATLAS — enough to glance at without opening the full ATLAS tab.
- ATLAS itself should not be a tab equal to the others — it's the last gate before something becomes actionable. Consider always-expanded or a distinct visual weight (e.g., a colored left border) so it can't be casually skipped.

### 4. Evidence Ledger + Recommendation — the "am I allowed to act" step
- This is the only place a formal/destructive action happens (approving a recommendation, generating a report).
- Approve should be a two-step action: click → confirm modal stating what will happen ("This will generate a report and notify NCRP (simulated). This cannot be undone.") → confirmed.
- Never a single click with no confirmation for anything that leaves an audit trail.

## States Every Screen Needs (beyond the "happy path")

| State | What it must communicate | Example copy |
|---|---|---|
| Empty queue | Nothing needs attention right now, not "broken" | "No open cases. New complaints will appear here as they're reported." |
| Loading / staged progress | Which stage it's in, not just "loading" — tracing can take real time | "Fetching transactions → done. Tracing (hop 5 of ≤8) → running." |
| Verify: in progress | It's actively recomputing, not frozen | "Recomputing hash chain, record 14 of 22…" |
| Verify: pass | Unambiguous, celebratory-but-not-cute | "Chain verified — 22 records, unbroken." |
| Verify: fail | Exactly where it broke, what's still trustworthy | "Chain broken at record 9 — hash mismatch. Everything before record 9 is intact." |
| Unauthorized action | Button visible but clearly blocked, with the reason and the fix | "Your role (Analyst) can view recommendations but not approve them. Ask a Supervisor to approve." |
| Unknown-tier attribution | Never a dead end — always paired with a next step | "This branch stopped at the depth limit, not a confirmed dead end. Suggested: request KYC records, or expand trace depth." |
| Rules/model disagreement | Expandable, not just a static warning icon | Clicking the ⚠ shows both reads side by side and states which one wins by default and why. |

## Trace Graph — Interaction Spec
The graph in `vajra_ui_reference.html` is a static SVG reference for visual language only (colors, node/edge conventions) — it is **not interactive** in the mockup. The real Next.js component must be.

### Must-have interactions
- **Click a node** → jump to that hop's evidence in the Evidence Ledger tab, and highlight the corresponding ledger row. This is the core "investigate from the graph" behavior, not optional polish.
- **Click/hover an edge** → show transaction detail (hash, amount, timestamp) in a tooltip or side panel without leaving the graph.
- **Pan and zoom** → required once a real trace has 7–8 hops with branching; the demo's clean 6-node path won't reflect real density.
- **Highlight the active path on hover** → hovering a node dims everything except the path from the victim wallet to that node, so a branch can be visually isolated.
- **Clicking a terminated node explains why** — limit hit vs. mixer/privacy boundary vs. unresolved — not just the grey color alone.

### Should-have (put behind the expand/full-page view, not the overview)
- Depth/value filter controls — collapse or hide branches below a confidence/value threshold.
- Full pan/zoom and denser layout tools for real investigation work.

### Implementation approach
- Use a real graph library rather than hand-rolled SVG event handling — `react-flow` is the natural fit given the stack (built for node/edge click/pan/zoom out of the box); `cytoscape.js` is the fallback if branching gets dense; `d3` is available if fully custom control is needed later.
- Map T1's `/cases/{id}/graph` (`TraceResult`) response directly into the library's node/edge model. Node/edge color and style conventions carry over unchanged from the mockup: teal = same-chain hop, dashed amber = cross-chain link (always lower confidence), grey = terminated/unresolved.
- Keep the case-overview graph read-only and simple (no filters, fixed size) for speed; put filters and deep pan/zoom behind the "Expand" button → dedicated `/cases/[id]/graph` route.


- **Keyboard focus visible everywhere** — queue items, tabs, buttons. Investigators may move fast without a mouse.
- **The disagreement flag is always clickable** to reveal detail — a bare warning icon creates anxiety without giving the investigator anything to act on.
- **URL reflects state** — case ID and active tab should be in the URL (e.g. `/cases/0417/atlas`) so a case can be deep-linked to a supervisor, not just navigated to by clicking through.
- **The rule-based tier always wins by default** when rules and model disagree — this must be stated in the UI itself, not just documented in the backend spec, so the investigator never mistakes the ML number for a second vote.
- **Errors describe what happened and how to fix it, in the interface's voice** — no apologies, no vague failure messages (per general product tone, but especially important here since this is an investigation tool people may rely on in a legal context).

## What's Explicitly Out of Scope for the Demo
- Multi-step onboarding/tutorial flows — investigators are assumed trained; don't build a walkthrough.
- Notification/alert delivery UI beyond the single alert channel already in scope (per `BUILD.md`) — no in-app notification center.
- Mobile-specific redesign — responsive down to tablet width is enough; this is not a phone-first tool.

# UNIQUENESS_ASSESSMENT.md — VAJRA vs. PS 26183 Baseline
> Reference document only. Not part of the build spec — nothing here changes `BUILD.md` or any `BUILD_Tx.md`. Revisit this **after** the 10-day build is complete, when deciding how to pitch/polish/position for judging.

## Problem Statement (confirmed)
**PS 26183:** "Real-Time Identification of Fraud-Linked Cryptocurrency Exchanges from Victim-Reported Suspect Wallet Addresses through Automated Blockchain Analytics."

Note: PS 26182 ("Automated Attribution of Unknown Cryptocurrency Wallets to Nearest VASPs through Blockchain Intelligence APIs") is adjacent and easy to confuse with 26183 in judging conversation. Keep the distinction clear: 26183 starts from a **victim complaint**, not a bare unknown wallet, and is investigation/report-workflow oriented, not a lookup tool.

## What the Baseline Solution Looks Like (what most competing teams will build)
Standard published/industry approach to this exact problem, based on current literature and practice:
- BFS/DFS-style transaction tracing (taint analysis: Poison, Haircut, FIFO, LIFO methods)
- Address clustering + common-spend heuristics
- A single "risk score" or "wallet score" output
- Static evidence — a report generated once, not a verifiable trail
- One winning attribution shown, no self-checking of that attribution

This is the floor. Your build's core tracing/clustering/mixer-detection work (T1, T2) sits at this floor too — that part is necessary but not differentiating on its own.

## Where VAJRA Currently Differs From the Baseline

| Feature | Baseline | VAJRA (as currently planned) | Differentiation strength |
|---|---|---|---|
| Attribution output | Single risk score | Evidence-tiered (Strong/Medium/Weak/Unknown) + 3 numbers shown separately, never merged | Strong |
| Self-checking | None — one trail, one answer | ATLAS: generates 3–4 competing hypotheses, contradictions, missing-data gaps before surfacing the leading attribution | Strongest — this is the standout feature |
| Evidence trail | Static report | Hash-chained Evidence Ledger, tamper-detectable, independently verifiable | Strong |
| Cross-chain | Usually absent or same-chain-only | One bridge pattern modeled explicitly with lower default confidence, not hidden | Moderate |
| ML role | Score is often treated as the verdict | ML output labeled `model_output`, never overrides deterministic rules, disagreement surfaced explicitly to the investigator | Moderate–strong (mostly a trust/rigor story, judges respond well to it) |
| Workflow framing | Wallet-in, score-out lookup tool | Complaint-in, investigator workflow, human-approval gate, standardized report, NCRP-style mock callback | Strong — matches the actual PS wording ("victim-reported") better than most baseline builds will |

## Honest Gaps / Not Differentiated
- Core tracing (bounded BFS, depth/value/fan-out limits) is standard practice — don't pitch it as novel.
- Clustering-based VASP attribution itself (matching a terminal address to a known VASP via labels) is the same mechanism most tools use — the novelty is what wraps around it (tiers + ATLAS), not the match itself.
- Only 2 live chains (BTC/ETH) and 1 simulated bridge — a judge could ask why not more; the honest answer is scope discipline for a 10-day build, not a claimed strength.

## What This Means for Timing
Don't touch positioning/pitch work now — the team is mid-build and every hour belongs to the 10-day plan already in motion. This document exists so that **after** the build is complete (post Day 10 freeze), the team can:
1. Decide which 2–3 differentiators to lead with in the pitch (ATLAS + Evidence Ledger are the strongest candidates).
2. Prepare a one-line answer distinguishing 26183 from 26182 if asked.
3. Avoid overclaiming on the parts that are actually baseline (tracing, clustering).

No action needed before then.

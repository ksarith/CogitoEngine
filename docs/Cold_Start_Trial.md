# Cold-Start Trial — Cogito method v0.4 × CogitoEngine runtime

**Status:** Protocol only — drafted 2026-11-01, not yet run. Everything below is a candidate evaluation design, not established results.

**Purpose:** The first joint experiment between the method (LazarusForge `Tests/Cogito_Engine.md` v0.4) and this runtime (contract v0.1). Test whether written carry-over lets an agent with **no access to the original conversation** reconstruct how an idea developed — the method's central claim (v0.4 P2) and the runtime's central mechanism (append-only notebook, contract §3), attacked at once.

**Registered as:** CE-U07 (docs/Unknowns.md).

## Design

Bounded design problem, fresh idea (NOT the Reset-Event example — it is already entangled with the method's own history). Two phases; run both, record both.

### Phase A — method trial (artifact reconstruction)

1. **Seed.** The human (or a designated agent) records a bounded design idea as a dated seed note.
2. **Pass 1 — author agent.** First draft + delta note per the v0.4 minimum delta record (draft identity; changes and triggers; kept / changed / dropped / unresolved; claim classes; next step).
3. **Pass 2 — challenger agent.** Different line; disclose line, model family, and shared-context exposure. Attack pass: strongest opposing case written; challenger disposition recorded — answered / partially answered / unresolved, with a reason.
4. **Pass 3 — author agent.** Revision delta (same schema).
5. **Cold start.** A fresh agent receives ONLY the artifacts (seed, deltas, disposition records) — no conversation access, no repo history beyond the named files — and answers:
   - What changed between passes, and what triggered each change?
   - Which objections remain unresolved?
   - What is the next review step, and who owns the readiness decision?
   - What material constraint or existing mechanism did the passes miss (if any)?
6. **Scoring.** Compare the cold-start answers against ground truth sealed before Phase A (held by the human or recorded unopened in the trial record).

### Phase B — runtime trial (run reconstruction)

1. Run a multi-step flow on the same idea (`cogito run`), including a Skeptic step with `stop_on_refusal: true`.
2. A fresh agent receives only the FlowResult (steps, roles, models/providers, durations, refusal flags, notebook) and reconstructs: what the flow concluded, where it was attacked, whether any refusal occurred, and what the next concrete test would be.

## Candidate measures (not established metrics)

| Measure | Question |
|---|---|
| Carry-over fidelity | Can a fresh agent reconstruct changes, reasons, and unresolved objections from artifacts alone? |
| Missed-context rate | Did a later reviewer find an existing constraint earlier passes missed? |
| Objection survival | How many serious objections remain unresolved when readiness is declared? |
| Rework | How often must a proposal be substantially rewritten after entering formal review? |
| Retirement quality | Are retired ideas retired for traceable, categorized reasons? |

Record failures as carefully as successes. No selection bias in any Lessons Learned drawn from this trial.

## Honesty constraints

- Same-model agents must be disclosed; no independent-verification claims (contract CE-U01/CE-U02; method v0.4 P5).
- Successful reconstruction is evidence about record-keeping, not about the idea's correctness (method v0.4 P3).
- No numeric coherence gate is asserted by this trial (CE-U03 remains open).

## Record sheet

To be filled per run: date, agents (line / model family), shared-context disclosure, artifact list, cold-start answers, scores, failures. Until run: (none).

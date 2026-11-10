# STOP_RULE — when an open-ended process halts (artifact-completeness first)

**Adopted:** 2026-11-09, as ruled roadmap item 3 ("one stop-rule (artifact-completeness first), experimental until a contract amendment"), at the human's "please continue."  
**Provenance:** the 2026-11-07 sufficiency-mechanism assessment (Grok-concurred, human-brokered Class A), reactivated by the v0.2 ratification; the preregistration pattern follows LazarusForge MAINT-57 / MAINT-71.  
**Status:** repo convention, experimental — not contract text (§8: the contract changes by human-ratified commit only; the v0.3 note: the stop-rule enters the contract only after a stable working subset exists). Subordinate to docs/Cogito_Engine.md; the contract governs on any conflict.

## Why

Gates verify products; they do not terminate processes. Self-judged "good enough" gets Goodharted by the loop. So the stop condition is preregistered before the work starts, and it is computed from records, not felt.

## Exit test 1 — artifact-completeness (ADOPTED)

A process halts, "sufficient for now," when its target artifact carries all four:

1. **Claim** — what is asserted, stated plainly.
2. **Evidence** — every significant claim carries a C6 label (Measured / Replicated / Simulated / Analogous / Placeholder, unchanged) or an explicit Placeholder.
3. **Unknowns** — open questions registered (docs/Unknowns.md or the run record), not buried (P5).
4. **Next step** — one concrete next step, or an explicit "none."

All four are checkable from the artifact itself. The check is recorded in the run-record entry (docs/runs/RUN_LOG.md) that halts the process. A halt under this rule ends the process, not any question: it closes no unknown, ratifies nothing, and the process reactivates only by explicit direction of the human or a preregistered trigger.

## Specified, not adopted (the assessment's other two exit tests)

- **Budget cap:** if the budget declared at start (passes, time, tokens) is exhausted before artifact-completeness, halt with the honest line "budget exhausted, blocked by X" recorded in the run record and reflected in the honest-state table. Not adopted; awaits his ruling.
- **No-delta convergence:** if K consecutive passes (K declared at start) produce no decision-relevant record change, checked against the run record, halt and log the passes as churn. Not adopted; awaits his ruling.

## What this rule is not

Not a coherence threshold (§6: specified-not-built; nothing here computes a numeric gate). Not a seal: a stop-rule halt never distributes ratification power; the human's word still governs. Not runtime code: no code changed in this pass; a runtime or flow may reference this file, and enforcement inside the runtime is a candidate for a later ruled pass.

---
*Provenance: adopted 2026-11-09 by Vibe (GLM 5.3) under the co-author mandate (2026-11-02/04), at the human's "please continue" on ruled roadmap item 3. Non-independent: the same line as the seed recorder and Pass-1 author; it serves in no run-01 evaluation role.*

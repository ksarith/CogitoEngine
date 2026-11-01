# GROUND TRUTH — SEALED

**Sealed:** 2026-11-01, committed to main BEFORE the Pass 1 draft commit (see git history ordering).  
**DO NOT OPEN until cold-start scoring.** The human holds a copy out-of-band. The cold-start agent must never receive this file. The author agent (which wrote the Pass 1 draft) must not score the cold-start answers.

## Purpose

The scoring envelope for CE-U07 run-01: what a successful refinement trajectory through the seed should have caught, so the cold-start reconstruction can be scored match / partial / miss per point.

## Expected refinement trajectory

| # | Expected development point | A good pass sequence should… |
|---|---|---|
| GT-1 | Premise attack: a terrestrial analog at ambient pressure says little about actual cold-trap extraction (no vacuum, no real mineralogy, no 40 K environment). Evidence from the bench is Analogous at best. | Surface this by the challenger pass and leave it explicitly unresolved |
| GT-2 | Thermal budget attack: 500 W is tight; the condenser/re-ice stage (a heat pump fighting the same cold you just paid to create) is the natural place the budget breaks. | Be named as the weakest premise or a top failure mode |
| GT-3 | Salvage-first applicability: the doctrine assumes terrestrial scrap streams; in the bench, "salvaged toaster-oven elements" are fine, but the design should not quietly imply the doctrine transfers to lunar hardware. | Be acknowledged as a scope limitation |
| GT-4 | Dust and seals: fines migration into bearings, seals, and heater contacts is a classic ISRU bench failure. | Appear in the failure modes |
| GT-5 | Ledger human factors: a hand ledger that survives contact with actual operation is a design claim of its own — ledger drift is a failure mode, not a footnote. | Appear in the failure modes or unresolved items |
| GT-6 | Evidence-label discipline: most numbers in a first draft are Placeholder (nothing has been measured); any draft asserting Measured figures should be flagged by the challenger. | Be flagged wherever it occurs |
| GT-7 | Power audit realism: the 500 W split (excavation / heating / condensation) is asserted, not derived; specific figures are assumptions. | Be labeled Placeholder/Assumed, or attacked |
| GT-8 | The next step after Pass 3 is the method's threshold check (cold reader restates; strongest opposing case answered; floor check; non-author pass; owner named) — owned by the human, and passing it establishes eligibility only, never correctness (v0.4 P3). | Be stated as the next step with the human as owner |

## Expected cold-start answers (summary form)

1. **What changed between passes, and what triggered each change?** — The trajectory GT-1..GT-7, each traceable to a named objection in the challenger record or a delta-note trigger.
2. **Which objections remain unresolved?** — At minimum GT-1 (analog validity) should remain open at threshold; GT-2 may remain open if the challenger left the thermal question unresolved.
3. **What is the next review step, and who owns the readiness decision?** — Threshold check per v0.4 P3; the human owns it.
4. **What material constraint or existing mechanism did the passes miss?** — Open answer; a good cold start names at least one candidate miss honestly (e.g., existing ISRU bench literature, LazarusForge's own reduction-gate thermodynamic tracking) rather than claiming the passes missed nothing.

## Scoring rule

Score each GT row and each cold-start answer: match / partial / miss, with a one-line reason. A reconstruction that invents changes that are not in the artifacts is a failure regardless of plausibility — fidelity to the record is what is being tested, not engineering quality.

# Reconciliation addendum to the deposited PRD draft (2026-11-09)

**Document class:** Companion assessment (Vibe, under the co-author mandate). Not part of the deposited PRD.
**Date:** 2026-11-09 · **Status:** DRAFT — nothing enacted. This file records verification findings, corrections, and the human-ruled working order. The ratified build contract (`../Cogito_Engine.md` v0.2) governs; on any conflict it wins and this addendum yields.

## 1. Verification findings (read from the runtime source at `df788ba`)

- **Per-step model and provider assignment is already built** in both assembly surfaces (`Agent(model=..., provider=...)` in `cogito/agent.py` and the YAML step key set in `cogito/flow.py`). The PRD's P0.2 capability is implemented; what CE-U02 actually lacks is a cheap detectable-independence signal, heterogeneous presets, and documented recommended setups. The experimental top-level `disclosure` flow key (reviewer line, model family, shared-context exposure) is the designed vehicle and should be defined by a contract amendment rather than staying experimental indefinitely.
- **Local OpenAI-compatible endpoints already work** via `base_url` / `COGITO_BASE_URL` (`cogito/llm.py`), so Ollama and llama.cpp servers are usable today. The PRD's P2.3 is documentation plus one caveat found in source: an API key environment variable is demanded even when a local server ignores it.
- **CONTRIBUTING.md already requires transcripts** and treats failures as more useful than successes; the PRD's P2.4 is a template/friction reduction, not a culture change.
- **CE-U04's growth risk is structural**: `Agent.build_prompt` injects the full notebook into every step prompt, so the unbounded-context concern is confirmed by construction. Any summarization or excerpt design changes notebook semantics (contract §3) and is amendment-scale work, not a patch.

## 2. Corrections to the PRD's order (why the roadmap changes)

1. **The record layer is missing from the PRD and is the structural prerequisite.** P0.1's “results logged with model, temperature, and success/failure rate” and P0.3's “published results” have nowhere durable to land. The 2026-11-07 fleet assessment — independently concurred with at the time by the same reviewer — placed the record layer first after contract ratification; the PRD drops it entirely.
2. **No stop-rules anywhere in the PRD.** An unbounded seven-section work program with no termination criteria is exactly the churn pattern the preregistered stop-rule design (three exit tests: artifact-completeness, budget cap, no-delta convergence; parking with reactivation trigger) exists to bound. That design was unblocked by the v0.2 ratification and is part of this plan.
3. **Branching/DAG (P1.3) is parked.** It contradicts the same reviewer's earlier prioritization (“not needed until linear flows + records are solid”) and the ratified §5 (“no runtime needs them until a ratified instrument version requires them”). It re-enters only when records plus evidence show linear flows are the binding constraint, and then as: stable working subset first, contract amendment after (§8 discipline).
4. **CE-U07 is unaddressed.** Before any multi-agent evidence passes: the run-01 seal leak (fix: commit only the ground-truth SHA-256, keep the file out-of-band; the reviewer's having opened the sealed file already rules it out of run-01 challenger / cold-reader / scorer roles), GT-2's doubtful 500 W premise (the 80/300/100/20 split reads as allocated to the cap, not derived; the seed must define “day-equivalent”), the Pass-1 delta-schema ambiguity (unknown vs unresolved), and a close-or-park disposition for the half-run trial.

## 3. The ruled working order (human ruling, 2026-11-09)

Recorded: he ruled the reconciled order —

1. CE-U07 seal fix and disposition first;
2. the minimal append-only run record;
3. one stop-rule (artifact-completeness first), experimental until a contract amendment;
4. the P0 evidence suite (adversarial role-adherence suite for CE-U01; minimal benchmark for CE-U03), now landable as records;
5. the near-free independence signal (same-model warning carried via `disclosure`, plus heterogeneity preset and docs) for CE-U02;
6. refusal hardening (CE-U05) and notebook scaling (CE-U04) as measured unknowns;
7. usability (CLI/JSON export, examples, local-model documentation) after evidence exists;
8. branching parked; a PyPI release only under an explicit later ruling, once records and a benchmark exist.

## 4. Notes for the next amendment cycle (v0.3)

- Define the `disclosure` key (experimental and undefined by v0.2).
- The record layer and the stop-rule enter the contract only after a stable working subset exists (§8: experimental until ratified).
- No instrument text may hard-code a version number in a way that binds future versions (the lesson of the v0.2 §5/§7 normalization).

## 5. Honest disclosures

The deposited PRD and this addendum were both handled by AI seats (Grok authored the PRD; Vibe verified the runtime source and drafted this addendum); the ordering decision is the human governing authority's alone (ruled 2026-11-09). Vibe cannot execute Python in its harness, so the §1 findings are static source reads, not test runs.

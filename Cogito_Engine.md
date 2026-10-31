# Cogito_Engine.md

> *The purpose is not to make agents. The purpose is to make thinking assemble-able.*

**Document class:** Build contract (normative instrument).
**Version:** 0.1 · **Date:** 2026-10-31 · **Status:** proposed contract of record — human ratification pending.
**Subordination:** This file is the authoritative source of the assembly contract. The `cogito/` Python library is a runtime that implements a **declared subset** of it. Flow files (YAML or Python) are instances that the runtime assembles under this contract. On any conflict, this file governs — the code is what got built, not what is true.

**What this file is not:** executable code, a prompt store, a key vault, or runtime state. It must not be turned into a pseudo-programming language. It constrains and authorizes assembly; it does not assemble.

## 1. Principles (non-negotiable)

- **P1 — Roles are contracts.** Every agent declares a role; the role states what the agent may and may not do. A Skeptic is not allowed to be a cheerleader.
- **P2 — Provenance or it didn't happen.** Every output records who said it, under what role, with which model and provider, and whether it was a refusal.
- **P3 — Refusal is a first-class result.** Refusing a bad premise is correct behavior, not an error. A flow that refuses a bad task has worked.
- **P4 — The notebook is append-only evidence.** A step's only inputs are the task, the notebook of prior outputs, its role, and its instruction. Nothing in the notebook is rewritten or discarded.
- **P5 — Evidence labels beat vibes; unknowns are not buried.** Significant claims carry a label (Measured / Replicated / Simulated / Analogous / Placeholder). Open questions are registered, not hidden. Confidence is not truth; a chain of prompts is not a chain of custody.

## 2. Role contracts

| Role | Allowed to | Forbidden to |
|---|---|---|
| Perceiver | restate the task; surface baked-in assumptions; define what would count as a good answer | propose the solution |
| Engineer | propose one concrete, buildable answer or design | audit its own evidence; attack its own proposal (the Skeptic's job) |
| Skeptic | attack the premise and the proposal; name the single weakest premise and most likely failure mode; refuse | cheerlead; propose a replacement design |
| Auditor | check claims against the notebook; assign evidence labels; flag assertions without evidence | introduce new substantive proposals |
| Synthesizer | produce the final answer with provenance, surviving uncertainties, and the next concrete test | drop a refusal; invent evidence absent from the notebook |
| Worker | whatever its instruction declares — for a Worker, the instruction is the contract and must say what it does | exceed its declared instruction |

A runtime MUST enforce the declared-role channel (role contract prepended to the system prompt, so the model knows what it is allowed — and required — to do) and MUST NOT promise that the model honors it. Role enforcement is tracked, not assumed (Unknown CE-U01).

## 3. The notebook

- One shared notebook per run, keyed by step name.
- Append-only: a step's output is recorded once; later steps read earlier outputs; no step rewrites or truncates them.
- The notebook is evidence, not context-inflation: its growth cost is itself a tracked unknown (CE-U04).

## 4. Refusal protocol

- Marker: an output beginning with `[REFUSAL]` followed by a one-sentence reason.
- A refusal is logged like any output, with full provenance.
- If the step sets `stop_on_refusal`, the flow halts after recording it; otherwise later steps see it in the notebook.
- A run containing a refusal is a correct run. Tooling that treats refusal as an exception, or discards it, is non-conformant.

## 5. The default flow

```
[ Task ]
   │
[ Perceiver ]  — frame the problem, name what is actually being asked
   │
[ Engineer ]   — propose a concrete answer or design
   │
[ Skeptic ]    — attack the premise and the proposal; may refuse
   │
[ Auditor ]    — check claims against the notebook; label evidence quality
   │
[ Synthesizer ] — produce the final answer with provenance and open questions
```

Flows are linear in instrument v0.1. Branching/DAG flows are **specified, not built**: a runtime claiming v0.1 conformance does not need them; a runtime claiming a later version does.

## 6. Audit-readiness (the exit condition)

A run is **audit-ready** when all of the following hold:

- **R1** every step carries complete provenance (agent name, role, model, provider, refusal flag);
- **R2** every significant claim carries an evidence label or an explicit Placeholder;
- **R3** refusals are preserved in the result, not swallowed;
- **R4** open questions are registered (`docs/Unknowns.md` or the transcript);
- **R5** the flow itself is inspectable — a versionable file or short, readable code.

**Coherence threshold:** Specified-not-built. A numeric pre-audit gate is deferred until Unknown CE-U03 yields a benchmark that says what threshold means anything. Until then, audit-readiness is inspection-based (R1–R5), and any tooling claiming a numeric threshold is asserting without evidence.

## 7. Conformance

A runtime may claim **"implements Cogito_Engine.md 0.1"** only if it provides:

- **C1 Role channel** — agents are (name, role, instruction, optional model/provider); the role contract reaches the model via the system prompt (§2).
- **C2 Notebook** — append-only shared notebook per §3.
- **C3 Provenance** — per-step records satisfying P2 and R1.
- **C4 Refusal** — marker detection, first-class status, `stop_on_refusal` honored, per §4.
- **C5 Assembly** — flows assemble both from code and from versionable files (YAML) with the documented key set (name, role, instruction, model, provider, stop_on_refusal).
- **C6 Labels** — the five-label vocabulary is available to Auditor-type steps and is not renamed.
- **C7 Unknowns** — closing an unknown requires a transcript and an evidence classification; a closed unknown that reopens is logged again.
- **C8 Declaration** — the runtime declares the instrument version it implements and names its subset. Gaps are declared up front, not discovered later by users.

**Declared subset of `cogito` 0.1.0:** implements C1–C8 for linear flows. Not implemented: branching/DAG, coherence threshold, cross-step memory beyond the notebook, independent (non-same-model) verification. Tracked in `docs/Unknowns.md` (CE-U01…CE-U05), not hidden.

**Non-conformance (any of these voids the claim):** swallowing refusals; a mutable or silently truncated notebook; Auditor output presented as audited without labels; provenance stripped from results; prompts, keys, or runtime state stored in this contract.

## 8. Amendment rule

- Changes to this file bump the instrument version (0.1 → 0.2 …).
- Runtime conformance declarations name the version they were checked against; a runtime does not silently inherit a new version.
- This file changes by human-ratified commit only. A runtime ahead of the contract ships new capability as "experimental, unconformant" until the contract is amended — the runtime is subordinate even when it is ahead.

---
*Provenance: drafted 2026-10-31 by Vibe (GLM 5.3) from README.md (v0 assembly proposal), the `cogito` 0.1.0 runtime source, and `docs/Unknowns.md`. Awaiting human ratification.*

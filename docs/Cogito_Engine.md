# Cogito_Engine.md

> *The purpose is not to make agents. The purpose is to make thinking assemble-able.*

**Document class:** Build contract (normative instrument).
**Version:** 0.2 · **Date:** 2026-11-09 · **Status:** contract of record — **ratified 2026-11-09 by Ksarith** (human governing authority). Amends the unratified v0.1 (2026-10-31); see §9.
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

The role contract that reaches the model MUST include the declared role's own Allowed / Forbidden text from the table above, not only a generic preamble. A custom role with no row in the table receives the generic contract plus its instruction, and is not thereby a §2 role contract.

## 3. The notebook

- One shared notebook per run, keyed by step name. Step names are unique: a flow with duplicate step names is non-conformant and is rejected at assembly, whether built from code or from a file.
- Append-only: a step's output is recorded once; later steps read earlier outputs; no step rewrites or truncates them. A later step's failure (for example a provider error) does not discard completed records: the runtime MUST surface the failure loudly, as an error and not as a refusal, and keep the completed steps available to the caller.
- The notebook is evidence, not context-inflation: its growth cost is itself a tracked unknown (CE-U04).

## 4. Refusal protocol

- Marker: an output beginning with `[REFUSAL]` followed by a one-sentence reason. Detection is prefix-only; a runtime MAY ignore leading whitespace, markdown emphasis/quote/heading characters and letter case when matching. Refusals without the marker, or after a preamble line, are not detected by this rule (Unknown CE-U05).
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

Flows are linear through instrument v0.2. Branching/DAG flows are **specified, not built**: no runtime needs them until a ratified instrument version requires them.

## 6. Audit-readiness (the exit condition)

A run is **audit-ready** when all of the following hold:

- **R1** every step carries complete provenance (agent name, role, model, provider, refusal flag);
- **R2** every significant claim carries an evidence label or an explicit Placeholder;
- **R3** refusals are preserved in the result, not swallowed;
- **R4** open questions are registered (`docs/Unknowns.md` or the transcript);
- **R5** the flow itself is inspectable — a versionable file or short, readable code.

**Coherence threshold:** Specified-not-built. A numeric pre-audit gate is deferred until Unknown CE-U03 yields a benchmark that says what threshold means anything. Until then, audit-readiness is inspection-based (R1–R5), and any tooling claiming a numeric threshold is asserting without evidence.

## 7. Conformance

A runtime may claim **"implements Cogito_Engine.md"**, naming the instrument version it was checked against (§8), only if it provides:

- **C1 Role channel** — agents are (name, role, instruction, optional model/provider); the role contract, including the role's own Allowed / Forbidden text, reaches the model via the system prompt (§2).
- **C2 Notebook** — append-only shared notebook per §3, with unique step names and completed records surviving a later step's failure.
- **C3 Provenance** — per-step records satisfying P2 and R1: the model the provider reported and the model requested (they differ under aliases such as `-latest`). A runtime SHOULD also record the endpoint base URL and sampling temperature, since a provider label alone does not say what was actually called.
- **C4 Refusal** — marker detection, first-class status, `stop_on_refusal` honored, per §4.
- **C5 Assembly** — flows assemble both from code and from versionable files (YAML) with the documented key set (name, role, instruction, model, provider, stop_on_refusal).
- **C6 Labels** — the five-label vocabulary is available to Auditor-type steps and is not renamed.
- **C7 Unknowns** — closing an unknown requires a transcript and an evidence classification; a closed unknown that reopens is logged again.
- **C8 Declaration** — the runtime declares the instrument version it implements and names its subset. Gaps are declared up front, not discovered later by users.

**Declared subset of `cogito` 0.1.2:** checked against instrument v0.2 (ratified 2026-11-09); the v0.2 amendments in this file (role-specific text in C1, C2 failure preservation, C3 reported-vs-requested model, §4 marker normalization) and the runtime's top-level `disclosure` flow key were experimental and unconformant while v0.2 was pending and are conformant as of its ratification (§8). Implements C1–C8 for linear flows. Not implemented: branching/DAG, coherence threshold, cross-step memory beyond the notebook, independent (non-same-model) verification. Tracked in `docs/Unknowns.md` (CE-U01…CE-U07), not hidden.

**Non-conformance (any of these voids the claim):** swallowing refusals; a mutable or silently truncated notebook; Auditor output presented as audited without labels; provenance stripped from results; completed steps discarded when a later step fails; duplicate step names; prompts, keys, or runtime state stored in this contract.

## 8. Amendment rule

- Changes to this file bump the instrument version (0.1 → 0.2 …).
- Runtime conformance declarations name the version they were checked against; a runtime does not silently inherit a new version.
- This file changes by human-ratified commit only. A runtime ahead of the contract ships new capability as "experimental, unconformant" until the contract is amended — the runtime is subordinate even when it is ahead.

## 9. Amendment log

- **v0.2 (2026-11-09, ratified):** role-specific contract text required in the role channel (§2, C1); unique step names and failure preservation (§3, C2); reported-vs-requested model, endpoint and temperature in provenance (C3); marker-matching normalization (§4); declared subset corrected to `cogito` 0.1.2 and CE-U01…CE-U07. No principle, role-table, flow or readiness-criteria change. Ratified 2026-11-09 by Ksarith with the §5/§7 instrument-version references normalized into the ratified text under his ruling (the draft's "a runtime claiming a later version does" would otherwise have required branching/DAG of any v0.2-conformant runtime); no other change.
- **v0.1 (2026-10-31):** initial draft.

---
*Provenance: drafted 2026-10-31 by Vibe (GLM 5.3) from README.md (v0 assembly proposal), the `cogito` 0.1.0 runtime source, and `docs/Unknowns.md`. Never ratified; superseded by v0.2.*
*v0.2 amendment drafted 2026-11-09 by Claude from a review of this contract against the `cogito` 0.1.1 source. Ratified 2026-11-09 by Ksarith (human governing authority); Grok-reviewed before ratification; landed by Vibe under the co-author mandate, with the §5/§7 instrument-version references normalized into the ratified text under his ruling.*

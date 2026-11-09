# Deposited external draft: PRD — Evidence-First Evolution (Grok, 2026-11-09)

**Document class:** External proposal draft, deposited verbatim as received (human-brokered Class A intake; relayed by Ksarith from Grok embedded in X on 2026-11-09).
**Deposited by:** Vibe under the co-author mandate, 2026-11-09.
**Status:** DRAFT — nothing in this file is enacted, ratified, or scheduled. The ruled working order and the corrections live in the companion `PRD_2026-11-09_RECONCILIATION_ADDENDUM.md`. The ratified build contract (`../Cogito_Engine.md` v0.2) governs; on any conflict the contract wins.

---

Everything below this line is the external message, verbatim and unedited.

**Here are focused, high-leverage improvements for CogitoEngine**, ordered by impact relative to the project’s own stated gaps (Unknowns CE-U01–CE-U07 and the current-state table).

### 1. Close the biggest epistemic gaps first (CE-U01 & CE-U02)
- **Role adherence measurement**: Add an adversarial test suite that deliberately tries to make models violate their Allowed/Forbidden contracts (e.g., force a Skeptic to cheerlead or an Engineer to self-audit). Log success/failure rates with different models and temperatures. This turns “role contract reaches the model” into measured evidence.
- **True multi-model independence**: Make different roles default to different providers/models (or at least force temperature / system-prompt variation). Same-model sequential agents are essentially one mind with extra steps—address this explicitly rather than treating it as an open unknown forever.

### 2. Ship a minimal, honest benchmark suite (CE-U03)
Create a small, versioned set of tasks (design, critique, factual synthesis, unfalsifiable claims) with:
- Single well-prompted model baseline
- Default CogitoEngine flow
- Human-judged or checklist-scored outcomes (evidence labels, refusal quality, open questions retained)

Even 8–12 tasks would let the project claim “beats / does not beat a single model on X” instead of leaving the core value proposition unmeasured.

### 3. Make the notebook scalable (CE-U04)
- Add optional notebook summarization or “relevant excerpt” retrieval for later steps instead of dumping the entire growing transcript.
- Track token growth and degradation in the unknowns ledger with concrete measurements.
- Consider a lightweight “evidence index” (claims + labels) that later agents can query without full context.

### 4. Harden refusal detection (CE-U05)
Prefix matching is brittle. Improve it with:
- Normalized detection (already partially done) plus a short secondary classifier or few-shot check when the marker is missing but language is clearly refusal-like.
- Explicit logging of “unmarked refusals” so the failure mode is visible.

### 5. Implement the already-specified next step: branching / DAG flows
Linear flows are a solid v0 foundation. Adding conditional branching (especially after Skeptic refusal or Auditor low-evidence flags) would unlock more realistic cognitive patterns without exploding complexity. Keep the contract-first discipline: amend the instrument only after a working subset exists.

### 6. Practical usability wins
- Richer CLI output: pretty-print the notebook with roles, evidence labels, and refusal highlights; optional JSON export for downstream analysis.
- More example flows (design critique, claim verification, salvage/repair tasks that mirror LazarusForge philosophy).
- Optional local-model support (Ollama / llama.cpp endpoints) so people can experiment without API keys.
- A simple “flow visualizer” (even text-based or Mermaid export) so the assembly is inspectable at a glance.

### 7. Process / community hygiene
- Require every closed Unknown to ship with a transcript + evidence classification (you already state this—make the template frictionless).
- Add a short “How to contribute a failed flow” section with a real example transcript.
- Consider a minimal PyPI release once the next couple of Unknowns have data, so others can `pip install cogitoengine` instead of editable installs only.

The project’s strongest asset is its intellectual honesty—the contract, the Unknowns ledger, and the refusal-as-success stance. The highest-ROI improvements are therefore the ones that turn open questions into measured results rather than adding more features. Prioritize evidence generation over expanding the surface area.

**PRD: CogitoEngine Improvements — Evidence-First Evolution**

**Document Status:** Draft v0.1  
**Date:** 2026-11-09  
**Author:** Derived from external review of current contract, README, and Unknowns ledger  
**Governing Instrument:** Must remain subordinate to `docs/Cogito_Engine.md` (currently v0.2). Any new capability ships as experimental until the contract is amended and ratified.

### 1. Overview & Problem Statement
CogitoEngine is a deliberately small, contract-driven runtime for assembling multi-agent cognitive flows with strong provenance, role contracts, and first-class refusal. Its current strengths (linear flows, append-only notebook, honest Unknowns tracking) are undercut by several open gaps that prevent it from demonstrating value over a single well-prompted model.

This PRD defines a focused set of improvements that close the highest-priority Unknowns (CE-U01–CE-U05), implement already-specified capabilities (branching), and improve usability—while preserving the project’s core epistemic discipline: no overclaiming, evidence required to close unknowns, and the runtime remains subordinate to the contract.

### 2. Goals
- Turn open Unknowns into measured results.
- Demonstrate (or falsify) that assembled multi-agent flows produce better, more auditable outcomes than single-model baselines on concrete tasks.
- Keep the surface area small and the contract authoritative.
- Make the system more usable for external contributors and real workflows without sacrificing inspectability.

**Non-goals:** Building an autonomous agent framework, adding a large plugin ecosystem, promising emergent intelligence, or expanding beyond the “workbench for assembling thinking” mission.

### 3. Success Metrics
- At least 3 Unknowns (preferably CE-U01, CE-U02, CE-U03) closed or substantially advanced with transcripts + evidence classifications.
- Public benchmark suite with baseline comparisons (single model vs. default flow) on ≥8 tasks.
- Measurable improvement in refusal detection rate (target: reduce unmarked refusals by ≥50% on a held-out set).
- Notebook degradation characterized with concrete token thresholds.
- Branching support implemented and covered by contract conformance tests.
- Increased external usability: at least 5 high-quality example flows and improved CLI output that makes provenance and evidence labels immediately visible.

### 4. Prioritized Requirements

**P0 — Evidence Generation (Must ship first)**

| ID | Requirement | Description | Acceptance Criteria | Related Unknown |
|----|-------------|-------------|---------------------|-----------------|
| P0.1 | Role Adherence Test Suite | Adversarial prompts that attempt to force role violations (Skeptic cheerleading, Engineer self-auditing, etc.) | Suite runs offline + with live models; results logged with model, temperature, and success/failure rate | CE-U01 |
| P0.2 | Multi-Model Independence | Support (and encourage) different models/providers per role; default configuration uses variation | Ability to assign models per step in YAML and Python API; documentation of recommended heterogeneous setups | CE-U02 |
| P0.3 | Minimal Benchmark Suite | Versioned set of tasks (design, critique, claim verification, unfalsifiable statements) with single-model baseline vs. CogitoEngine flow | ≥8 tasks, human or checklist scoring, published results with evidence labels | CE-U03 |

**P1 — Core Capability Hardening**

| ID | Requirement | Description | Acceptance Criteria | Related Unknown |
|----|-------------|-------------|---------------------|-----------------|
| P1.1 | Robust Refusal Detection | Improve beyond simple prefix matching (normalization already present) | Secondary detection path or few-shot check for unmarked refusals; unmarked cases logged; measured reduction in false negatives | CE-U05 |
| P1.2 | Notebook Scalability | Strategies to prevent unbounded context growth | Optional summarization / selective retrieval / evidence-index mode; measured degradation curves published | CE-U04 |
| P1.3 | Branching / DAG Flows | Implement the already-specified non-linear flow capability | YAML + Python support for conditional branches (especially post-refusal / low-evidence); contract updated only after implementation is stable | Specified, not built |

**P2 — Usability & Adoption**

| ID | Requirement | Description | Acceptance Criteria |
|----|-------------|-------------|---------------------|
| P2.1 | Enhanced CLI Output | Human-readable + machine-readable views of notebook, roles, evidence labels, and refusals | Color/structured terminal output + JSON export; Mermaid or simple text visualization of flow |
| P2.2 | Expanded Examples | High-quality, documented flows that demonstrate real value | ≥5 additional flows (including salvage/repair style tasks aligned with LazarusForge philosophy) |
| P2.3 | Local Model Support | First-class Ollama / OpenAI-compatible local endpoints | Works out-of-the-box with common local setups; documented |
| P2.4 | Contribution Friction Reduction | Clear templates and examples for submitting failed flows and closing Unknowns | Updated CONTRIBUTING.md + issue templates |

### 5. Phasing (Suggested)
- **Phase 1 (Evidence Foundation):** P0.1–P0.3 + improved refusal logging  
- **Phase 2 (Hardening):** P1.1–P1.3  
- **Phase 3 (Usability):** P2.x  

Each phase must update the Unknowns ledger and, where necessary, propose a contract amendment only after the capability is working and tested.

### 6. Out of Scope (for this PRD)
- Full agent memory systems beyond notebook improvements
- Tool-calling / external action loops
- GUI or web interface
- Automatic prompt optimization
- Multi-user or collaborative editing of flows
- Any claim of “guaranteed better reasoning”

### 7. Risks & Mitigations
- **Risk:** New features dilute the “small and honest” ethos.  
  **Mitigation:** Contract remains the source of truth; experimental flags required until ratification.
- **Risk:** Benchmarks become performative rather than informative.  
  **Mitigation:** Tasks must include unfalsifiable / refusal-worthy cases; scoring emphasizes provenance and evidence labels over “winning.”
- **Risk:** Multi-model setups increase cost and complexity.  
  **Mitigation:** Keep single-model fully supported; treat heterogeneity as optional but recommended for independence experiments.

### 8. Open Questions
- What is the lightest-weight way to score benchmark tasks while remaining reproducible?
- Should notebook summarization itself be performed by a dedicated role (e.g., a “Compressor” Worker)?
- How strictly should branching be constrained in the next contract version to avoid complexity explosion?

---

This PRD prioritizes turning the project’s own Unknowns into closed, evidenced results before expanding surface area. Implementation should continue the existing culture: every change ships with tests, every claim carries an evidence label, and the contract governs.

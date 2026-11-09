# CogitoEngine

> *The purpose of CogitoEngine is not to make agents.*  
> *The purpose is to make thinking assemble-able.*

CogitoEngine is a scrappy open-source experiment in **multi-agent cognitive flow in applicable, easy assembly** — a small Python library and CLI for wiring AI agents into flows where every agent declares its role, every output carries provenance, and refusal of a bad premise is a first-class result.

It is the cognitive sibling of the [Lazarus Forge](https://github.com/ksarith/LazarusForge): where the Forge salvages material value, CogitoEngine salvages reasoning value. Nothing gets discarded without accounting — not scrap, not a failed hypothesis, not a weak argument.

The project assumes that agents can hallucinate, that confidence is not truth, and that a chain of prompts is not a chain of custody. So every result records **who said it, under what role, with which model**.

---

## The assembly model

> **Contract:** the assembly model is normative in **[Cogito_Engine.md](Cogito_Engine.md)** (the build contract; v0.2 proposed, ratification pending; the runtime is checked against v0.1). This library is a runtime subordinate to it: the runtime declares the version and subset it implements. The summary below is descriptive; the contract governs.

Three layers, deliberately small:

1. **Agents** — a declared role + an instruction + a model. Roles are contracts: a Skeptic is not allowed to be a cheerleader.
2. **Flows** — an ordered chain of steps. Each step sees the task plus a shared **notebook** of everything prior steps produced. The notebook is append-only evidence.
3. **Assembly** — put a flow together in a few lines of Python, or from a YAML file you can version, diff, and audit.

### The default cognitive flow

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

Refusal rule: any agent may return `[REFUSAL] <reason>` instead of an answer. A refusal is a valid, logged output — not an error. A flow that refuses a bad task has worked correctly. In the default flow, a Skeptic refusal halts the run after the refusal is recorded.

---

## Install

```bash
pip install -e .
```

Set one API key (CogitoEngine talks to OpenAI-, Mistral-, and Anthropic-compatible APIs):

```bash
export MISTRAL_API_KEY="..."   # or OPENAI_API_KEY / ANTHROPIC_API_KEY
```

## Quick start

```python
from cogito import cognitive_flow

flow = cognitive_flow()          # Perceiver -> Engineer -> Skeptic -> Auditor -> Synthesizer
result = flow.run("Design a cheap rainwater filter from salvage parts.")

print(result.final)              # synthesized answer
for step in result.steps:        # full provenance
    print(f"{step.agent.role}: {step.output[:80]}...")
```

Or from YAML:

```bash
cogito run examples/flows/peer_review.yaml --task "State the problem this repo solves."
```

If the flow file defines `task:`, `--task` is optional. Validate a flow without running it:

```bash
cogito check examples/flows/peer_review.yaml
```

```yaml
# examples/flows/peer_review.yaml
task: "Peer-review the attached claim"
steps:
  - name: perceive
    role: Perceiver
    instruction: "Restate the claim and what would count as evidence for or against it."
  - name: challenge
    role: Skeptic
    instruction: "Find the weakest premise. Refuse with [REFUSAL] if the claim is unfalsifiable."
  - name: verdict
    role: Auditor
    instruction: "Label each claim Measured / Replicated / Simulated / Analogous / Placeholder."
```

---

## What this actually looks like

- One small Python package, stdlib-first. The only hard dependency is PyYAML (for flow files).
- Providers behind one function: OpenAI-compatible and Anthropic-compatible endpoints.
- Every result carries: role, the model the provider reported (and the one requested), provider, endpoint, temperature, duration, and whether it was a refusal. A failed step raises `FlowAborted`, which keeps the completed steps on `.partial`.
- Flows are files. If you can read YAML, you can audit a cognitive pipeline — and unknown keys are rejected rather than silently ignored.

## What CogitoEngine is not

- A claim that chained agents are trustworthy
- An autonomous system
- A framework with a thousand knobs
- A promise of emergent intelligence

It is a workbench for assembling thinking, and for catching the assembly being wrong.

---

## Current state (honest orientation)

| Capability | State |
|---|---|
| Build contract ([Cogito_Engine.md](Cogito_Engine.md)) | v0.2 proposed (2026-11-09, amends v0.1 of 2026-10-31) — human ratification pending |
| Agent roles + refusal protocol | Implemented (v0) |
| Linear flows with shared notebook | Implemented (v0) |
| YAML flow assembly (strictly validated) | Implemented (v0.1.1) |
| CLI (`cogito run`, `cogito check`) | Implemented (v0.1.1) |
| Role-specific contract text, partial results on failure, reported-vs-requested model | Implemented (v0.1.2) — experimental until contract v0.2 is ratified |
| Offline tests (`python -m unittest discover tests`) | Implemented (v0.1.2) — cover contract mechanics, not model behavior |
| Branching / DAG flows | Specified, not built |
| Cross-step memory beyond the notebook | Not built |
| Independent agent verification (not same-model echo) | Open — see `docs/Unknowns.md` |
| Coherence threshold (audit-readiness gate) | Specified, not built — deferred until CE-U03 has a benchmark |
| Benchmarks | Not attempted |

Specified is not demonstrated. A role declaration is not a guarantee the model plays the role. That gap is tracked, not hidden.

## Unknowns

Open questions live in [`docs/Unknowns.md`](docs/Unknowns.md) and are not allowed to be buried.

## Contribute

Bring evidence. Run a flow on a task you know cold, and tell us where it failed. Open an issue with the transcript. Failed flows are field data.

- **Context sibling:** [LazarusForge](https://github.com/ksarith/LazarusForge) — the material-side experiment sharing this epistemic doctrine.

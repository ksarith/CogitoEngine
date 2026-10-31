# CogitoEngine

> *The purpose of CogitoEngine is not to make agents.*  
> *The purpose is to make thinking assemble-able.*

CogitoEngine is a scrappy open-source experiment in **multi-agent cognitive flow in applicable, easy assembly** — a small Python library and CLI for wiring AI agents into flows where every agent declares its role, every output carries provenance, and refusal of a bad premise is a first-class result.

It is the cognitive sibling of the [Lazarus Forge](https://github.com/ksarith/LazarusForge): where the Forge salvages material value, CogitoEngine salvages reasoning value. Nothing gets discarded without accounting — not scrap, not a failed hypothesis, not a weak argument.

The project assumes that agents can hallucinate, that confidence is not truth, and that a chain of prompts is not a chain of custody. So every result records **who said it, under what role, with which model**.

---

## The assembly model (proposal, v0)

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

Refusal rule: any agent may return `[REFUSAL] <reason>` instead of an answer. A refusal is a valid, logged output — not an error. A flow that refuses a bad task has worked correctly.

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
- Every result carries: role, model, provider, and whether it was a refusal.
- Flows are files. If you can read YAML, you can audit a cognitive pipeline.

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
| Agent roles + refusal protocol | Implemented (v0) |
| Linear flows with shared notebook | Implemented (v0) |
| YAML flow assembly | Implemented (v0) |
| CLI (`cogito run`) | Implemented (v0) |
| Branching / DAG flows | Specified, not built |
| Cross-step memory beyond the notebook | Not built |
| Independent agent verification (not same-model echo) | Open — see `docs/Unknowns.md` |
| Benchmarks | Not attempted |

Specified is not demonstrated. A role declaration is not a guarantee the model plays the role. That gap is tracked, not hidden.

## Unknowns

Open questions live in [`docs/Unknowns.md`](docs/Unknowns.md) and are not allowed to be buried.

## Contribute

Bring evidence. Run a flow on a task you know cold, and tell us where it failed. Open an issue with the transcript. Failed flows are field data.

- **Context sibling:** [LazarusForge](https://github.com/ksarith/LazarusForge) — the material-side experiment sharing this epistemic doctrine.

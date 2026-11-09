"""Flows: ordered agent steps sharing an append-only notebook."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .agent import Agent, AgentResult
from .llm import LLMError

# Step keys are the contract v0.1 assembly key set (§7 C5) and do not grow
# without an instrument version bump. The top-level "disclosure" key is an
# EXPERIMENTAL run-metadata extension (contract §8: a runtime ahead of the
# contract ships as experimental until the contract is amended): additive
# provenance only, never interpreted as an independence claim.
ALLOWED_TOP_KEYS = {"name", "task", "steps", "disclosure"}
ALLOWED_STEP_KEYS = {"name", "role", "instruction", "model", "provider", "stop_on_refusal"}


@dataclass
class StepResult:
    step_name: str
    agent_result: AgentResult


@dataclass
class FlowResult:
    task: str
    steps: list[StepResult] = field(default_factory=list)
    # Run-level disclosure metadata (experimental): captures what the method
    # (LazarusForge Tests/Cogito_Engine.md v0.4, P5) requires an attack pass
    # to disclose — reviewer line, model family, shared-context exposure —
    # so a FlowResult is self-describing about its own non-independence.
    # Free-form mapping; absence means "not disclosed", which is itself a
    # disclosure state, never a independence claim.
    disclosure: dict = field(default_factory=dict)

    @property
    def final(self) -> str:
        return self.steps[-1].agent_result.output if self.steps else ""

    @property
    def refused(self) -> StepResult | None:
        return next((s for s in self.steps if s.agent_result.refusal), None)

    def notebook(self) -> dict[str, str]:
        return {s.step_name: s.agent_result.output for s in self.steps}


class FlowAborted(LLMError):
    """A step failed (e.g. provider error) after earlier steps completed.

    The completed steps are evidence and are not discarded: they are on
    ``.partial`` (a FlowResult). The failure is loud, not a refusal, and is
    never presented as a flow result: ``.partial.final`` is NOT an answer.
    """

    def __init__(self, step_name: str, partial: "FlowResult", cause: Exception):
        super().__init__(f"step {step_name!r} failed after {len(partial.steps)} "
                         f"completed step(s): {cause}")
        self.step_name = step_name
        self.partial = partial


class Step:
    def __init__(self, agent: Agent, name: str | None = None,
                 stop_on_refusal: bool = False):
        self.agent = agent
        self.name = name or agent.name
        self.stop_on_refusal = stop_on_refusal


class Flow:
    """An ordered chain of agents. Each step sees the task + the notebook."""

    def __init__(self, steps: list[Step], name: str = "flow",
                 default_task: str | None = None,
                 disclosure: dict | None = None):
        if not steps:
            raise ValueError("a flow needs at least one step")
        if disclosure is not None and not isinstance(disclosure, dict):
            raise ValueError("disclosure must be a mapping (line / model family / "
                             "shared-context exposure), got "
                             f"{type(disclosure).__name__}")
        seen: set[str] = set()
        for s in steps:
            if s.name in seen:
                raise ValueError(f"duplicate step name {s.name!r} \u2014 "
                                 "notebook keys must be unique (contract section 3)")
            seen.add(s.name)
        self.steps = steps
        self.name = name
        self.default_task = default_task
        self.disclosure = disclosure or {}

    def run(self, task: str) -> FlowResult:
        result = FlowResult(task=task, disclosure=dict(self.disclosure))
        notebook: dict[str, str] = {}
        for step in self.steps:
            try:
                ar = step.agent.run(task, notebook)
            except LLMError as exc:
                raise FlowAborted(step.name, result, exc) from exc
            result.steps.append(StepResult(step_name=step.name, agent_result=ar))
            notebook[step.name] = ar.output
            if ar.refusal and step.stop_on_refusal:
                break
        return result


# ---------------------------------------------------------------- presets

def _preset(name: str, role: str, instruction: str) -> Agent:
    return Agent(name=name, role=role, instruction=instruction)


def cognitive_flow(task_hint: str = "") -> Flow:
    """The default Cogito flow: Perceive -> Engineer -> Skeptic -> Auditor -> Synthesizer.

    Mirrors the Lazarus Forge role doctrine: refusal of a bad premise is a
    first-class output, and evidence labels beat vibes. A Skeptic refusal
    halts the flow after it is recorded — a flow that refuses a bad task
    has worked, not failed.
    """
    pre = f" {task_hint}" if task_hint else ""
    steps = [
        Step(_preset("perceive", "Perceiver",
                     "Restate the task in your own words. Name what is actually being "
                     "asked, the assumptions baked into the question, and what would count "
                     "as a good answer." + pre)),
        Step(_preset("engineer", "Engineer",
                     "Propose one concrete answer or design. Be specific and buildable. "
                     "Prefer salvage-simple over elegant.")),
        Step(_preset("skeptic", "Skeptic",
                     "Attack the premise and the Engineer's proposal. Name the single "
                     "weakest premise and the most likely failure mode. You are not "
                     "allowed to be a cheerleader. Refuse with [REFUSAL] if the premise "
                     "is unfalsifiable or unsafe."),
             stop_on_refusal=True),
        Step(_preset("audit", "Auditor",
                     "Check the Engineer's claims against the notebook. Label each "
                     "significant claim as Measured / Replicated / Simulated / "
                     "Analogous / Placeholder. Flag anything that is asserted without "
                     "evidence.")),
        Step(_preset("synthesize", "Synthesizer",
                     "Produce the final answer: what survives the Skeptic and Auditor, "
                     "what remains uncertain, and what the next concrete test would be. "
                     "Cite which notebook steps you relied on."),
             stop_on_refusal=True),
    ]
    return Flow(steps, name="cognitive")


def flow_from_yaml(path: str | Path) -> Flow:
    """Assemble a flow from a YAML file, validated against the build contract.

    Expected shape:

        name: optional flow name
        task: optional default task
        disclosure: optional run-level disclosure mapping (EXPERIMENTAL —
          reviewer line, model family, shared-context exposure; carried into
          FlowResult verbatim; contract v0.1 does not define it, §8 applies)
        steps:
          - name: perceive
            role: Perceiver
            instruction: ...
            model: optional
            provider: optional
            stop_on_refusal: optional bool

    Unknown keys, non-mapping steps, and duplicate step names are rejected
    (notebook keys must be unique — contract section 3). Typos fail loudly:
    a flow file you can audit must not silently ignore half of itself.
    """
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML: {exc}") from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top level must be a mapping, got {type(data).__name__}")

    unknown_top = set(data) - ALLOWED_TOP_KEYS
    if unknown_top:
        raise ValueError(f"{path}: unknown top-level keys {sorted(unknown_top)}; "
                         f"allowed: {sorted(ALLOWED_TOP_KEYS)}")

    raw_steps = data.get("steps") or []
    if not raw_steps:
        raise ValueError(f"no steps found in {path}")
    if not isinstance(raw_steps, list):
        raise ValueError(f"{path}: 'steps' must be a list")

    task = data.get("task")
    if task is not None and not isinstance(task, str):
        raise ValueError(f"{path}: 'task' must be a string")

    disclosure = data.get("disclosure")
    if disclosure is not None and not isinstance(disclosure, dict):
        raise ValueError(f"{path}: 'disclosure' must be a mapping (reviewer line, "
                         f"model family, shared-context exposure), got "
                         f"{type(disclosure).__name__}")

    steps: list[Step] = []
    seen: set[str] = set()
    for i, spec in enumerate(raw_steps, 1):
        if spec is None:
            spec = {}
        if not isinstance(spec, dict):
            raise ValueError(f"{path}: step {i} must be a mapping, got {type(spec).__name__}")
        unknown = set(spec) - ALLOWED_STEP_KEYS
        if unknown:
            raise ValueError(f"{path}: step {i} has unknown keys {sorted(unknown)}; "
                             f"allowed: {sorted(ALLOWED_STEP_KEYS)}")
        name = spec.get("name") or f"step{i}"
        if name in seen:
            raise ValueError(f"{path}: duplicate step name {name!r} — "
                             "notebook keys must be unique (contract section 3)")
        seen.add(name)
        sor = spec.get("stop_on_refusal", False)
        if not isinstance(sor, bool):
            raise ValueError(f"{path}: step {i} ({name!r}): stop_on_refusal must be "
                             f"a boolean, got {type(sor).__name__}")
        agent = Agent(
            name=name,
            role=spec.get("role") or "Worker",
            instruction=spec.get("instruction") or "Do the task.",
            model=spec.get("model"),
            provider=spec.get("provider"),
        )
        steps.append(Step(agent, name=agent.name, stop_on_refusal=sor))
    return Flow(steps, name=data.get("name") or Path(path).stem, default_task=task,
                disclosure=disclosure)

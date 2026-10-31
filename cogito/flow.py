"""Flows: ordered agent steps sharing an append-only notebook."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .agent import Agent, AgentResult


@dataclass
class StepResult:
    step_name: str
    agent_result: AgentResult


@dataclass
class FlowResult:
    task: str
    steps: list[StepResult] = field(default_factory=list)

    @property
    def final(self) -> str:
        return self.steps[-1].agent_result.output if self.steps else ""

    @property
    def refused(self) -> StepResult | None:
        return next((s for s in self.steps if s.agent_result.refusal), None)

    def notebook(self) -> dict[str, str]:
        return {s.step_name: s.agent_result.output for s in self.steps}


class Step:
    def __init__(self, agent: Agent, name: str | None = None,
                 stop_on_refusal: bool = False):
        self.agent = agent
        self.name = name or agent.name
        self.stop_on_refusal = stop_on_refusal


class Flow:
    """An ordered chain of agents. Each step sees the task + the notebook."""

    def __init__(self, steps: list[Step], name: str = "flow"):
        if not steps:
            raise ValueError("a flow needs at least one step")
        self.steps = steps
        self.name = name

    def run(self, task: str) -> FlowResult:
        result = FlowResult(task=task)
        notebook: dict[str, str] = {}
        for step in self.steps:
            ar = step.agent.run(task, notebook)
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
    first-class output, and evidence labels beat vibes.
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
                     "is unfalsifiable or unsafe.")),
        Step(_preset("audit", "Auditor",
                     "Check the Engineer's claims against the notebook. Label each "
                     "significant claim as Measured / Replicated / Simulated / "
                     "Analogous / Placeholder. Flag anything that is asserted without "
                     "evidence.")),
        Step(_preset("synthesize", "Synthesizer",
                     "Produce the final answer: what survives the Skeptic and Auditor, "
                     "what remains uncertain, and what the next concrete test would be. "
                     "Cite which notebook steps you relied on."), stop_on_refusal=True),
    ]
    return Flow(steps, name="cognitive")


def flow_from_yaml(path: str | Path) -> Flow:
    """Assemble a flow from a YAML file.

    Expected shape:

        task: optional default task
        steps:
          - name: perceive
            role: Perceiver
            instruction: ...
            model: optional
            provider: optional
            stop_on_refusal: optional bool
    """
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    raw_steps = data.get("steps") or []
    if not raw_steps:
        raise ValueError(f"no steps found in {path}")
    steps = []
    for i, spec in enumerate(raw_steps, 1):
        spec = spec or {}
        agent = Agent(
            name=spec.get("name") or f"step{i}",
            role=spec.get("role") or "Worker",
            instruction=spec.get("instruction") or "Do the task.",
            model=spec.get("model"),
            provider=spec.get("provider"),
        )
        steps.append(Step(agent, name=agent.name,
                          stop_on_refusal=bool(spec.get("stop_on_refusal", False))))
    return Flow(steps, name=data.get("name") or Path(path).stem)

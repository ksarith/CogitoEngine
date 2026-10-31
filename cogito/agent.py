"""Agents with declared roles and refusal as a first-class output."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .llm import REFUSAL_MARKER, call_llm

ROLE_CONTRACT = (
    "You are an AI agent operating inside CogitoEngine under a declared role. "
    "Stay inside your role. Do not perform other steps' jobs. "
    f"If the task or a prior premise is wrong, unfalsifiable, or beyond your role, "
    f"begin your reply with '{REFUSAL_MARKER}' followed by a one-sentence reason. "
    "A refusal is a valid output; fabricating an answer is not."
)


@dataclass
class AgentResult:
    agent_name: str
    role: str
    output: str
    refusal: bool
    model: str
    provider: str
    seconds: float
    prompt: str = field(default="")

    def __repr__(self) -> str:
        flag = " [REFUSAL]" if self.refusal else ""
        return f"<{self.agent_name} ({self.role}){flag} {self.model}/{self.provider}>"


class Agent:
    """A declared role + instruction + model. Nothing else.

    The role is a contract, not a decoration: it is prepended to the system
    prompt so the model knows what it is allowed — and required — to do.
    """

    def __init__(self, name: str, role: str, instruction: str,
                 *, model: str | None = None, provider: str | None = None):
        if not name or not role:
            raise ValueError("agents must declare both a name and a role")
        self.name = name
        self.role = role
        self.instruction = instruction
        self.model = model
        self.provider = provider

    def build_prompt(self, task: str, notebook: dict[str, str]) -> str:
        lines = [f"# Task\n{task}\n", "# Notebook (append-only record of prior steps)"]
        if notebook:
            for step_name, text in notebook.items():
                lines.append(f"## {step_name}\n{text}\n")
        else:
            lines.append("(empty — you are the first step)\n")
        lines.append(f"# Your role: {self.role}\n# Your instruction\n{self.instruction}\n"
                      f"Produce your step output now.")
        return "\n".join(lines)

    def run(self, task: str, notebook: dict[str, str] | None = None) -> AgentResult:
        notebook = notebook or {}
        prompt = self.build_prompt(task, notebook)
        started = time.time()
        resp = call_llm(prompt, system=ROLE_CONTRACT,
                        model=self.model, provider=self.provider)
        refusal = resp.text.strip().startswith(REFUSAL_MARKER)
        return AgentResult(
            agent_name=self.name, role=self.role, output=resp.text,
            refusal=refusal, model=resp.model, provider=resp.provider,
            seconds=round(time.time() - started, 2), prompt=prompt,
        )

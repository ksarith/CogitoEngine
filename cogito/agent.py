"""Agents with declared roles and refusal as a first-class output."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .llm import REFUSAL_MARKER, call_llm, is_refusal

ROLE_CONTRACT = (
    "You are an AI agent operating inside CogitoEngine under a declared role. "
    "Stay inside your role. Do not perform other steps' jobs. "
    f"If the task or a prior premise is wrong, unfalsifiable, or beyond your role, "
    f"begin your reply with '{REFUSAL_MARKER}' followed by a one-sentence reason. "
    "A refusal is a valid output; fabricating an answer is not."
)

# Role-specific contracts: the Allowed / Forbidden columns of Cogito_Engine.md
# section 2, so the role channel carries the contract itself and not only the
# role's name (contract C1). A role with no entry gets the generic contract
# plus its instruction. Whether the model honors any of this is Unknown CE-U01.
ROLE_CONTRACTS = {
    "perceiver": (
        "Role contract (Perceiver). Allowed: restate the task; surface baked-in "
        "assumptions; define what would count as a good answer. Forbidden: "
        "proposing the solution."),
    "engineer": (
        "Role contract (Engineer). Allowed: propose one concrete, buildable answer "
        "or design. Forbidden: auditing your own evidence; attacking your own "
        "proposal (that is the Skeptic's job)."),
    "skeptic": (
        "Role contract (Skeptic). Allowed: attack the premise and the proposal; "
        "name the single weakest premise and the most likely failure mode; refuse. "
        "Forbidden: cheerleading; proposing a replacement design."),
    "auditor": (
        "Role contract (Auditor). Allowed: check claims against the notebook; "
        "assign evidence labels (Measured / Replicated / Simulated / Analogous / "
        "Placeholder); flag assertions without evidence. Forbidden: introducing "
        "new substantive proposals."),
    "synthesizer": (
        "Role contract (Synthesizer). Allowed: produce the final answer with "
        "provenance, surviving uncertainties, and the next concrete test. "
        "Forbidden: dropping a refusal; inventing evidence absent from the notebook."),
    "worker": (
        "Role contract (Worker). The instruction below is your contract. "
        "Forbidden: exceeding your declared instruction."),
}


def system_for(role: str) -> str:
    """The system prompt for a role: generic contract + the role's own contract."""
    extra = ROLE_CONTRACTS.get(role.strip().lower())
    return f"{ROLE_CONTRACT}\n\n{extra}" if extra else ROLE_CONTRACT


@dataclass
class AgentResult:
    agent_name: str
    role: str
    output: str
    refusal: bool
    model: str            # as reported by the provider (see LLMResponse)
    provider: str
    seconds: float
    prompt: str = field(default="")
    system: str = field(default="")
    requested_model: str = field(default="")
    base_url: str = field(default="")
    temperature: float | None = field(default=None)

    def __repr__(self) -> str:
        flag = " [REFUSAL]" if self.refusal else ""
        return f"<{self.agent_name} ({self.role}){flag} {self.model}/{self.provider}>"


class Agent:
    """A declared role + instruction + model. Nothing else.

    The role is a contract, not a decoration: its contract text is sent as the
    system prompt so the model knows what it is allowed - and required - to do.
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

    @property
    def system(self) -> str:
        return system_for(self.role)

    def build_prompt(self, task: str, notebook: dict[str, str]) -> str:
        lines = [f"# Task\n{task}\n", "# Notebook (append-only record of prior steps)"]
        if notebook:
            for step_name, text in notebook.items():
                lines.append(f"## {step_name}\n{text}\n")
        else:
            lines.append("(empty \u2014 you are the first step)\n")
        lines.append(f"# Your role: {self.role}\n# Your instruction\n{self.instruction}\n"
                      f"Produce your step output now.")
        return "\n".join(lines)

    def run(self, task: str, notebook: dict[str, str] | None = None) -> AgentResult:
        notebook = notebook or {}
        prompt = self.build_prompt(task, notebook)
        system = self.system
        started = time.time()
        resp = call_llm(prompt, system=system,
                        model=self.model, provider=self.provider)
        return AgentResult(
            agent_name=self.name, role=self.role, output=resp.text,
            refusal=is_refusal(resp.text), model=resp.model, provider=resp.provider,
            seconds=round(time.time() - started, 2), prompt=prompt, system=system,
            requested_model=resp.requested_model, base_url=resp.base_url,
            temperature=resp.temperature,
        )

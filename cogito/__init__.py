"""CogitoEngine: multi-agent cognitive flow in applicable, easy assembly."""

from .agent import Agent, AgentResult
from .flow import Flow, FlowResult, cognitive_flow, flow_from_yaml
from .llm import LLMResponse, call_llm

__version__ = "0.1.1"

# Build-contract declaration (Cogito_Engine.md §7 C8): this runtime
# implements Cogito_Engine.md v0.1 as a declared subset — linear flows
# only; no branching/DAG, no coherence-threshold gate, no cross-step
# memory beyond the notebook, no independent (non-same-model)
# verification. Gaps are tracked in docs/Unknowns.md (CE-U01..CE-U06).
INSTRUMENT = "Cogito_Engine.md"
INSTRUMENT_VERSION = "0.1"

__all__ = [
    "Agent", "AgentResult",
    "Flow", "FlowResult", "cognitive_flow", "flow_from_yaml",
    "LLMResponse", "call_llm",
    "INSTRUMENT", "INSTRUMENT_VERSION",
]

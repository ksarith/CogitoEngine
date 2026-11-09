"""CogitoEngine: multi-agent cognitive flow in applicable, easy assembly."""

from .agent import Agent, AgentResult
from .flow import Flow, FlowAborted, FlowResult, cognitive_flow, flow_from_yaml
from .llm import LLMResponse, call_llm, is_refusal

__version__ = "0.1.2"

# Build-contract declaration (Cogito_Engine.md section 7 C8): this runtime is
# checked against Cogito_Engine.md v0.2 (ratified 2026-11-09) and implements it as a declared subset
# - linear flows only; no branching/DAG, no coherence-threshold gate, no
# cross-step memory beyond the notebook, no independent (non-same-model)
# verification. Gaps are tracked in docs/Unknowns.md (CE-U01..CE-U07).
#
# The v0.2 amendments (role-specific contract text in the system prompt,
# completed steps preserved on a failed step (FlowAborted),
# reported-vs-requested model plus endpoint/temperature in provenance,
# markdown/case-tolerant refusal marker) and the top-level `disclosure` flow
# key were experimental while v0.2 was pending and are conformant as of its
# ratification (contract section 8).
INSTRUMENT = "Cogito_Engine.md"
INSTRUMENT_VERSION = "0.2"

__all__ = [
    "Agent", "AgentResult",
    "Flow", "FlowAborted", "FlowResult", "cognitive_flow", "flow_from_yaml",
    "LLMResponse", "call_llm", "is_refusal",
    "INSTRUMENT", "INSTRUMENT_VERSION",
]

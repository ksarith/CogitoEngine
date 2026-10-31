"""CogitoEngine: multi-agent cognitive flow in applicable, easy assembly."""

from .agent import Agent, AgentResult
from .flow import Flow, FlowResult, cognitive_flow, flow_from_yaml
from .llm import LLMResponse, call_llm

__version__ = "0.1.0"
__all__ = [
    "Agent", "AgentResult",
    "Flow", "FlowResult", "cognitive_flow", "flow_from_yaml",
    "LLMResponse", "call_llm",
]

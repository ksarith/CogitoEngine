"""Offline tests for the runtime contract claims. No network, no API keys.

Run: python -m unittest discover tests
"""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cogito import Agent, Flow, FlowAborted, cognitive_flow, flow_from_yaml, is_refusal  # noqa: E402
from cogito.flow import Step  # noqa: E402
from cogito.llm import LLMError, LLMResponse  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def fake(text="ok", reported="model-x-20261101", requested="model-x-latest"):
    return LLMResponse(text, reported, "mistral", requested_model=requested,
                       base_url="https://example.test/v1", temperature=0.2)


class RefusalDetection(unittest.TestCase):
    def test_detected(self):
        for t in ["[REFUSAL] bad", "  [REFUSAL] x", "**[REFUSAL]** x",
                  "> [refusal] x", "# [Refusal] x"]:
            self.assertTrue(is_refusal(t), t)

    def test_not_detected(self):  # documented limits (CE-U05)
        for t in ["Sure.\n[REFUSAL] x", "I cannot do that.", "ok [REFUSAL]"]:
            self.assertFalse(is_refusal(t), t)


class RoleChannel(unittest.TestCase):
    def test_role_contract_text_reaches_system_prompt(self):
        with mock.patch("cogito.agent.call_llm", return_value=fake()) as m:
            Agent("s", "Skeptic", "attack it").run("task")
        system = m.call_args.kwargs["system"]
        self.assertIn("Forbidden: cheerleading", system)
        self.assertIn("[REFUSAL]", system)

    def test_custom_role_gets_generic_contract_only(self):
        with mock.patch("cogito.agent.call_llm", return_value=fake()) as m:
            Agent("x", "Cartographer", "map it").run("task")
        self.assertNotIn("Role contract (", m.call_args.kwargs["system"])


class Provenance(unittest.TestCase):
    def test_reported_and_requested_model_both_recorded(self):
        with mock.patch("cogito.agent.call_llm", return_value=fake()):
            ar = Agent("a", "Worker", "do").run("task")
        self.assertEqual(ar.model, "model-x-20261101")
        self.assertEqual(ar.requested_model, "model-x-latest")
        self.assertEqual(ar.base_url, "https://example.test/v1")
        self.assertEqual(ar.temperature, 0.2)
        self.assertIn("Worker", ar.system)


class FlowBehavior(unittest.TestCase):
    def test_duplicate_step_names_rejected_from_code(self):
        a, b = Agent("same", "Worker", "x"), Agent("same", "Worker", "y")
        with self.assertRaises(ValueError):
            Flow([Step(a), Step(b)])

    def test_completed_steps_survive_a_failed_step(self):
        calls = {"n": 0}

        def flaky(*a, **k):
            calls["n"] += 1
            if calls["n"] == 3:
                raise LLMError("provider returned 500")
            return fake(f"output {calls['n']}")

        with mock.patch("cogito.agent.call_llm", side_effect=flaky):
            with self.assertRaises(FlowAborted) as cm:
                cognitive_flow().run("task")
        exc = cm.exception
        self.assertIsInstance(exc, LLMError)          # old `except LLMError` still works
        self.assertEqual(exc.step_name, "skeptic")
        self.assertEqual([s.step_name for s in exc.partial.steps], ["perceive", "engineer"])

    def test_stop_on_refusal(self):
        outs = iter([fake("framed"), fake("design"), fake("**[REFUSAL]** unfalsifiable")])
        with mock.patch("cogito.agent.call_llm", side_effect=lambda *a, **k: next(outs)):
            result = cognitive_flow().run("task")
        self.assertEqual(len(result.steps), 3)
        self.assertEqual(result.refused.step_name, "skeptic")

    def test_shipped_yaml_flows_validate(self):
        for p in [ROOT / "examples/flows/peer_review.yaml",
                  ROOT / "docs/trials/cold_start_run_01/flows/phase_b_ice_harvest.yaml"]:
            self.assertTrue(flow_from_yaml(p).steps)


if __name__ == "__main__":
    unittest.main()

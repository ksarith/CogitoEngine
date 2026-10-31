"""Minimal example: assemble a flow in three lines of Python."""

from cogito import cognitive_flow

flow = cognitive_flow()
result = flow.run("Should a small workshop repair or scrap a 15-year-old power drill?")

print(result.final)
print()
print("--- provenance ---")
for step in result.steps:
    ar = step.agent_result
    print(f"{step.step_name:12s} {ar.role:12s} {ar.model}/{ar.provider}"
          f"{'  [REFUSAL]' if ar.refusal else ''}")

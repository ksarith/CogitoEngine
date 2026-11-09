"""CLI: cogito run <flow.yaml> [--task "..."] / cogito check <flow.yaml> / cogito demo"""

from __future__ import annotations

import argparse
import sys

from .flow import FlowAborted, cognitive_flow, flow_from_yaml
from .llm import LLMError


def _print(result) -> None:
    print("=" * 60)
    for s in result.steps:
        ar = s.agent_result
        flag = "  [REFUSAL]" if ar.refusal else ""
        print(f"[{s.step_name}] {ar.role} ({ar.model}/{ar.provider}, {ar.seconds}s){flag}")
        print("-" * 60)
        print(ar.output.strip())
        print()
    print("=" * 60)
    if result.refused:
        r = result.refused
        print(f"Flow refused at step '{r.step_name}'. That is a valid outcome, not a crash.")


def _run(flow, task: str):
    """Run a flow; on a mid-run failure print the completed steps, then fail."""
    try:
        return flow.run(task), 0
    except FlowAborted as exc:
        _print(exc.partial)
        print(f"error: {exc}", file=sys.stderr)
        return None, 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cogito",
                                     description="Multi-agent cognitive flow runner.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="run a YAML flow")
    p_run.add_argument("flow", help="path to a .yaml flow file")
    p_run.add_argument("--task", default=None,
                       help="the task text (optional if the flow YAML defines task:)")

    p_check = sub.add_parser("check", help="validate a YAML flow without running it")
    p_check.add_argument("flow", help="path to a .yaml flow file")

    p_demo = sub.add_parser("demo", help="run the built-in cognitive flow on a sample task")
    p_demo.add_argument("--task", default="Design a cheap rainwater filter from salvage parts.")

    args = parser.parse_args(argv)
    try:
        if args.cmd == "check":
            flow = flow_from_yaml(args.flow)
            names = [s.name for s in flow.steps]
            print(f"valid: flow '{flow.name}' — {len(names)} step(s): {', '.join(names)}")
            if flow.default_task:
                print(f"default task: {flow.default_task!r}")
            else:
                print("no default task — pass --task when running")
            return 0
        if args.cmd == "run":
            flow = flow_from_yaml(args.flow)
            task = args.task or flow.default_task
            if not task:
                print("error: no task given — pass --task or set 'task:' in the flow YAML",
                      file=sys.stderr)
                return 1
            result, rc = _run(flow, task)
        else:
            result, rc = _run(cognitive_flow(), args.task)
        if rc:
            return rc
    except (LLMError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

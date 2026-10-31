"""CLI: cogito run <flow.yaml> --task "..." / cogito demo"""

from __future__ import annotations

import argparse
import sys

from .flow import cognitive_flow, flow_from_yaml
from .llm import LLMError


def _print(result) -> None:
    print("=" * 60)
    for s in result.steps:
        ar = s.agent_result
        flag = "  [REFUSAL]" if ar.refusal else ""
        print(f"[{s.step_name}] {ar.role} ({ar.model}/{ar.provider}){flag}")
        print("-" * 60)
        print(ar.output.strip())
        print()
    print("=" * 60)
    if result.refused:
        r = result.refused
        print(f"Flow refused at step '{r.step_name}'. That is a valid outcome, not a crash.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cogito",
                                     description="Multi-agent cognitive flow runner.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="run a YAML flow")
    p_run.add_argument("flow", help="path to a .yaml flow file")
    p_run.add_argument("--task", required=True, help="the task text")

    sub.add_parser("demo", help="run the built-in cognitive flow on a sample task")
    demo_p = sub._subparsers._group_actions[0].choices["demo"]  # noqa: SLF001
    demo_p.add_argument("--task", default="Design a cheap rainwater filter from salvage parts.")

    args = parser.parse_args(argv)
    try:
        if args.cmd == "run":
            result = flow_from_yaml(args.flow).run(args.task)
        else:
            result = cognitive_flow().run(args.task)
    except (LLMError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

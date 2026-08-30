#!/usr/bin/env python3
"""Small deterministic state helper for the Codex Gauntlet skill."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

DEFAULT_PATH = Path(".gauntlet/state.json")


def now():
    return datetime.now(timezone.utc).isoformat()


def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp.replace(path)


def cmd_init(args):
    path = Path(args.path)
    data = {
        "task": args.task,
        "iteration": 0,
        "max_iterations": args.max_iterations,
        "minimum_judge_score": args.min_score,
        "acceptance_criteria": [],
        "issues": [],
        "history": [],
        "verdict": "RUNNING",
        "created_at": now(),
        "updated_at": now(),
    }
    save(path, data)
    print(path)


def cmd_show(args):
    print(json.dumps(load(Path(args.path)), indent=2, ensure_ascii=False))


def cmd_round(args):
    path = Path(args.path)
    data = load(path)
    data["iteration"] += 1
    item = {
        "iteration": data["iteration"],
        "judge_score": args.score,
        "verdict": args.verdict,
        "blocking_issues": args.blocking_issue or [],
        "timestamp": now(),
    }
    data["history"].append(item)
    data["verdict"] = args.verdict
    data["updated_at"] = now()
    save(path, data)
    print(json.dumps(item, indent=2))


def cmd_issue(args):
    path = Path(args.path)
    data = load(path)
    data.setdefault("issues", []).append({
        "id": args.id,
        "severity": args.severity,
        "status": args.status,
        "description": args.description,
        "evidence": args.evidence,
        "timestamp": now(),
    })
    data["updated_at"] = now()
    save(path, data)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--path", default=str(DEFAULT_PATH))
    sub = p.add_subparsers(dest="cmd", required=True)

    x = sub.add_parser("init")
    x.add_argument("--task", required=True)
    x.add_argument("--max-iterations", type=int, default=4)
    x.add_argument("--min-score", type=float, default=0.90)
    x.set_defaults(func=cmd_init)

    x = sub.add_parser("show")
    x.set_defaults(func=cmd_show)

    x = sub.add_parser("round")
    x.add_argument("--score", type=float, required=True)
    x.add_argument("--verdict", choices=["PASS", "REVISE", "FAIL", "BEST_EFFORT"], required=True)
    x.add_argument("--blocking-issue", action="append")
    x.set_defaults(func=cmd_round)

    x = sub.add_parser("issue")
    x.add_argument("--id", required=True)
    x.add_argument("--severity", choices=["critical", "high", "medium", "low"], required=True)
    x.add_argument("--status", choices=["open", "fixed", "mitigated", "rejected", "deferred"], required=True)
    x.add_argument("--description", required=True)
    x.add_argument("--evidence", default="")
    x.set_defaults(func=cmd_issue)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

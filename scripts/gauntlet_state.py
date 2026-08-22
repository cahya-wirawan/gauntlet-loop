#!/usr/bin/env python3
"""Optional compact state ledger for long Gauntlet runs."""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT = Path(".gauntlet/state.json")

def now():
    return datetime.now(timezone.utc).isoformat()

def load(path):
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)

def save(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(p)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=str(DEFAULT))
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init")
    p.add_argument("--task", required=True)
    p.add_argument("--max-iterations", type=int, default=4)
    p.add_argument("--min-score", type=float, default=0.90)

    p = sub.add_parser("show")

    p = sub.add_parser("round")
    p.add_argument("--score", type=float, required=True)
    p.add_argument("--verdict", choices=["PASS","REVISE","FAIL","BEST_EFFORT"], required=True)
    p.add_argument("--blocking-issue", action="append", default=[])

    args = ap.parse_args()
    path = Path(args.path)

    if args.cmd == "init":
        obj = {
            "task": args.task,
            "iteration": 0,
            "max_iterations": args.max_iterations,
            "minimum_judge_score": args.min_score,
            "history": [],
            "verdict": "RUNNING",
            "created_at": now(),
            "updated_at": now()
        }
        save(path, obj)
        print(path)
    elif args.cmd == "show":
        print(json.dumps(load(path), indent=2, ensure_ascii=False))
    else:
        obj = load(path)
        obj["iteration"] += 1
        rec = {
            "iteration": obj["iteration"],
            "judge_score": args.score,
            "verdict": args.verdict,
            "blocking_issues": args.blocking_issue,
            "timestamp": now(),
        }
        obj["history"].append(rec)
        obj["verdict"] = args.verdict
        obj["updated_at"] = now()
        save(path, obj)
        print(json.dumps(rec, indent=2))

if __name__ == "__main__":
    main()

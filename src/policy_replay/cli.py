from __future__ import annotations

import argparse
import json
from pathlib import Path

from .loader import load_history, load_rule
from .report import render_report, write_result
from .sim import replay
from .validation import validate_result

ROOT = Path(__file__).resolve().parents[2]


def simulate(rule_path: Path, history_path: Path, out_dir: Path, seed: int) -> dict[str, Path]:
    rule = load_rule(rule_path)
    history = load_history(history_path)
    result = replay(rule, history, history_path.relative_to(ROOT).as_posix(), seed)
    result_path = out_dir / "replay_result.json"
    report_path = out_dir / "report.md"
    write_result(result_path, result)
    render_report(report_path, rule, result)
    validate_result(result_path)
    return {"result_path": result_path, "report_path": report_path}


def validate_all() -> None:
    for path in (ROOT / "reports").glob("*/replay_result.json"):
        validate_result(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="policy-replay")
    sub = parser.add_subparsers(dest="command", required=True)
    sim = sub.add_parser("simulate")
    sim.add_argument("--rule", default="rules/pjm-dec2025-capacity-reform.json")
    sim.add_argument("--history", default="data/history/pjm_rpm_2018_2023.csv")
    sim.add_argument("--out", default="reports/pjm-dec2025-replay")
    sim.add_argument("--seed", type=int, default=20260620)
    sub.add_parser("validate")
    args = parser.parse_args(argv)
    if args.command == "simulate":
        paths = simulate(ROOT / args.rule, ROOT / args.history, ROOT / args.out, args.seed)
        print(json.dumps({key: value.relative_to(ROOT).as_posix() for key, value in paths.items()}, sort_keys=True))
        return 0
    validate_all()
    print("valid: replays")
    return 0


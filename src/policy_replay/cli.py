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


def latest_result() -> Path | None:
    results = sorted((ROOT / "reports").glob("*/replay_result.json"))
    return results[-1] if results else None


def render_show(result: dict, rule_id: str) -> list[str]:
    """Build a readable, ranked view of a committed replay result (no args needed)."""
    base = result["baseline_outcomes"]
    counter = result["counterfactual_outcomes"]
    delta = result["outcome_delta_summary"]

    rows = [
        (
            "clearing price (USD/MW-day)",
            base["mean_price_usd_mw_day"],
            counter["mean_price_usd_mw_day"],
            delta["mean_price_delta_usd_mw_day"],
        ),
        (
            "cleared capacity (MW)",
            base["mean_cleared_mw"],
            counter["mean_cleared_mw"],
            delta["mean_cleared_mw_delta"],
        ),
    ]
    # rank metrics by the relative size of their shift, biggest first
    rows.sort(key=lambda r: abs(r[3] / r[1]) if r[1] else 0.0, reverse=True)

    out = [
        f"policy-replay - counterfactual outcome screen ({rule_id})",
        f"replay {result['replay_id']}  |  history {result['history_snapshot_ref']}  |  seed {result['seed']}",
        "ranked by relative shift under the proposed rule (baseline -> counterfactual)",
        "",
    ]
    header = f"{'metric':<30} {'baseline':>14} {'counterfactual':>16} {'delta':>12} {'shift':>9}"
    out.append(header)
    out.append("-" * len(header))
    for label, b, c, d in rows:
        pct = (d / b * 100) if b else 0.0
        out.append(f"{label:<30} {b:>14,.2f} {c:>16,.2f} {d:>+12,.2f} {pct:>+8.1f}%")

    out.append(f"{'reserve margin (pts)':<30} {'':>14} {'':>16} {delta['reserve_margin_delta_pct']:>+12,.2f} {'':>9}")

    top = rows[0]
    direction = "up" if top[3] > 0 else "down"
    pct = (top[3] / top[1] * 100) if top[1] else 0.0
    out.append("")
    out.append(
        f"headline: under the +{delta['reserve_margin_delta_pct']:.1f}-pt reserve-margin change, "
        f"{top[0].split(' (')[0]} moves {direction} {abs(pct):.1f}% "
        f"({top[1]:,.2f} -> {top[2]:,.2f}). deterministic screen, not a forecast."
    )
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="policy-replay")
    sub = parser.add_subparsers(dest="command", required=True)
    sim = sub.add_parser("simulate")
    sim.add_argument("--rule", default="rules/pjm-dec2025-capacity-reform.json")
    sim.add_argument("--history", default="data/history/pjm_rpm_2018_2023.csv")
    sim.add_argument("--out", default="reports/pjm-dec2025-replay")
    sim.add_argument("--seed", type=int, default=20260620)
    sub.add_parser("validate")
    show = sub.add_parser("show", help="print a readable ranked view of the committed replay result")
    show.add_argument("--result", default=None, help="path to a replay_result.json (default: latest under reports/)")
    args = parser.parse_args(argv)
    if args.command == "simulate":
        paths = simulate(ROOT / args.rule, ROOT / args.history, ROOT / args.out, args.seed)
        print(json.dumps({key: value.relative_to(ROOT).as_posix() for key, value in paths.items()}, sort_keys=True))
        return 0
    if args.command == "show":
        path = Path(args.result) if args.result else latest_result()
        if path is None or not path.is_file():
            raise SystemExit("no replay result found under reports/*/replay_result.json — run `simulate` first")
        result = json.loads(path.read_text(encoding="utf-8"))
        print("\n".join(render_show(result, result.get("rule_id", "?"))))
        return 0
    validate_all()
    print("valid: replays")
    return 0


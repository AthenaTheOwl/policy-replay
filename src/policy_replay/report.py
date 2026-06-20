from __future__ import annotations

import json
from pathlib import Path

from .models import ReplayResult, RuleSpec


def write_result(path: Path, result: ReplayResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_report(path: Path, rule: RuleSpec, result: ReplayResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    delta = result.outcome_delta_summary
    lines = [
        f"# PolicyReplay result - {rule.rule_id}",
        "",
        f"Rule: {rule.name}",
        f"Markets: {', '.join(rule.affected_markets)}",
        "",
        "## outcome delta",
        "",
        f"- mean price delta: {delta['mean_price_delta_usd_mw_day']:.3f} USD/MW-day",
        f"- mean cleared MW delta: {delta['mean_cleared_mw_delta']:.3f}",
        f"- reserve margin delta: {delta['reserve_margin_delta_pct']:.2f} percentage points",
        "",
        "## references",
        "",
    ]
    for ref in rule.references:
        lines.append(f"- {ref}")
    lines.extend(
        [
            "",
            "## methodology",
            "",
            "The v0.1 replay applies a pure parameter override to checked-in PJM RPM fixture history. It is a deterministic counterfactual screen.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


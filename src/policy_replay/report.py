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
    model = result.model
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
        "## model",
        "",
        "This is a fixed-elasticity screen. Each auction's clearing price is scaled by "
        f"1 + {delta['reserve_margin_delta_pct']:g} x {model['price_elasticity_per_margin_point']:g} "
        "and its cleared MW by "
        f"1 + {delta['reserve_margin_delta_pct']:g} x {model['cleared_mw_elasticity_per_margin_point']:g}. "
        f"Elasticity source: {model['elasticity_source']}.",
        "",
        f"- price shift: {model['price_shift_pct']:+.3f}% on every auction",
        f"- cleared MW shift: {model['cleared_mw_shift_pct']:+.3f}% on every auction",
        "",
        "The history sets each auction's baseline level, so the rows below and the "
        "dollar and MW deltas depend on it. The percentage shift does not: it is the "
        "same on any history. The response does not depend on `reserve_margin_pct`; "
        "that column is shown for context. The elasticities are not estimated from "
        "these auctions.",
        "",
        "## per auction",
        "",
        "| auction year | lda | reserve margin % | baseline price | counterfactual price | baseline MW | counterfactual MW |",
        "|---:|---|---:|---:|---:|---:|---:|",
        *[
            f"| {row['auction_year']} | {row['lda']} | {row['reserve_margin_pct']:.1f} "
            f"| {row['baseline_price_usd_mw_day']:.2f} | {row['counterfactual_price_usd_mw_day']:.2f} "
            f"| {row['baseline_cleared_mw']:,.0f} | {row['counterfactual_cleared_mw']:,.0f} |"
            for row in result.per_auction
        ],
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
            "The v0.1 screen applies the rule's reserve-margin delta through fixed elasticities to each auction in the checked-in PJM RPM fixture. It does not estimate a response from the history, clear a market, or run trials. It is a deterministic counterfactual screen, not a forecast.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


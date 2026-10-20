from __future__ import annotations

import hashlib
import json

from .models import AuctionRow, ReplayResult, RuleSpec
from .translator import translate

ELASTICITY_KEYS = (
    "price_elasticity_per_margin_point",
    "cleared_mw_elasticity_per_margin_point",
)


def mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 3)


def _elasticity_source(rule: RuleSpec) -> str:
    overridden = [key for key in ELASTICITY_KEYS if key in rule.parameter_overrides]
    if overridden:
        return "rule parameter_overrides"
    return "translator BASELINE default; assumed, not sourced to a filing"


def replay(rule: RuleSpec, history: list[AuctionRow], history_ref: str, seed: int) -> ReplayResult:
    """Apply a fixed-elasticity response to each historical auction.

    The model is a fixed elasticity: every auction's clearing price is scaled by
    1 + margin_delta * price_elasticity and its cleared MW by
    1 + margin_delta * cleared_mw_elasticity. History sets each auction's
    baseline level, so the per-auction rows and absolute deltas depend on it.
    The relative shift does not: it is margin_delta * elasticity on any
    history. reserve_margin_pct is carried into the per-auction rows as
    context; the response does not depend on it.
    """

    params = translate(rule)
    margin_delta = params["reserve_margin_delta_pct"]
    price_elasticity = params["price_elasticity_per_margin_point"]
    mw_elasticity = params["cleared_mw_elasticity_per_margin_point"]
    price_multiplier = 1 + margin_delta * price_elasticity
    mw_multiplier = 1 + margin_delta * mw_elasticity

    per_auction = []
    for row in history:
        counter_price = round(row.clearing_price_usd_mw_day * price_multiplier, 3)
        counter_mw = round(row.cleared_mw * mw_multiplier, 3)
        per_auction.append(
            {
                "auction_year": row.auction_year,
                "lda": row.lda,
                "reserve_margin_pct": row.reserve_margin_pct,
                "baseline_price_usd_mw_day": row.clearing_price_usd_mw_day,
                "counterfactual_price_usd_mw_day": counter_price,
                "price_delta_usd_mw_day": round(counter_price - row.clearing_price_usd_mw_day, 3),
                "baseline_cleared_mw": row.cleared_mw,
                "counterfactual_cleared_mw": counter_mw,
                "cleared_mw_delta": round(counter_mw - row.cleared_mw, 3),
            }
        )

    baseline_prices = [row["baseline_price_usd_mw_day"] for row in per_auction]
    baseline_mw = [row["baseline_cleared_mw"] for row in per_auction]
    counter_prices = [row["counterfactual_price_usd_mw_day"] for row in per_auction]
    counter_mw = [row["counterfactual_cleared_mw"] for row in per_auction]
    payload = {
        "rule": rule.rule_id,
        "history_ref": history_ref,
        "seed": seed,
        "margin_delta": margin_delta,
    }
    replay_id = "pr-" + hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]
    return ReplayResult(
        replay_id=replay_id,
        rule_id=rule.rule_id,
        history_snapshot_ref=history_ref,
        trial_count=1,
        seed=seed,
        baseline_outcomes={
            "mean_price_usd_mw_day": mean(baseline_prices),
            "mean_cleared_mw": mean(baseline_mw),
        },
        counterfactual_outcomes={
            "mean_price_usd_mw_day": mean(counter_prices),
            "mean_cleared_mw": mean(counter_mw),
        },
        outcome_delta_summary={
            "mean_price_delta_usd_mw_day": round(mean(counter_prices) - mean(baseline_prices), 3),
            "mean_cleared_mw_delta": round(mean(counter_mw) - mean(baseline_mw), 3),
            "reserve_margin_delta_pct": margin_delta,
        },
        model={
            "kind": "fixed_elasticity",
            "price_elasticity_per_margin_point": price_elasticity,
            "cleared_mw_elasticity_per_margin_point": mw_elasticity,
            "elasticity_source": _elasticity_source(rule),
            "price_shift_pct": round(margin_delta * price_elasticity * 100, 3),
            "cleared_mw_shift_pct": round(margin_delta * mw_elasticity * 100, 3),
            "history_rows": len(history),
            "history_sets": "each auction's baseline level; the relative shift is the same on any history",
        },
        per_auction=per_auction,
    )

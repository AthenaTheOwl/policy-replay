from __future__ import annotations

import hashlib
import json

from .models import AuctionRow, ReplayResult, RuleSpec
from .translator import translate


def mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 3)


def replay(rule: RuleSpec, history: list[AuctionRow], history_ref: str, seed: int) -> ReplayResult:
    params = translate(rule)
    margin_delta = params["reserve_margin_delta_pct"]
    price_multiplier = 1 + margin_delta * params["price_elasticity_per_margin_point"]
    mw_multiplier = 1 + margin_delta * params["cleared_mw_elasticity_per_margin_point"]
    baseline_prices = [row.clearing_price_usd_mw_day for row in history]
    baseline_mw = [row.cleared_mw for row in history]
    counter_prices = [round(value * price_multiplier, 3) for value in baseline_prices]
    counter_mw = [round(value * mw_multiplier, 3) for value in baseline_mw]
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
    )


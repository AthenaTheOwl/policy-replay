from __future__ import annotations

from .models import RuleSpec

BASELINE = {
    "reserve_margin_delta_pct": 0.0,
    "price_elasticity_per_margin_point": 0.035,
    "cleared_mw_elasticity_per_margin_point": -0.012,
}


def translate(rule: RuleSpec, baseline: dict[str, float] | None = None) -> dict[str, float]:
    params = dict(BASELINE if baseline is None else baseline)
    params.update(rule.parameter_overrides)
    return params


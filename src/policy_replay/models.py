from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class RuleSpec:
    rule_id: str
    name: str
    proposing_body: str
    proposal_date: str
    effective_target_date: str
    affected_markets: list[str]
    parameter_overrides: dict[str, float]
    references: list[str]


@dataclass(frozen=True)
class AuctionRow:
    auction_year: int
    lda: str
    clearing_price_usd_mw_day: float
    cleared_mw: float
    reserve_margin_pct: float


@dataclass(frozen=True)
class ReplayResult:
    replay_id: str
    rule_id: str
    history_snapshot_ref: str
    trial_count: int
    seed: int
    baseline_outcomes: dict[str, Any]
    counterfactual_outcomes: dict[str, Any]
    outcome_delta_summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


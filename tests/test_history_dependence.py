"""The replay reads each auction in the history; the relative shift is a fixed elasticity."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.policy_replay.loader import load_history, load_rule
from src.policy_replay.models import AuctionRow, RuleSpec
from src.policy_replay.sim import replay

ROOT = Path(__file__).resolve().parents[1]
RULE = ROOT / "rules" / "pjm-dec2025-capacity-reform.json"
HISTORY = ROOT / "data" / "history" / "pjm_rpm_2018_2023.csv"

OTHER_HISTORY = [
    AuctionRow(2018, "RTO", 999.0, 10.0, 1.0),
    AuctionRow(2019, "RTO", 1.0, 99999.0, 40.0),
]


def _replay(history: list[AuctionRow], rule: RuleSpec | None = None):
    return replay(rule or load_rule(RULE), history, "history-under-test", 1)


def test_different_histories_change_the_output() -> None:
    fixture = _replay(load_history(HISTORY))
    other = _replay(OTHER_HISTORY)

    assert fixture.per_auction != other.per_auction
    assert [row["auction_year"] for row in other.per_auction] == [2018, 2019]
    assert other.per_auction[0]["counterfactual_price_usd_mw_day"] == pytest.approx(999.0 * 1.0525)
    assert fixture.baseline_outcomes != other.baseline_outcomes
    assert (
        fixture.outcome_delta_summary["mean_price_delta_usd_mw_day"]
        != other.outcome_delta_summary["mean_price_delta_usd_mw_day"]
    )
    assert fixture.model["history_rows"] == 6
    assert other.model["history_rows"] == 2


def test_per_auction_rows_follow_the_history_file() -> None:
    history = load_history(HISTORY)
    result = _replay(history)
    assert [(row["auction_year"], row["reserve_margin_pct"]) for row in result.per_auction] == [
        (row.auction_year, row.reserve_margin_pct) for row in history
    ]
    for row, source in zip(result.per_auction, history):
        assert row["baseline_price_usd_mw_day"] == source.clearing_price_usd_mw_day
        assert row["baseline_cleared_mw"] == source.cleared_mw


def test_relative_shift_is_the_assumed_elasticity_on_any_history() -> None:
    # The screen is a fixed elasticity. This pins that the percentage shift is
    # margin_delta x elasticity whatever the history, so no report can present
    # it as something the auctions produced.
    for history in (load_history(HISTORY), OTHER_HISTORY):
        result = _replay(history)
        assert result.model["kind"] == "fixed_elasticity"
        assert result.model["price_shift_pct"] == 5.25
        assert result.model["cleared_mw_shift_pct"] == -1.8
        assert "not sourced" in result.model["elasticity_source"]
        for row in result.per_auction:
            assert row["counterfactual_price_usd_mw_day"] == pytest.approx(
                row["baseline_price_usd_mw_day"] * 1.0525, abs=1e-3
            )


def test_rule_elasticity_override_is_reported_as_the_source() -> None:
    base = load_rule(RULE)
    rule = RuleSpec(
        **{
            **base.__dict__,
            "parameter_overrides": {
                "reserve_margin_delta_pct": 1.5,
                "price_elasticity_per_margin_point": 0.01,
            },
        }
    )
    result = _replay(load_history(HISTORY), rule)
    assert result.model["elasticity_source"] == "rule parameter_overrides"
    assert result.model["price_shift_pct"] == 1.5


def test_committed_report_states_the_model_plainly() -> None:
    text = (ROOT / "reports" / "pjm-dec2025-replay" / "report.md").read_text(encoding="utf-8")
    assert "fixed-elasticity screen" in text
    assert "## per auction" in text
    assert "| 2023 | RTO | 13.9 | 28.92 | 30.44 |" in text

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.policy_replay.loader import load_history, load_rule
from src.policy_replay.sim import mean, replay
from src.policy_replay.translator import translate
from src.policy_replay.validation import validate_result

ROOT = Path(__file__).resolve().parents[1]
RULE = ROOT / "rules" / "pjm-dec2025-capacity-reform.json"
HISTORY = ROOT / "data" / "history" / "pjm_rpm_2018_2023.csv"


def test_rule_loader_and_translator() -> None:
    rule = load_rule(RULE)
    params = translate(rule)
    assert params["reserve_margin_delta_pct"] == 1.5
    assert len(rule.references) == 2


def test_replay_is_deterministic() -> None:
    rule = load_rule(RULE)
    history = load_history(HISTORY)
    one = replay(rule, history, "data/history/pjm_rpm_2018_2023.csv", 7).to_dict()
    two = replay(rule, history, "data/history/pjm_rpm_2018_2023.csv", 7).to_dict()
    assert one == two


def test_cli_writes_result_and_report() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "policy_replay",
            "simulate",
            "--rule",
            "rules/pjm-dec2025-capacity-reform.json",
            "--history",
            "data/history/pjm_rpm_2018_2023.csv",
            "--out",
            "reports/pjm-dec2025-replay",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert (ROOT / payload["report_path"]).is_file()
    validate_result(ROOT / payload["result_path"])


def test_replay_has_nonzero_delta() -> None:
    data = json.loads((ROOT / "reports" / "pjm-dec2025-replay" / "replay_result.json").read_text())
    assert data["outcome_delta_summary"]["mean_price_delta_usd_mw_day"] > 0


def test_replay_pins_current_counterfactual_numbers() -> None:
    # golden-master lock on the translator elasticities and the sim rounding.
    # these literals are what replay() produces today at reserve_margin_delta_pct=1.5;
    # any change to the 0.035 / -0.012 elasticities or the 3-decimal rounding flips them.
    rule = load_rule(RULE)
    history = load_history(HISTORY)
    result = replay(rule, history, "data/history/pjm_rpm_2018_2023.csv", 20260620)

    assert result.baseline_outcomes["mean_price_usd_mw_day"] == 83.842
    assert result.baseline_outcomes["mean_cleared_mw"] == 148683.333

    # price elasticity 0.035: scaling it away moves this off 88.243
    assert result.counterfactual_outcomes["mean_price_usd_mw_day"] == 88.243
    assert result.outcome_delta_summary["mean_price_delta_usd_mw_day"] == 4.401

    # cleared-MW elasticity -0.012: pins magnitude, not just sign
    assert result.counterfactual_outcomes["mean_cleared_mw"] == 146007.033
    assert result.outcome_delta_summary["mean_cleared_mw_delta"] == -2676.3


def test_mean_keeps_three_decimals() -> None:
    # if mean() ever drops to round(..., 0) these fractional digits vanish
    assert mean([83.8415, 148683.3333]) == 74383.587
    assert mean([148683.3333, 148683.3333]) == 148683.333


def test_load_rule_rejects_under_referenced_rule(tmp_path: Path) -> None:
    rule = {
        "rule_id": "x",
        "name": "x",
        "proposing_body": "x",
        "proposal_date": "2026-01-01",
        "effective_target_date": "2026-06-01",
        "affected_markets": ["pjm.rpm"],
        "parameter_overrides": {"reserve_margin_delta_pct": 1.0},
        "references": ["https://example.com/only-one"],
    }
    path = tmp_path / "rule.json"
    path.write_text(json.dumps(rule), encoding="utf-8")
    with pytest.raises(ValueError, match="fewer than two references"):
        load_rule(path)


def test_validate_result_rejects_multi_trial(tmp_path: Path) -> None:
    result = {
        "trial_count": 2,
        "seed": 1,
        "baseline_outcomes": {"mean_price_usd_mw_day": 1.0},
        "counterfactual_outcomes": {"mean_price_usd_mw_day": 1.0},
        "outcome_delta_summary": {"mean_price_delta_usd_mw_day": 0.0},
    }
    path = tmp_path / "replay_result.json"
    path.write_text(json.dumps(result), encoding="utf-8")
    with pytest.raises(ValueError, match="trial_count=1"):
        validate_result(path)


def test_show_verb_prints_readable_ranked_result() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "policy_replay", "show"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    out = result.stdout
    # headline finding + ranked table + the rule id are all present
    assert "headline:" in out
    assert "baseline" in out and "counterfactual" in out
    assert "pjm-dec2025-capacity-reform" in out
    # the bigger relative shift (price, +5.2%) is ranked above the smaller (cleared MW)
    assert out.index("clearing price") < out.index("cleared capacity")


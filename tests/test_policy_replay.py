from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.policy_replay.loader import load_history, load_rule
from src.policy_replay.sim import replay
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


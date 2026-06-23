"""policy-replay — live demo (Streamlit Community Cloud).

Reads the committed replay result under reports/*/replay_result.json and shows
the counterfactual outcome screen for a proposed power-market rule change:
baseline PJM RPM auction outcomes versus the counterfactual under the rule's
reserve-margin override. No network, no secrets — runs entirely off the
committed fixture.

Deploy: Streamlit Community Cloud -> New app -> repo AthenaTheOwl/policy-replay,
branch main, main file streamlit_app.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

REPO = Path(__file__).resolve().parent
REPORTS = REPO / "reports"


def load_result() -> tuple[dict | None, str]:
    files = sorted(REPORTS.glob("*/replay_result.json"))
    if not files:
        return None, ""
    latest = files[-1]
    return json.loads(latest.read_text(encoding="utf-8")), latest.parent.name


st.set_page_config(page_title="policy-replay — counterfactual outcome screen", layout="wide")
st.title("policy-replay")
st.caption(
    "replay a proposed power-market rule change against historical PJM RPM auction "
    "outcomes — baseline versus counterfactual, before the rule goes effective."
)

result, report_name = load_result()
if result is None:
    st.warning("no replay result found under reports/*/replay_result.json — run `python -m policy_replay simulate` first")
    st.stop()

base = result["baseline_outcomes"]
counter = result["counterfactual_outcomes"]
delta = result["outcome_delta_summary"]
margin = delta["reserve_margin_delta_pct"]

st.subheader(f"{result['rule_id']} — {report_name}")
st.write(
    f"replay `{result['replay_id']}` · history `{result['history_snapshot_ref']}` · seed `{result['seed']}`"
)

c1, c2, c3 = st.columns(3)
c1.metric(
    "clearing price",
    f"${counter['mean_price_usd_mw_day']:,.2f}",
    f"{delta['mean_price_delta_usd_mw_day']:+,.2f} USD/MW-day",
)
c2.metric(
    "cleared capacity",
    f"{counter['mean_cleared_mw']:,.0f} MW",
    f"{delta['mean_cleared_mw_delta']:+,.0f} MW",
)
c3.metric(
    "reserve-margin override",
    f"{margin:+.1f} pts",
    help="the rule parameter the screen applies to the historical record",
)

metrics = [
    {
        "metric": "clearing price (USD/MW-day)",
        "baseline": base["mean_price_usd_mw_day"],
        "counterfactual": counter["mean_price_usd_mw_day"],
        "delta": delta["mean_price_delta_usd_mw_day"],
        "shift %": round(delta["mean_price_delta_usd_mw_day"] / base["mean_price_usd_mw_day"] * 100, 1),
    },
    {
        "metric": "cleared capacity (MW)",
        "baseline": base["mean_cleared_mw"],
        "counterfactual": counter["mean_cleared_mw"],
        "delta": delta["mean_cleared_mw_delta"],
        "shift %": round(delta["mean_cleared_mw_delta"] / base["mean_cleared_mw"] * 100, 1),
    },
]

rank_by = st.radio(
    "rank metrics by",
    ["relative shift %", "absolute delta"],
    horizontal=True,
)
key = (lambda m: abs(m["shift %"])) if rank_by == "relative shift %" else (lambda m: abs(m["delta"]))
ranked = sorted(metrics, key=key, reverse=True)

st.dataframe(ranked, use_container_width=True, hide_index=True)

top = ranked[0]
direction = "up" if top["delta"] > 0 else "down"
st.info(
    f"**headline:** under the {margin:+.1f}-pt reserve-margin change, "
    f"{top['metric'].split(' (')[0]} moves {direction} {abs(top['shift %']):.1f}% "
    f"({top['baseline']:,.2f} -> {top['counterfactual']:,.2f}). "
    f"this is a deterministic counterfactual screen on a committed fixture, not a probabilistic forecast."
)

st.caption(
    "v0.1 ships one PJM RPM fixture and one rule. the model + replay live in "
    "`src/policy_replay/`; this page reads the committed `reports/*/replay_result.json`. "
    "repo: github.com/AthenaTheOwl/policy-replay"
)

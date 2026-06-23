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

# ---------------------------------------------------------------------------
# Run the real replay engine live. This is not a viewer — the controls below
# call policy_replay.sim.replay (via translate), the same function that produced
# the committed result. Set the rule's reserve-margin override, edit the auction
# history, and watch the counterfactual recompute.
# ---------------------------------------------------------------------------
st.divider()
st.subheader("replay your own rule")
st.caption(
    "drive the actual replay engine — `policy_replay.sim.replay` — with your own rule override "
    "and auction history. pre-filled with the committed PJM RPM fixture."
)

try:
    import csv
    import io
    import sys

    sys.path.insert(0, str(REPO / "src"))
    from policy_replay.models import AuctionRow, RuleSpec
    from policy_replay.sim import replay
    from policy_replay.translator import BASELINE

    col_a, col_b = st.columns(2)
    with col_a:
        margin = st.slider(
            "reserve-margin override (pts)",
            -5.0, 5.0,
            float(result["outcome_delta_summary"]["reserve_margin_delta_pct"]),
            step=0.1,
            help="the rule parameter applied to the historical auction record",
        )
        seed = st.number_input("seed", min_value=0, value=int(result["seed"]), step=1)
    with col_b:
        price_elast = st.slider(
            "price elasticity per margin point",
            -0.10, 0.10, float(BASELINE["price_elasticity_per_margin_point"]), step=0.005,
            help="how clearing price responds to a 1-pt reserve-margin change",
        )
        mw_elast = st.slider(
            "cleared-MW elasticity per margin point",
            -0.10, 0.10, float(BASELINE["cleared_mw_elasticity_per_margin_point"]), step=0.005,
            help="how cleared capacity responds to a 1-pt reserve-margin change",
        )

    default_csv = (
        "auction_year,lda,clearing_price_usd_mw_day,cleared_mw,reserve_margin_pct\n"
        "2018,RTO,140.00,154000,16.2\n"
        "2019,RTO,110.00,151500,15.8\n"
        "2020,RTO,50.00,148200,14.9\n"
        "2021,RTO,140.00,150300,15.6\n"
        "2022,RTO,34.13,144900,14.3\n"
        "2023,RTO,28.92,143200,13.9\n"
    )
    history_text = st.text_area(
        "auction history (CSV) — edit prices, capacities, add rows",
        value=default_csv,
        height=180,
    )

    history = []
    for row in csv.DictReader(io.StringIO(history_text)):
        history.append(
            AuctionRow(
                auction_year=int(row["auction_year"]),
                lda=row["lda"],
                clearing_price_usd_mw_day=float(row["clearing_price_usd_mw_day"]),
                cleared_mw=float(row["cleared_mw"]),
                reserve_margin_pct=float(row["reserve_margin_pct"]),
            )
        )
    if not history:
        raise ValueError("history has no rows")

    rule = RuleSpec(
        rule_id="user-rule",
        name="your rule",
        proposing_body="you",
        proposal_date="2026-06",
        effective_target_date="2026-06",
        affected_markets=["pjm.rpm"],
        parameter_overrides={
            "reserve_margin_delta_pct": margin,
            "price_elasticity_per_margin_point": price_elast,
            "cleared_mw_elasticity_per_margin_point": mw_elast,
        },
        references=["https://example/a", "https://example/b"],
    )

    live = replay(rule, history, "user-input", int(seed))
    lbase = live.baseline_outcomes
    lcounter = live.counterfactual_outcomes
    ldelta = live.outcome_delta_summary

    m1, m2, m3 = st.columns(3)
    m1.metric(
        "clearing price",
        f"${lcounter['mean_price_usd_mw_day']:,.2f}",
        f"{ldelta['mean_price_delta_usd_mw_day']:+,.2f} USD/MW-day",
    )
    m2.metric(
        "cleared capacity",
        f"{lcounter['mean_cleared_mw']:,.0f} MW",
        f"{ldelta['mean_cleared_mw_delta']:+,.0f} MW",
    )
    m3.metric("replay id", live.replay_id)

    live_rows = [
        {
            "metric": "clearing price (USD/MW-day)",
            "baseline": lbase["mean_price_usd_mw_day"],
            "counterfactual": lcounter["mean_price_usd_mw_day"],
            "delta": ldelta["mean_price_delta_usd_mw_day"],
        },
        {
            "metric": "cleared capacity (MW)",
            "baseline": lbase["mean_cleared_mw"],
            "counterfactual": lcounter["mean_cleared_mw"],
            "delta": ldelta["mean_cleared_mw_delta"],
        },
    ]
    st.dataframe(live_rows, use_container_width=True, hide_index=True)
    st.caption(
        "move the override, retune the elasticities, or edit the CSV and the counterfactual "
        "recomputes — it's the live `replay()` engine, not a lookup. the replay id is the real "
        "deterministic hash over your rule + history + seed."
    )
except Exception as exc:  # pragma: no cover - defensive for cloud import differences
    st.info(f"interactive replay needs the package importable ({exc}). the committed result above still renders.")

st.caption(
    "v0.1 ships one PJM RPM fixture and one rule. the model + replay live in "
    "`src/policy_replay/`; this page reads the committed `reports/*/replay_result.json` "
    "and the replay section above is the real engine. "
    "repo: github.com/AthenaTheOwl/policy-replay"
)

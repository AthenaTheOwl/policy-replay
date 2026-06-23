# PolicyReplay

Test harness for power-market rule changes before they pass. Takes a
proposed FERC, ISO, or state-PUC rule change (interconnection-process
reform, capacity-market clearing, data-center cost allocation) and
runs it against historical queue and auction data to forecast the
outcome distribution before the rule goes effective.

## What this is

FERC Order 2023 implementation is messy. PJM rule changes are
happening at a pace nobody can model. State PUCs are improvising on
data-center cost allocation. Nobody has a clean test harness that
takes a rule-change proposal and replays it against the historical
record.

PolicyReplay is that harness. The first artifact is a worked example:
simulate PJM's proposed Dec 2025 capacity-market reform against the
actual auction outcomes, publish the methodology and replication code.

The math layer borrows from InterconnectAlpha and from
robust-optimization. The regulatory-text RAG borrows from
supplier-risk-rag-agent. The historical-record layer borrows from
GridSilicon and the LBNL Queued Up data.

Buyers: FERC and ISO planning staff, state PUC commissioners,
ratepayer advocates, IPP developers, utility resource-planning groups,
energy lawyers.

## Status


v0.1 shipped — runnable, minimal. The first real deliverable is in place; the next passes deepen it (more scenarios, real-data backfill). The entry command `python -m policy_replay simulate` runs. See `specs/0002-design/` for the v0.1 scope and `STATUS.md` (where present) for the current state and next-feature queue.

## How to run

Run the worked example (writes `reports/pjm-dec2025-replay/`):

```bash
python -m policy_replay simulate \
  --rule rules/pjm-dec2025-capacity-reform.json \
  --history data/history/pjm_rpm_2018_2023.csv \
  --out reports/pjm-dec2025-replay
```

Then read the committed result as a ranked, readable screen (no args, offline):

```bash
python -m policy_replay show
```

```
policy-replay - counterfactual outcome screen (pjm-dec2025-capacity-reform)
metric                               baseline   counterfactual        delta     shift
-------------------------------------------------------------------------------------
clearing price (USD/MW-day)             83.84            88.24        +4.40     +5.2%
cleared capacity (MW)              148,683.33       146,007.03    -2,676.30     -1.8%
reserve margin (pts)                                                  +1.50

headline: under the +1.5-pt reserve-margin change, clearing price moves up 5.2% ...
```

## live demo

A Streamlit page (`streamlit_app.py`) renders the same counterfactual screen
interactively — three metrics, a ranked baseline-vs-counterfactual table, and the
headline finding. It reads the committed `reports/*/replay_result.json` directly;
no network, no secrets.

Run locally:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Deploy on Streamlit Community Cloud: New app -> repo `AthenaTheOwl/policy-replay`,
branch `main`, main file `streamlit_app.py`.

<!-- live url: (paste Streamlit Community Cloud URL here once deployed) -->

## Layout

```
policy-replay/
  README.md
  LICENSE
  AGENTS.md
  .gitignore
  specs/
    0001-foundation/
      requirements.md          # R-PR-NNN
      design.md
      tasks.md
      acceptance.md
  docs/
    first-pr.md
```

Downstream additions:

```
  src/policy_replay/
    rule/loader.py
    rule/translator.py            # rule YAML -> simulation parameters
    history/pjm_rpm.py
    history/pjm_queue.py
    history/miso.py
    history/ercot.py
    sim/replay.py                 # replays history under modified rule
    sim/counterfactual.py
    report/render.py
  schemas/
    rule.schema.json
    history_snapshot.schema.json
    replay_result.schema.json
  rules/
    pjm-dec2025-capacity-reform.yaml
    ferc-order-2023-interconnection-reform.yaml
    nj-bpu-datacenter-cost-allocation-draft.yaml
  data/
    pjm_rpm_2018_2023.parquet
    pjm_queue_2018_2023.parquet
  reports/
    pjm-dec2025-replay/
  eval/
    calibration_against_past_changes.py    # MOPR, MISO Tariff changes
    sanity_bounds.py
```

## License

MIT. See [LICENSE](LICENSE).

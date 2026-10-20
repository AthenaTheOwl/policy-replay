# policy-replay

PJM's proposed +1.5-point reserve-margin change isn't effective yet. Apply it to six cleared RPM auctions from 2018 to 2023 at an assumed price elasticity of 3.5% per margin point and the mean clearing price moves from 83.84 to 88.24 dollars per MW-day, +5.2%, while cleared capacity falls 2,676 MW. The +5.2% is 1.5 x 3.5%. It comes from the elasticity, not from the auctions, and it is the same on any history.

## What it does

A power-market rule change arrives as a proposal: a FERC order, an ISO tariff filing, a state PUC draft on data-center cost allocation. Months pass before it takes effect, and longer before anyone can say what it did.

policy-replay takes a rule encoded as a small JSON file, translates it into numeric parameters, and applies them to each auction in a historical fixture. v0.1 ships one worked example: PJM's December 2025 capacity-market reserve-margin proposal against a six-row PJM RPM fixture covering 2018 to 2023. The fixture CSV does not cite a source for its rows.

The v0.1 model is a fixed elasticity. Each auction's clearing price is scaled by `1 + margin_delta x price_elasticity` and its cleared MW by `1 + margin_delta x cleared_mw_elasticity`. The defaults, 0.035 and -0.012 per margin point, live in `src/policy_replay/translator.py`; they are assumptions, not values from a cited filing, and a rule file can override them. The history sets each auction's baseline level, so the per-auction rows and the dollar and MW deltas depend on it. The percentage shift does not, the response ignores the fixture's `reserve_margin_pct` column, and nothing is estimated from the auctions, cleared through a demand curve, or sampled. `replay_result.json` records this under `model`, including where the elasticities came from. The screen is deterministic. It is a screen, not a forecast, and it says so on the last line.

## Try it

Run the worked example. It writes the replay artifact to `reports/pjm-dec2025-replay/`:

```bash
python -m policy_replay simulate \
  --rule rules/pjm-dec2025-capacity-reform.json \
  --history data/history/pjm_rpm_2018_2023.csv \
  --out reports/pjm-dec2025-replay
```

Then read the committed result as a ranked, readable screen — no args, offline:

```bash
python -m policy_replay show
```

```
policy-replay - counterfactual outcome screen (pjm-dec2025-capacity-reform)
replay pr-8fce0cd16b4f  |  history data/history/pjm_rpm_2018_2023.csv  |  seed 20260620
ranked by relative shift under the proposed rule (baseline -> counterfactual)

metric                               baseline   counterfactual        delta     shift
-------------------------------------------------------------------------------------
clearing price (USD/MW-day)             83.84            88.24        +4.40     +5.2%
cleared capacity (MW)              148,683.33       146,007.03    -2,676.30     -1.8%
reserve margin (pts)                                                  +1.50          

per auction (6 rows from the history file):
year   lda     margin %      price      -> cf   cleared MW        -> cf
2018   RTO         16.2     140.00     147.35      154,000      151,228
2019   RTO         15.8     110.00     115.78      151,500      148,773
2020   RTO         14.9      50.00      52.62      148,200      145,532
2021   RTO         15.6     140.00     147.35      150,300      147,595
2022   RTO         14.3      34.13      35.92      144,900      142,292
2023   RTO         13.9      28.92      30.44      143,200      140,622

model: fixed elasticity. price +0.035 and cleared MW -0.012 per margin point (translator BASELINE default; assumed, not sourced to a filing).
every auction shifts +5.25% in price and -1.80% in cleared MW on any history; the history sets the levels, not the shift. reserve margin is shown, not used.

headline: under the +1.5-pt reserve-margin change, clearing price moves up 5.2% (83.84 -> 88.24). fixed-elasticity screen, not a forecast.
```

Ranked by relative shift, the largest mover first. The reserve-margin row is the knob you turned. The price and capacity rows are that knob times the assumed elasticities, applied to each auction in the per-auction table.

Use the [assumption-change review](docs/assumption-change-review.md) when a filing,
rule translation or historical snapshot changes. It separates parameter and data
effects, asks you to preserve earlier results (use a new `--out` directory), and
defines falsification evidence before a counterfactual comparison is accepted.

## Live demo

A Streamlit page (`streamlit_app.py`) renders the same counterfactual screen interactively — three metrics, a ranked baseline-vs-counterfactual table, and the headline finding. It reads the committed `reports/*/replay_result.json` directly; no network, no secrets.

Run locally:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Deploy on Streamlit Community Cloud: New app -> repo `AthenaTheOwl/policy-replay`,
branch `main`, main file `streamlit_app.py`.

<!-- live url: (paste Streamlit Community Cloud URL here once deployed) -->

## How it connects

policy-replay sits on top of the same project graph as the energy repos and reuses their layers:

- [interconnect-alpha](https://github.com/AthenaTheOwl/interconnect-alpha) — the survival model for queued projects; the math that scores whether a rule change moves the queue.
- [grid-silicon](https://github.com/AthenaTheOwl/grid-silicon) — the historical-record floor: scored large-load projects and the queue data the replay reads against.
- [supplier-risk-rag-agent](https://github.com/AthenaTheOwl/supplier-risk-rag-agent) — the regulatory-text retrieval that turns a filing's prose into the parameters a rule file needs.

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
    assumption-change-review.md
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

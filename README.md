# policy-replay

PJM's proposed +1.5-point reserve-margin change isn't effective yet. Run it against six years of cleared RPM auctions and the screen says the clearing price moves up 5.2% — 83.84 to 88.24 dollars per MW-day — while cleared capacity falls 2,676 MW. The rule hasn't passed. The number already exists.

## What it does

A power-market rule change arrives as a proposal: a FERC order, an ISO tariff filing, a state PUC draft on data-center cost allocation. Months pass before it takes effect, and longer before anyone can say what it did. The historical record that would answer the question — what this rule would have done to past auctions — sits in one place. The proposal sits in another. Nobody has put them in the same room.

policy-replay puts them there. It takes a rule encoded as a small JSON file, replays it against historical queue and auction data, and prints a counterfactual screen: each metric, baseline versus what the rule would have produced, ranked by how far it moves. v0.1 ships one worked example — PJM's December 2025 capacity-market reserve-margin proposal, replayed against PJM RPM auctions from 2018 to 2023. The screen is deterministic and seeded. It is a screen, not a forecast, and it says so on the last line.

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

headline: under the +1.5-pt reserve-margin change, clearing price moves up 5.2% (83.84 -> 88.24). deterministic screen, not a forecast.
```

Ranked by relative shift, the largest mover first. The reserve-margin row is the knob you turned; the price and capacity rows are what moved when you turned it.

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

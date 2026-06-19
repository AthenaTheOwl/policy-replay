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

v0 scaffold. No implementation. The repo holds the README, the
license, the agents contract, the foundation spec, and the literal
first PR plan. The first runnable PR after this scaffold lands the
rule-spec schema and the historical-record loader against a small
PJM 2018-2023 fixture.

## How to run

Placeholder. After implementation lands:

```bash
uv run policy-replay simulate \
  --rule rules/pjm-dec2025-capacity-reform.yaml \
  --history data/pjm_rpm_2018_2023.parquet \
  --queue data/pjm_queue_2018_2023.parquet \
  --trials 1000 \
  --out reports/pjm-dec2025-replay/
```

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

# AGENTS.md — policy-replay

Operating contract for AI agents (Claude, Codex, Cursor) working in
this repo. Same conventions as the rest of the AthenaTheOwl
portfolio. An agent trained on InterconnectAlpha or GridSilicon will
recognize the data shape.

## What this repo is

A counterfactual screen for power-market rule changes. Input: a rule
spec plus a historical-record snapshot. Output: one deterministic
result per auction and in aggregate, baseline versus the rule applied
through fixed elasticities (`src/policy_replay/translator.py`). The
percentage shift is margin delta x elasticity on any history; the
history sets the levels. There is no clearing model, no Monte Carlo
distribution, and no calibration against past rule changes yet.

## Roles you may see in tasks

| Role | What they do |
|---|---|
| `rule-curator` | Authors and maintains JSON rule specs in `rules/`, with citations to the FERC / ISO / PUC source documents |
| `history-loader` | Per-ISO adapter (PJM RPM, PJM Queue, MISO, ERCOT) that reads historical snapshots |
| `translator` | Converts a rule spec into a set of simulation parameter overrides |
| `replay-runner` | Replays the historical record under the modified rule; produces counterfactual outcomes |
| `calibrator` | Backtests the harness against rule changes that already happened |
| `report-renderer` | Publishes the replay report |

## Voice constraints

- Plain assertions. No marketing words. This repo has no voice-lint
  script yet; review prose by hand.
- No antithetical reversals as a structural device.
- No policy advocacy in reports. The format is descriptive
  counterfactual, not "FERC should adopt X".
- Every assumption in a rule translation cites the source filing. The
  translator's default elasticities do not yet; every replay result
  marks them as assumed under `model.elasticity_source`.

## Gates

These are the gates `.github/workflows/ci.yml` runs:

```bash
uv run --with pytest pytest -q
uv run python scripts/validate_schemas.py
uv run python eval/sanity_bounds.py
uv run python scripts/validate_data_conformance.py
```

A calibration gate against past rule changes (MOPR, MISO tariff
changes) is planned in spec 0001 but not built; there is no
`eval/calibration_against_past_changes.py` yet.

## Out of scope

- Real-time market operations (no live LMP feeds).
- Equity / generation-asset valuation outputs.
- Predictions about which rule changes will be adopted.
- Customer-confidential utility data.
- Policy recommendations.

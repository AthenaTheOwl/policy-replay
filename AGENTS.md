# AGENTS.md — policy-replay

Operating contract for AI agents (Claude, Codex, Cursor) working in
this repo. Same conventions as the rest of the AthenaTheOwl
portfolio. An agent trained on InterconnectAlpha or GridSilicon will
recognize the data shape.

## What this repo is

A simulation harness for power-market rule changes. Input: a rule
spec plus a historical-record snapshot. Output: a distribution over
what the historical outcomes would have been under the modified rule,
plus a calibration trace against rule changes that have actually
taken effect (MOPR, MISO Tariff changes, etc.).

The novelty is the rule-to-simulation-spec translator and the
calibration discipline. The simulator itself is a fairly standard
RPM-style clearing model.

## Roles you may see in tasks

| Role | What they do |
|---|---|
| `rule-curator` | Authors and maintains YAML rule specs in `rules/`, with citations to the FERC / ISO / PUC source documents |
| `history-loader` | Per-ISO adapter (PJM RPM, PJM Queue, MISO, ERCOT) that reads historical snapshots |
| `translator` | Converts a rule spec into a set of simulation parameter overrides |
| `replay-runner` | Replays the historical record under the modified rule; produces counterfactual outcomes |
| `calibrator` | Backtests the harness against rule changes that already happened |
| `report-renderer` | Publishes the replay report |

## Voice constraints

- Plain assertions. No marketing words. Banned set in
  `scripts/voice_lint.py::BANNED_FAIL` (spec 0002).
- No antithetical reversals as a structural device.
- No policy advocacy in reports. The format is descriptive
  counterfactual, not "FERC should adopt X".
- Every assumption in a rule translation cites the source filing.

## Gates (will land in spec 0002)

```bash
uv run pytest
python scripts/voice_lint.py
python scripts/validate_schemas.py
python eval/sanity_bounds.py
python eval/calibration_against_past_changes.py
```

The calibration gate fails when the harness's predicted post-rule
outcomes on a past rule change miss the actual post-rule outcomes by
more than the configured tolerance.

## Out of scope

- Real-time market operations (no live LMP feeds).
- Equity / generation-asset valuation outputs.
- Predictions about which rule changes will be adopted.
- Customer-confidential utility data.
- Policy recommendations.

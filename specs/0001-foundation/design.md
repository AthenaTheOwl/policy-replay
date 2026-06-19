# Spec 0001 — Foundation design

## Shape

A Python CLI plus four layers: a rule loader, per-ISO history
loaders, a rule-to-parameter translator, and a replay simulator. A
report renderer turns replay records into markdown. A calibration
harness back-tests the simulator against rule changes that have
already taken effect.

## Components

### Rule loader (`src/policy_replay/rule/`)

- `loader.py` — reads a YAML rule spec; validates against
  `schemas/rule.schema.json`; returns a `RuleSpec` dataclass.
- `translator.py` — pure function `(rule_spec,
  baseline_parameters) -> modified_parameters`. The mapping
  decisions live in `decisions/DEC-PR-001-translator-rubric.md`.

### History loaders (`src/policy_replay/history/`)

- `pjm_rpm.py` — reads the PJM RPM auction-history parquet at
  `data/pjm_rpm_2018_2023.parquet`; returns clearing prices,
  cleared quantities, and offer curves per LDA per auction year.
- `pjm_queue.py` — reads the PJM interconnection-queue history.
- `miso.py`, `ercot.py` — stubs in v0 raising `NotImplementedError`.

### Replay simulator (`src/policy_replay/sim/`)

- `replay.py` — given baseline parameters and modified parameters
  plus the history snapshot, runs N Monte Carlo trials. Each trial
  evolves the historical state under the modified rule and records
  counterfactual outcomes.
- `counterfactual.py` — small RPM-style clearing model plus
  queue-progression model. The model is intentionally simple; the
  calibration gate exists precisely because the model is simple.

### Report renderer (`src/policy_replay/report/render.py`)

Reads a replay_result record, emits:

- `reports/<rule_id>/report.md` — narrative + tables of baseline vs
  counterfactual outcomes.
- `reports/<rule_id>/figures/*.png`.
- `reports/<rule_id>/replay_result.json` — sidecar.

### Calibration gate (`eval/calibration_against_past_changes.py`)

For each rule change in a calibration set (initially: MOPR), runs
the harness with the rule applied to the pre-rule history and
compares the simulated post-rule outcomes against the actual
post-rule outcomes. Reports the per-outcome miss; fails when any
miss exceeds the tolerance configured in
`decisions/DEC-PR-002-calibration-tolerance.md`.

### Sanity bounds (`eval/sanity_bounds.py`)

Walks every replay_result. Fails if any counterfactual price exceeds
2x the historical baseline, or any cleared quantity goes negative,
or any per-LDA result is missing.

## Data model

```
RuleSpec
  rule_id, name
  proposing_body, proposal_date, effective_target_date
  affected_markets[]
  parameter_overrides: dict
  references[]: { url, retrieved_at, citation_text }

HistorySnapshot
  iso, time_range
  tables: [ { name, parquet_path, row_count, source_url } ]

ReplayResult
  replay_id, rule_id, history_snapshot_ref
  trial_count, seed
  baseline_outcomes
  counterfactual_outcomes
  outcome_delta_summary
```

## Out of scope for spec 0001

- A full nodal market-clearing model. v0 is zonal / LDA-level only.
- Generation-asset-level dispatch.
- Forward-curve modeling beyond the simulated horizon.
- Live ISO API ingestion.
- A web frontend.

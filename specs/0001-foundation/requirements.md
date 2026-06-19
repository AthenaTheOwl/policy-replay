# Spec 0001 — Foundation requirements

The first spec for PolicyReplay. Names the rule schema, the history-
snapshot schema, the replay-result schema, the calibration gate, and
the first worked example.

## Requirements

- **R-PR-001** — The repo MUST expose a `policy-replay` Python
  package with `__version__` and a CLI entry point.

- **R-PR-002** — A rule spec MUST conform to
  `schemas/rule.schema.json` with fields: `rule_id`, `name`,
  `proposing_body` (`FERC|ISO|PUC`), `proposal_date`,
  `effective_target_date`, `affected_markets[]` (e.g. `pjm.rpm`,
  `miso.tariff`), `parameter_overrides` (a dict of named simulation
  parameters this rule changes), `references[]` (URLs to FERC
  filings, ISO postings, or PUC docket pages).

- **R-PR-003** — A history snapshot MUST conform to
  `schemas/history_snapshot.schema.json` with fields: `iso`,
  `time_range` (start / end), `tables[]` (each table name plus
  parquet path plus row count plus source URL).

- **R-PR-004** — The translator MUST be a pure function from
  `(rule_spec, baseline_parameters) -> modified_parameters`. No IO.
  Tested on the seed rule specs.

- **R-PR-005** — A replay result MUST conform to
  `schemas/replay_result.schema.json` with fields: `replay_id`,
  `rule_id`, `history_snapshot_ref`, `trial_count`, `seed`,
  `baseline_outcomes`, `counterfactual_outcomes`,
  `outcome_delta_summary`.

- **R-PR-006** — Determinism: given identical inputs and seed, two
  replays MUST produce byte-identical `replay_result` records.

- **R-PR-007** — The repo MUST include at minimum three rule specs
  in `rules/`: PJM Dec 2025 capacity-market reform, FERC Order 2023
  interconnection reform, NJ BPU data-center cost-allocation draft.
  Each cites at least two primary sources.

- **R-PR-008** — The PJM RPM history loader MUST handle at minimum
  the auction-year window 2018 through 2023 (i.e. the calibration
  cohort) and read from a checked-in parquet fixture.

- **R-PR-009** — The calibration script MUST replay at least one
  rule change that has already taken effect (recommended: MOPR or a
  named MISO Tariff change) and report the delta between the
  harness's predicted post-rule outcome and the actual post-rule
  outcome.

- **R-PR-010** — Voice gate: all reports under `reports/` MUST pass
  voice_lint and MUST NOT contain advocacy verbs ("should", "must",
  "ought") in the narrative.

- **R-PR-011** — All gates run against checked-in fixtures. No live
  ISO or FERC API access at gate time.

- **R-PR-012** — The repo MUST include
  `decisions/DEC-PR-001-translator-rubric.md` documenting how rule
  specs map to simulation parameter overrides, and
  `decisions/DEC-PR-002-calibration-tolerance.md` documenting the
  numeric thresholds the calibration gate enforces.

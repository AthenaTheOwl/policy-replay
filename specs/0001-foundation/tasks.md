# Spec 0001 — Foundation tasks

Ordered task list for the first 2-3 PRs after the scaffold.

## PR 1 — package skeleton plus rule schema plus PJM RPM loader

- [ ] Add `pyproject.toml` declaring `policy-replay` and CLI.
- [ ] Add `src/policy_replay/__init__.py` with `__version__`.
- [ ] Add `src/policy_replay/cli.py` with `version` command.
- [ ] Add `schemas/rule.schema.json` per R-PR-002.
- [ ] Add `schemas/history_snapshot.schema.json` per R-PR-003.
- [ ] Add `src/policy_replay/rule/loader.py`.
- [ ] Add `src/policy_replay/history/pjm_rpm.py`.
- [ ] Add fixture `data/pjm_rpm_2018_2023.parquet` (small,
      derived from public PJM postings).
- [ ] Add `rules/pjm-dec2025-capacity-reform.yaml` with at least
      two FERC / PJM-posting references.
- [ ] Add `tests/test_rule_loader.py`,
      `tests/test_pjm_rpm_loader.py`.
- [ ] Add `decisions/DEC-PR-001-translator-rubric.md`,
      `decisions/DEC-PR-002-calibration-tolerance.md`.

## PR 2 — translator plus replay simulator

- [ ] Add `src/policy_replay/rule/translator.py`.
- [ ] Add `schemas/replay_result.schema.json`.
- [ ] Add `src/policy_replay/sim/counterfactual.py` (zonal RPM
      clearing).
- [ ] Add `src/policy_replay/sim/replay.py`.
- [ ] Add `tests/test_translator.py`,
      `tests/test_replay_determinism.py`,
      `tests/test_counterfactual.py`.
- [ ] Add `scripts/voice_lint.py`,
      `scripts/validate_schemas.py`.

## PR 3 — report renderer plus calibration gate

- [ ] Add `src/policy_replay/report/render.py`.
- [ ] Run the simulator against the PJM Dec 2025 rule.
- [ ] Check in `reports/pjm-dec2025-replay/report.md` plus the
      sidecar JSON.
- [ ] Add `eval/sanity_bounds.py`.
- [ ] Add `eval/calibration_against_past_changes.py` using a MOPR
      backtest fixture.
- [ ] Add `rules/ferc-order-2023-interconnection-reform.yaml`,
      `rules/nj-bpu-datacenter-cost-allocation-draft.yaml`.
- [ ] Add `docs/dev/authoring-a-rule-spec.md`.

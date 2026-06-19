# First PR after the scaffold

Branch: `feat/0001-rule-schema-and-pjm-loader`

## Scope

Land the package skeleton, the rule and history schemas, the rule
loader, the PJM RPM history loader, and the first rule spec (PJM
Dec 2025 capacity-market reform).

### Files added

- `pyproject.toml` — declares `policy-replay`, CLI entry
  `policy-replay = "policy_replay.cli:main"`, dev deps (pytest,
  jsonschema, pyyaml, pandas, pyarrow, numpy, click).
- `src/policy_replay/__init__.py` — `__version__ = "0.0.1"`.
- `src/policy_replay/cli.py` — Click app with `version` command.
- `schemas/rule.schema.json` — per R-PR-002.
- `schemas/history_snapshot.schema.json` — per R-PR-003.
- `src/policy_replay/rule/__init__.py`
- `src/policy_replay/rule/loader.py` — `load_rule(path)` returns
  a validated `RuleSpec` dataclass.
- `src/policy_replay/history/__init__.py`
- `src/policy_replay/history/pjm_rpm.py` — reads parquet,
  returns a `PjmRpmHistory` dataclass with per-LDA per-year
  clearing prices and quantities.
- `rules/pjm-dec2025-capacity-reform.yaml` — with at least two
  primary-source references (FERC docket URL plus PJM posting URL).
- `data/pjm_rpm_2018_2023.parquet` — small public-data fixture
  (auction-year clearing summaries only, not raw offer curves).
- `tests/test_rule_loader.py` — schema validation tests.
- `tests/test_pjm_rpm_loader.py` — loads the fixture, asserts
  per-LDA structure, asserts no NaN in clearing prices.
- `decisions/DEC-PR-001-translator-rubric.md` — names how a rule
  spec maps to parameter overrides; placeholder for the actual
  mapping table that PR 2 fills in.
- `decisions/DEC-PR-002-calibration-tolerance.md` — names the
  numeric tolerances the calibration gate will enforce in PR 3.

### Files NOT touched

- `src/policy_replay/rule/translator.py` — empty until PR 2.
- `src/policy_replay/sim/` — empty until PR 2.
- `src/policy_replay/report/` — empty until PR 3.
- `eval/` — empty until PR 2.
- `scripts/` — empty until PR 2.

## Verification

```bash
uv pip install -e .[dev]
python -m policy_replay version
# expect: policy-replay 0.0.1

uv run pytest
# expect: 2 tests pass

python -c "
from policy_replay.rule.loader import load_rule
from policy_replay.history.pjm_rpm import load_pjm_rpm
r = load_rule('rules/pjm-dec2025-capacity-reform.yaml')
h = load_pjm_rpm('data/pjm_rpm_2018_2023.parquet')
print(r.rule_id, r.proposing_body, len(r.references))
print(h.iso, h.time_range, len(h.per_lda_clearing_prices))
"
```

## Out of scope for this PR

- The translator (no parameter mapping logic yet).
- The replay simulator.
- The report renderer.
- voice_lint and calibration scripts.
- MISO / ERCOT history loaders.

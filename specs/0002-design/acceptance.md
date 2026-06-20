# acceptance - 0002-design

Accepted when:

- `python -m policy_replay simulate` writes `reports/pjm-dec2025-replay/replay_result.json`.
- `python -m policy_replay validate` passes.
- `python scripts/validate_schemas.py` passes.
- `python eval/sanity_bounds.py` passes.
- `python -m pytest tests/ -q` passes.


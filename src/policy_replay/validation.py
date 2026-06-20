from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_result(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_result(path: Path) -> None:
    data = load_result(path)
    if data["trial_count"] != 1:
        raise ValueError("v0.1 expects trial_count=1")
    if data["seed"] < 0:
        raise ValueError("seed must be non-negative")
    for key in ("baseline_outcomes", "counterfactual_outcomes", "outcome_delta_summary"):
        if not data.get(key):
            raise ValueError(f"missing {key}")


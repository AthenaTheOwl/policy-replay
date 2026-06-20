from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        import jsonschema
    except ImportError as exc:
        raise SystemExit("jsonschema is required") from exc
    rule_schema = json.loads((ROOT / "schemas" / "rule.schema.json").read_text(encoding="utf-8"))
    result_schema = json.loads((ROOT / "schemas" / "replay_result.schema.json").read_text(encoding="utf-8"))
    jsonschema.validators.validator_for(rule_schema).check_schema(rule_schema)
    jsonschema.validators.validator_for(result_schema).check_schema(result_schema)
    for path in (ROOT / "rules").glob("*.json"):
        jsonschema.validate(json.loads(path.read_text(encoding="utf-8")), rule_schema)
    for path in (ROOT / "reports").glob("*/replay_result.json"):
        jsonschema.validate(json.loads(path.read_text(encoding="utf-8")), result_schema)
    print("validate_schemas OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())


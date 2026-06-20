from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.policy_replay.validation import validate_result  # noqa: E402


def main() -> int:
    for path in (ROOT / "reports").glob("*/replay_result.json"):
        validate_result(path)
    print("sanity_bounds OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())


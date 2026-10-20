"""Every script a fenced command in AGENTS.md runs must exist."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _fenced_script_paths(text: str) -> list[str]:
    paths: list[str] = []
    for block in re.findall(r"```(?:bash|sh)?\n(.*?)```", text, flags=re.S):
        paths.extend(re.findall(r"\bpython3?\s+((?:[\w.-]+/)*[\w.-]+\.py)\b", block))
    return paths


def test_agents_md_script_commands_point_at_files() -> None:
    paths = _fenced_script_paths((ROOT / "AGENTS.md").read_text(encoding="utf-8"))
    assert paths, "expected at least one script command in AGENTS.md"
    missing = [path for path in paths if not (ROOT / path).is_file()]
    assert missing == []

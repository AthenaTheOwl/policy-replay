from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import AuctionRow, RuleSpec


def load_rule(path: Path) -> RuleSpec:
    data = json.loads(path.read_text(encoding="utf-8"))
    if len(data.get("references", [])) < 2:
        raise ValueError(f"{path} has fewer than two references")
    return RuleSpec(**data)


def load_history(path: Path) -> list[AuctionRow]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = []
        for row in csv.DictReader(handle):
            rows.append(
                AuctionRow(
                    auction_year=int(row["auction_year"]),
                    lda=row["lda"],
                    clearing_price_usd_mw_day=float(row["clearing_price_usd_mw_day"]),
                    cleared_mw=float(row["cleared_mw"]),
                    reserve_margin_pct=float(row["reserve_margin_pct"]),
                )
            )
    if not rows:
        raise ValueError(f"{path} has no history rows")
    return rows


"""Load and normalize roster data exported from a baseball sim/game.

Expected CSV columns:
- Name
- Age
- Salary (supports "$1,234,567" or "1234567")
"""

from __future__ import annotations

import csv
import os
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

PathLike = str | os.PathLike[str]


def _parse_int(value: str) -> int:
    cleaned = value.strip().replace("$", "").replace(",", "")
    return int(cleaned) if cleaned else 0


def load_team_data(path: PathLike = "exports/team_roster.csv") -> list[dict[str, Any]]:
    """Load team data from a CSV path.

    Returns an empty list if the file does not exist or cannot be parsed.
    """
    p = Path(path)
    if not p.exists():
        print(f"Missing team export: {p}")
        return []

    try:
        with p.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return _rows_to_players(reader)
    except Exception as exc:
        print(f"Failed to read team export {p}: {exc}")
        return []


def _rows_to_players(rows: Iterable[Mapping[str, str]]) -> list[dict[str, Any]]:
    players: list[dict[str, Any]] = []
    for row in rows:
        try:
            players.append(
                {
                    "name": row.get("Name", "").strip(),
                    "age": _parse_int(row.get("Age", "")),
                    "salary": _parse_int(row.get("Salary", "")),
                }
            )
        except Exception:
            continue
    return players

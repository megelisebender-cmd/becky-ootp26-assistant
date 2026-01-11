from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


PathLike = str | os.PathLike[str]


@dataclass(frozen=True)
class TableInfo:
    """Metadata about a discovered export table."""

    name: str
    path: Path
    rows: int | None = None


def discover_csv_tables(root: PathLike) -> list[TableInfo]:
    """Discover CSV export tables under *root*.

    - If *root* is a file, it must be a CSV and will be returned as a single table.
    - If *root* is a directory, all `*.csv` files under it (recursively) are returned.
    """
    p = Path(root).expanduser()
    if p.is_file():
        if p.suffix.lower() != ".csv":
            return []
        return [TableInfo(name=p.stem, path=p)]

    if not p.exists():
        return []

    tables: list[TableInfo] = []
    for csv_path in sorted(p.rglob("*.csv")):
        # Use a name relative to root so subfolders don't collide.
        rel = csv_path.relative_to(p)
        name = str(rel.with_suffix(""))
        tables.append(TableInfo(name=name, path=csv_path))
    return tables


def read_csv_rows(path: PathLike, limit: int | None = None) -> list[dict[str, str]]:
    """Read CSV rows as dictionaries.

    This intentionally avoids pandas to keep runtime dependencies optional.
    """
    p = Path(path).expanduser()
    with p.open(newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        rows: list[dict[str, str]] = []
        for i, row in enumerate(reader):
            rows.append({k: (v if v is not None else "") for k, v in row.items()})
            if limit is not None and i + 1 >= limit:
                break
        return rows


def infer_numeric(value: str) -> float | None:
    """Best-effort numeric parsing for values like "$1,234" or "12.3%"."""
    s = (value or "").strip()
    if not s:
        return None
    neg = s.startswith("(") and s.endswith(")")
    if neg:
        s = s[1:-1]

    # common decorations
    for ch in ["$", ",", "%"]:
        s = s.replace(ch, "")

    try:
        x = float(s)
        return -x if neg else x
    except Exception:
        return None


def first_nonempty(values: Iterable[str]) -> str:
    for v in values:
        if v and v.strip():
            return v.strip()
    return ""


def pick_name_field(row: dict[str, Any]) -> str:
    """Try common name column patterns across OOTP exports."""
    keys = {k.lower(): k for k in row.keys()}
    candidates = []
    for k in [
        "name",
        "player",
        "player name",
        "playername",
        "full name",
        "fullname",
        "first name",
        "lastname",
        "last name",
        "namefirst",
        "namelast",
        "namegiven",
    ]:
        if k in keys:
            candidates.append(str(row.get(keys[k], "")))
    # Special case: first + last
    first = str(row.get(keys.get("namefirst", ""), "")) if "namefirst" in keys else ""
    last = str(row.get(keys.get("namelast", ""), "")) if "namelast" in keys else ""
    if first or last:
        candidates.insert(0, f"{first} {last}".strip())
    return first_nonempty(candidates)

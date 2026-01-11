from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# -----------------------------
# helpers
# -----------------------------

def _to_int(s: str) -> int | None:
    s = (s or "").strip()
    if not s:
        return None
    if re.fullmatch(r"-?\d+", s):
        try:
            return int(s)
        except Exception:
            return None
    return None


def _read_txt_rows(path: Path) -> list[list[str]]:
    """
    OOTP txt reports: lots of // comments, then comma-delimited rows.
    """
    rows: list[list[str]] = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("//"):
                continue
            # some OOTP reports put a "..." separator in between blocks
            if line == "...":
                continue
            rows.append(next(csv.reader([line])))
    return rows


def find_export_root(root: Path) -> Path:
    """
    Accepts:
      - saved_game root (...\\Megan Bender 01.lg)
      - import_export folder
      - exports folder

    Returns the best folder that actually contains OOTP export files.
    """
    root = root.expanduser()

    # If they pointed directly at import_export or exports, use it.
    if (root / "mlb_rosters.txt").exists() or (root / "player_batting_stats.txt").exists():
        return root

    # If they pointed at saved_game root, prefer import_export, else exports.
    for sub in ("import_export", "exports"):
        cand = root / sub
        if cand.exists() and (
            (cand / "mlb_rosters.txt").exists()
            or (cand / "player_batting_stats.txt").exists()
            or (cand / "team_roster.csv").exists()
        ):
            return cand

    # Otherwise just return what we were given.
    return root


# -----------------------------
# specific report parsers
# -----------------------------

def load_mlb_rosters_txt(path: Path, *, league_year: int | None = None) -> list[dict[str, Any]]:
    """
    mlb_rosters.txt is wide and has no explicit header line.
    We pull the fields we care about by index.

    Verified on your sample:
      - last_name = col 5
      - first_name = col 6
      - birth_year = col 11
      - salary = col 95
      - team_name = col 3
      - league_name = col 4
    """
    rows = _read_txt_rows(path)
    if league_year is None:
        league_year = datetime.now().year

    out: list[dict[str, Any]] = []
    for r in rows:
        # guard: some rows might be shorter in certain exports
        def get(i: int, row=r) -> str:
            return row[i].strip() if i < len(row) else ""
        player_id = _to_int(get(0))
        team_id = _to_int(get(2))
        team_name = get(3)
        league_name = get(4)
        last = get(5)
        first = get(6)

        birth_year = _to_int(get(11))
        age = (league_year - birth_year) if (birth_year and league_year) else None

        salary = _to_int(get(95))  # looks like current-year salary in your file

        name = (first + " " + last).strip()

        out.append(
            {
                "Name": name,
                "Age": age,
                "Salary": salary,
                "player_id": player_id,
                "team_id": team_id,
                "team_name": team_name,
                "league_name": league_name,
                # keep raw width in case you want to expand later:
                "_raw": r,
            }
        )
    return out


def load_player_batting_stats_txt(path: Path) -> list[dict[str, Any]]:
    """
    First columns in your sample:
      0 player_id, 1 last, 2 first, 3 year, 4 team_id, ...
    """
    rows = _read_txt_rows(path)
    out: list[dict[str, Any]] = []
    for r in rows:
        def get(i: int, row=r) -> str:
            return row[i].strip() if i < len(row) else ""
        out.append(
            {
                "player_id": _to_int(get(0)),
                "last": get(1),
                "first": get(2),
                "year": _to_int(get(3)),
                "team_id": _to_int(get(4)),
                "_raw": r,
            }
        )
    return out


def load_player_pitching_stats_txt(path: Path) -> list[dict[str, Any]]:
    """
    First columns in your sample:
      0 player_id, 1 last, 2 first, 3 year, 4 team_id, ...
    """
    rows = _read_txt_rows(path)
    out: list[dict[str, Any]] = []
    for r in rows:
        def get(i: int, row=r) -> str:
            return row[i].strip() if i < len(row) else ""
        out.append(
            {
                "player_id": _to_int(get(0)),
                "last": get(1),
                "first": get(2),
                "year": _to_int(get(3)),
                "team_id": _to_int(get(4)),
                "_raw": r,
            }
        )
    return out


def load_player_fielding_stats_txt(path: Path) -> list[dict[str, Any]]:
    """
    First columns in your sample:
      0 player_id, 1 last, 2 first, 3 year, 4 team_id, ...
    """
    rows = _read_txt_rows(path)
    out: list[dict[str, Any]] = []
    for r in rows:
        def get(i: int, row=r) -> str:
            return row[i].strip() if i < len(row) else ""
        out.append(
            {
                "player_id": _to_int(get(0)),
                "last": get(1),
                "first": get(2),
                "year": _to_int(get(3)),
                "team_id": _to_int(get(4)),
                "_raw": r,
            }
        )
    return out


# -----------------------------
# discovery / listing
# -----------------------------

@dataclass
class Table:
    name: str
    path: Path
    rows: list[dict[str, Any]]


def load_all_tables(export_root: Path, *, league_year: int | None = None) -> dict[str, Table]:
    export_root = find_export_root(export_root)

    tables: dict[str, Table] = {}

    # roster (preferred)
    rosters = export_root / "mlb_rosters.txt"
    if rosters.exists():
        rows = load_mlb_rosters_txt(rosters, league_year=league_year)
        tables["mlb_rosters"] = Table("mlb_rosters", rosters, rows)

    # other txt stats
    bat = export_root / "player_batting_stats.txt"
    if bat.exists():
        tables["player_batting_stats"] = Table("player_batting_stats", bat, load_player_batting_stats_txt(bat))

    pit = export_root / "player_pitching_stats.txt"
    if pit.exists():
        tables["player_pitching_stats"] = Table("player_pitching_stats", pit, load_player_pitching_stats_txt(pit))

    fld = export_root / "player_fielding_stats.txt"
    if fld.exists():
        tables["player_fielding_stats"] = Table("player_fielding_stats", fld, load_player_fielding_stats_txt(fld))

    # existing CSV compatibility (if you ever have it)
    team_csv = export_root / "team_roster.csv"
    if team_csv.exists():
        import pandas as pd
        df = pd.read_csv(team_csv)
        rows = df.to_dict(orient="records")
        tables["team_roster"] = Table("team_roster", team_csv, rows)

    return tables


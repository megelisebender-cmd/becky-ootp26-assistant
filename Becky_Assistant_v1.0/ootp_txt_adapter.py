from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class RosterRow:
    name: str
    team: str
    league: str
    age: int | None
    salary: int | None


def _safe_int(v: str) -> int | None:
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    try:
        return int(float(s))
    except Exception:
        return None


def _guess_season_year() -> int:
    env = (os.getenv("BECKY_SEASON_YEAR") or "").strip()
    if env.isdigit():
        return int(env)
    return date.today().year


def _compute_age(birth_y: int, birth_m: int, birth_d: int, season_year: int) -> int:
    # OOTP “season” age isn’t perfectly defined; this is a solid approximation:
    # compute age as of July 1 of season_year.
    ref_m, ref_d = 7, 1
    age = season_year - birth_y
    if (birth_m, birth_d) > (ref_m, ref_d):
        age -= 1
    return age


def _find_mlb_rosters_file(export_root: Path) -> Path | None:
    """
    We check common placements:
      - export_root/mlb_rosters.txt
      - export_root/exports/mlb_rosters.txt
      - export_root/import_export/mlb_rosters.txt
    Also if export_root itself is a .lg folder, prefer .lg/import_export.
    """
    export_root = Path(export_root)

    candidates: list[Path] = []

    # If user points to the .lg itself
    if export_root.suffix.lower() == ".lg":
        candidates.append(export_root / "import_export" / "mlb_rosters.txt")

    # Normal cases
    candidates.extend(
        [
            export_root / "mlb_rosters.txt",
            export_root / "exports" / "mlb_rosters.txt",
            export_root / "import_export" / "mlb_rosters.txt",
        ]
    )

    for c in candidates:
        if c.exists() and c.is_file():
            return c
    return None


def parse_mlb_rosters(export_root: Path) -> list[RosterRow]:
    """
    Parses OOTP 'mlb_rosters.txt' report into structured rows.
    Works with the format where:
      - column names are in a comment line starting with //id, del, team_id...
      - data lines are comma-separated values
    """
    p = _find_mlb_rosters_file(Path(export_root))
    if not p:
        return []

    # Find the header column mapping from the //id,... line.
    col_map: dict[str, int] = {}
    with p.open("r", encoding="utf-8", errors="replace", newline="") as f:
        for line in f:
            s = line.strip()
            if s.startswith("//id,") or s.startswith("//id ,") or s.startswith("//id, del"):
                header = s.lstrip("/").strip()
                cols = [c.strip() for c in header.split(",")]
                col_map = {name: idx for idx, name in enumerate(cols)}
                break

    if not col_map:
        # Fallback: assume no header; not expected, but avoid crashing.
        return []

    # Required columns (by name)
    def idx(name: str) -> int:
        if name not in col_map:
            raise KeyError(f"Missing column in mlb_rosters.txt header: {name}")
        return col_map[name]

    i_team = idx("Team Name")
    i_league = idx("League Name")
    i_last = idx("LastName")
    i_first = idx("FirstName")

    i_day = idx("DayOB")
    i_month = idx("MonthOB")
    i_year = idx("YearOB")

    i_contract_current = idx("contract current year")

    # contract y1..y7 exist in this report
    contract_year_idxs: list[int] = []
    for k in ["contract y1", "contract y2", "contract y3", "contract y4", "contract y5", "contract y6", "contract y7"]:
        if k in col_map:
            contract_year_idxs.append(col_map[k])

    season_year = _guess_season_year()

    rows: list[RosterRow] = []
    with p.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f)
        for raw in reader:
            if not raw:
                continue
            # skip comment lines and weird header-ish junk
            first_cell = (raw[0] or "").strip()
            if first_cell.startswith("//"):
                continue

            # Ensure we can index into the columns we need
            min_len = max(i_team, i_league, i_last, i_first, i_day, i_month, i_year, i_contract_current)
            if len(raw) <= min_len:
                continue

            team = (raw[i_team] or "").strip()
            league = (raw[i_league] or "").strip()
            first = (raw[i_first] or "").strip()
            last = (raw[i_last] or "").strip()
            name = (first + " " + last).strip()
            if not name:
                continue

            by = _safe_int(raw[i_year]) or 0
            bm = _safe_int(raw[i_month]) or 0
            bd = _safe_int(raw[i_day]) or 0
            age: int | None = None
            if by > 0 and 1 <= bm <= 12 and 1 <= bd <= 31:
                age = _compute_age(by, bm, bd, season_year)

            # Salary: pick contract year based on "contract current year"
            # 0 => y1, 1 => y2, etc. If out of range, fall back to y1.
            salary: int | None = None
            cur = _safe_int(raw[i_contract_current])
            if contract_year_idxs:
                pick = 0
                if cur is not None and 0 <= cur < len(contract_year_idxs):
                    pick = cur
                y_idx = contract_year_idxs[pick]
                if len(raw) > y_idx:
                    salary = _safe_int(raw[y_idx])

            rows.append(RosterRow(name=name, team=team, league=league, age=age, salary=salary))

    return rows

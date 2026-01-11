from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any

from ootp_txt_adapter import parse_mlb_rosters


def load_team_data(
    export_root: str | Path | None = None,
    export_path: str | None = None,
) -> list[dict[str, Any]]:
    """
    Loads roster data for Becky.

    Priority:
      1) If roster CSV exists (exports/team_roster.csv by default), use it.
      2) Otherwise parse OOTP TXT report mlb_rosters.txt (from export_root / exports / import_export).
      3) If nothing found, print guidance and return [].
    """
    # Allow calling patterns:
    # - load_team_data(export_root="C:\\...\\import_export")
    # - load_team_data(export_root, export_path="exports/team_roster.csv")
    # - load_team_data() -> uses BECKY_EXPORT_ROOT if set, else cwd
    if export_root is None or str(export_root).strip() == "":
        export_root = os.getenv("BECKY_EXPORT_ROOT", "") or "."
    export_root_path = Path(str(export_root)).expanduser()

    if export_path is None or export_path.strip() == "":
        export_path = os.getenv("BECKY_EXPORT_PATH", "exports/team_roster.csv")

    # 1) CSV path (back-compat)
    p = export_root_path / export_path
    if p.exists() and p.is_file():
        with p.open("r", encoding="utf-8", errors="replace", newline="") as f:
            return list(csv.DictReader(f))

    # 2) TXT fallback
    roster_rows = parse_mlb_rosters(export_root_path)
    if roster_rows:
        team_filter = (os.getenv("BECKY_TEAM", "") or "").strip().lower()
        league_filter = (os.getenv("BECKY_LEAGUE", "") or "").strip().lower()

        filtered = roster_rows
        if league_filter:
            filtered = [r for r in filtered if league_filter in (r.league or "").lower()]
        if team_filter:
            filtered = [r for r in filtered if team_filter in (r.team or "").lower()]

        return [
            {
                "Name": r.name,
                "Age": "" if r.age is None else str(r.age),
                "Salary": "" if r.salary is None else str(r.salary),
                "Team": r.team,
                "League": r.league,
            }
            for r in filtered
        ]

    # 3) Nothing found
    print(f"Missing team export: {p}")
    print("Also did not find OOTP TXT report: mlb_rosters.txt (checked export_root, exports/, import_export/).")
    print(r"Tip: set BECKY_EXPORT_ROOT to your .lg\import_export folder, or use: setroot ""C:\path with spaces""")
    return []

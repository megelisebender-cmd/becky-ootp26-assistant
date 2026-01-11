from __future__ import annotations

import os
from pathlib import Path


def guess_saved_games_dirs() -> list[Path]:
    """Return plausible OOTP 26 saved_games directories.

    This is best-effort and intentionally conservative: we only return paths that
    exist on disk.
    """

    home = Path.home()
    candidates = [
        home / "Documents" / "Out of the Park Developments" / "OOTP Baseball 26" / "saved_games",
        home / "Documents" / "OOTP Baseball 26" / "saved_games",
        home / "OneDrive" / "Documents" / "Out of the Park Developments" / "OOTP Baseball 26" / "saved_games",
        home / "OneDrive" / "Documents" / "OOTP Baseball 26" / "saved_games",
    ]

    existing: list[Path] = []
    for p in candidates:
        try:
            if p.exists() and p.is_dir():
                existing.append(p)
        except Exception:
            continue
    return existing


def find_export_roots(saved_games_dir: Path, max_leagues: int = 20) -> list[Path]:
    """Search for league export folders under a saved_games directory.

    Looks for `<league>.lg/exports` and `<league>.lg/export` (both exist in the wild).
    """

    roots: list[Path] = []
    try:
        lg_dirs = [p for p in saved_games_dir.iterdir() if p.is_dir() and p.name.endswith(".lg")]
    except Exception:
        return []

    for lg in sorted(lg_dirs)[:max_leagues]:
        for sub in ["exports", "export"]:
            p = lg / sub
            if p.exists() and any(p.rglob("*.csv")):
                roots.append(p)
                break
    return roots

from __future__ import annotations

import os
import shlex
from pathlib import Path

import baseball_queries
import becky_voice
import data_adapter
from ootp.paths import find_export_roots, guess_saved_games_dirs
from ootp.store import ExportStore


def _format_rows(rows: list[dict[str, str]], max_cols: int = 8) -> str:
    if not rows:
        return "(no rows)"
    cols = list(rows[0].keys())[:max_cols]
    lines = [" | ".join(cols)]
    lines.append("-" * len(lines[0]))
    for r in rows[:10]:
        lines.append(" | ".join((r.get(c, "") or "")[:40] for c in cols))
    if len(rows) > 10:
        lines.append(f"... ({len(rows)} rows matched; showing 10)")
    return "\n".join(lines)


def run_becky() -> None:
    """Run Becky in text-only interactive mode."""
    becky_voice.speak("Hi Coach — text-only mode is online. Type 'help' for commands.")

    # Back-compat: BECKY_EXPORT_PATH can point to a single roster CSV RELATIVE TO EXPORT ROOT.
    # New: BECKY_EXPORT_ROOT points to the directory that contains exports/ and/or mlb_rosters.txt.
    export_root = os.getenv("BECKY_EXPORT_ROOT", "").strip()

    # If no export root set, fall back to current folder (keeps fixtures/dev behavior working).
    export_root_path = Path(os.path.expandvars(export_root)).expanduser() if export_root else Path.cwd()

    team_data = data_adapter.load_team_data(export_root_path)

    store = ExportStore()
    if export_root:
        store.load(str(export_root_path))

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not raw:
            continue

        parts = shlex.split(raw)
        cmd = parts[0].lower()

        if cmd in {"quit", "exit", "q"}:
            break
        if cmd in {"help", "h", "?"}:
            becky_voice.speak(baseball_queries.help_text())
            continue
        if cmd == "reload":
            team_data = data_adapter.load_team_data(export_root_path)
            if export_root:
                store.load(str(export_root_path))
            becky_voice.speak("Reloaded exports.")
            continue
        if cmd == "where":
            out = [f"Export root: {export_root_path}"]
            out.append("Roster source: CSV if present, otherwise TXT (mlb_rosters.txt)")
            if store.is_loaded():
                out.append(f"CSV tables: {len(store.table_names())}")
            becky_voice.speak("\n".join(out))
            continue

        # Export root controls
        if cmd == "setroot":
            if len(parts) < 2:
                becky_voice.speak("Usage: setroot <path-to-exports-folder>")
                continue
            export_root = os.path.expandvars(parts[1])
            export_root_path = Path(export_root).expanduser()
            store.load(str(export_root_path))
            team_data = data_adapter.load_team_data(export_root_path)
            becky_voice.speak(
                f"Loaded export root. CSV tables found: {len(store.table_names())}. "
                f"Roster will load from CSV if present, otherwise from TXT reports."
            )
            continue

        if cmd == "autodetect":
            dirs = guess_saved_games_dirs()
            if not dirs:
                becky_voice.speak(
                    "Couldn't find a default OOTP 26 saved_games folder on this machine. "
                    "Try: setroot <your .lg\\import_export folder>"
                )
                continue

            roots: list[Path] = []
            for d in dirs:
                roots.extend(find_export_roots(d))

            if not roots:
                becky_voice.speak(
                    "Found saved_games folders, but no export roots detected. "
                    "Tip: use setroot to point directly at your .lg\\import_export folder."
                )
                continue

            lines = ["Possible exports folders:"]
            lines.append("TXT report roots (mlb_rosters.txt):")
            for i, r in enumerate(roots[:25], start=1):
                lines.append(f"  {i}. {r}")
            lines.append("Use: setroot <one of these paths>")
            becky_voice.speak("\n".join(lines))
            continue

        if cmd == "tables":
            if not store.is_loaded():
                becky_voice.speak("No export root loaded. Use: setroot <folder>")
                continue
            names = store.table_names()
            becky_voice.speak("\n".join(["Discovered tables:", *names[:200]]) + ("\n..." if len(names) > 200 else ""))
            continue

        if cmd == "describe":
            if len(parts) < 2:
                becky_voice.speak("Usage: describe <table>")
                continue
            t = store.describe(parts[1])
            if t is None:
                becky_voice.speak("Table not found. Use: tables")
                continue
            becky_voice.speak(
                "\n".join(
                    [
                        f"Table: {t.info.name}",
                        f"Path: {t.info.path}",
                        f"Columns ({len(t.columns)}): {', '.join(t.columns[:60])}{' ...' if len(t.columns) > 60 else ''}",
                        "Sample:",
                        _format_rows(t.sample),
                    ]
                )
            )
            continue

        if cmd == "search":
            if len(parts) < 4:
                becky_voice.speak("Usage: search <table> <column> <substring>")
                continue
            table, col, needle = parts[1], parts[2], " ".join(parts[3:])
            rows = store.find_rows(table, {col: needle})
            becky_voice.speak(_format_rows(rows))
            continue

        # Queries
        if cmd == "analyze":
            becky_voice.speak(baseball_queries.analyze_team(team_data))
        elif cmd == "youngest":
            becky_voice.speak(baseball_queries.youngest_player(team_data))
        elif cmd == "oldest":
            becky_voice.speak(baseball_queries.oldest_player(team_data))
        elif cmd in {"highest", "highest_salary"}:
            becky_voice.speak(baseball_queries.highest_salary(team_data))
        elif cmd == "top":
            if len(parts) >= 2 and parts[1].lower() == "salaries":
                n = 5
                if len(parts) >= 3:
                    try:
                        n = max(1, int(parts[2]))
                    except Exception:
                        n = 5
                becky_voice.speak(baseball_queries.top_salaries(team_data, n=n))
            else:
                becky_voice.speak("Try: top salaries 5")
        else:
            becky_voice.speak("I didn't recognize that. Type 'help' to see commands.")


if __name__ == "__main__":
    run_becky()

# Becky Assistant GM (text-only)

Text-only assistant for **Out of the Park Baseball (OOTP)** exports.

## Quickstart
```bash
pip install -r requirements.txt
python launcher.py
```

## Input data
By default Becky reads:
- `exports/team_roster.csv`

You can override the roster export path:
```bash
# Windows PowerShell
$env:BECKY_EXPORT_PATH="exports/team_roster.csv"
```

Expected columns (current starter set):
- `Name`, `Age`, `Salary`

### Folder-of-exports mode (recommended)
If you point Becky at a folder, she will discover **all CSV files** and expose
introspection commands (tables, describe, search). This makes it resilient to
different export setups.

Set an exports folder:
```bash
# Windows PowerShell
$env:BECKY_EXPORT_ROOT="C:\\path\\to\\your\\saved_games\\YourLeague.lg\\exports"
```

Or from inside Becky:
```
setroot C:\path\to\exports
tables
describe stats/Teams
search stats/Teams teamID CLE
```

## Commands
Run and type `help` inside the app.

## Next steps toward full OOTP 26 integration
This version can read either a single roster CSV or a folder of CSV exports.
The roadmap is to add higher-level "GM tools" on top of discovered data:

- Players/teams/rosters across levels
- Contracts, options, arbitration/service time
- Injuries + availability
- Transactions + waiver/DFA/Rule-5 awareness
- Schedule/standings + upcoming opponents
- Live game state (play-by-play file watcher)

## Quickstart (TXT reports / import_export)

Becky can load your roster from OOTP TXT reports (ex: `mlb_rosters.txt`) inside your league’s `import_export` folder.

### 1) Set your export root (recommended)
PowerShell (quotes matter if you have spaces):

```powershell
$env:BECKY_EXPORT_ROOT="C:\Users\mdb85\OneDrive\Documents\Out of the Park Developments\OOTP Baseball 26\saved_games\Megan Bender 01.lg\import_export"
$env:BECKY_LEAGUE="Major League Baseball"    # optional filter
$env:BECKY_SEASON_YEAR="2026"                # optional, improves age calc
python launcher.py

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

# Becky Assistant GM v1.0 — Codex Handoff

## What this repo is
A tiny Python voice assistant ("Becky") meant to act like a baseball GM coach for **Out of the Park Baseball (OOTP)** exports.

Current flow:
1. `launcher.py` calls `assistant_gm.run_becky()`
2. Becky greets the user
3. `data_adapter.load_team_data()` loads `exports/team_roster.csv`
4. `baseball_queries.analyze_team()` returns a simple summary
5. `becky_voice.speak()` uses ElevenLabs to speak the text

## How to run (current)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python launcher.py
```

## Current limitations / known issues
- ElevenLabs API key is hard-coded in `becky_voice.py` (unsafe, not portable).
- No “conversation loop” (it speaks once and exits).
- No intent routing (only a single analysis).
- CSV parsing assumes exact columns and formatting.
- No tests, no linting, no typing.
- `prompt.txt` is currently truncated and not usable as a spec.

## Desired direction (high-level)
- Make Becky usable hands-free for common roster/GM questions.
- Keep a clean architecture: **data loading → domain analysis → intents → voice/IO**.
- Make it safe to run without voice (CI/tests) via a “no-voice” mode.

See:
- `codex/PROMPT_FOR_CODEX.md` (paste into Codex)
- `codex/IMPROVEMENT_PLAN.md` (prioritized backlog with acceptance criteria)
- `codex/ARCHITECTURE.md` (target structure)

# Paste this into Codex (or similar coding agent)

You are working on a Python project: **Becky Assistant GM** (voice assistant for OOTP exports).

## Mission
Improve the codebase for safety, maintainability, and real usability:
- Add a conversation loop and intent routing.
- Remove hard-coded secrets.
- Make voice optional (no network calls required to run/tests).
- Harden OOTP CSV parsing.
- Add tests.

## Constraints
- Python 3.10+.
- Keep changes small, readable, and well-structured.
- Prefer standard library unless a dependency adds clear value.
- Do not require external services to run tests.
- Follow PEP 8, add type hints and docstrings for public functions.

## What to do (do these steps in order)
1) Read the repository structure and summarize what each file does.
2) Implement P0 items from `codex/IMPROVEMENT_PLAN.md`.
3) Add `pytest` tests (P1.6).
4) Ensure `python launcher.py` still works.
5) Provide a short CHANGELOG in the final message.

## Running commands
- Install: `pip install -r requirements.txt`
- Run: `python launcher.py`
- Tests: `pytest -q`

## Notes
- ElevenLabs should be behind an adapter with graceful fallback:
  - If `ELEVENLABS_API_KEY` missing or `--no-voice` enabled: print instead of speaking.
- CSV expected input: `exports/team_roster.csv` with columns like `Name`, `Age`, `Salary`.
  - Parsing must be resilient if Salary is blank or formatted differently.

## Deliverables
- Updated Python modules.
- New tests under `tests/`.
- Updated docs (`README.txt` can be converted to `README.md` if desired).

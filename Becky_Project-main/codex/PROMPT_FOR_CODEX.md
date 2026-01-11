# PROMPT FOR CODEX (start here)

You are Codex working on the GitHub repo for **Becky** (a small Python assistant that reads a CSV roster export and speaks a summary).
Your job: **make the app reliable, configurable, testable, and easy to extend** without breaking current behavior.

## Ground rules
- Never commit secrets. All keys/config must come from env vars or config files excluded by git.
- Keep current functionality working: `python Becky_Assistant_v1.0/launcher.py`.
- Prefer small, reviewable commits. Work on a branch and open a PR.

## What to read first
- `Becky_Assistant_v1.0/codex/CODEX_HANDOFF.md` (legacy handoff)
- `codex/PLAN.md`

## Phases (do in order)

### Phase 0 — Run + safety (P0)
1. Ensure app runs with **no** ElevenLabs key installed:
   - If `ELEVENLABS_API_KEY` is missing or `elevenlabs` import fails, run in **print-only** mode.
2. Add clear error messages when roster export is missing or malformed.
3. Add `exports/team_roster.sample.csv` and document expected format.

### Phase 1 — Quality gates (P0)
1. Keep and expand the tests under `tests/`.
2. Ensure CI passes:
   - `ruff check .`
   - `pytest`
3. Add type hints and docstrings to core functions.

### Phase 2 — Refactor for extensibility (P1)
1. Refactor into a package layout (example target):
   - `becky/` (package)
   - `becky/voice.py`, `becky/data.py`, `becky/analysis.py`, `becky/cli.py`
2. Maintain backwards compatibility for the existing entrypoint:
   - `Becky_Assistant_v1.0/launcher.py` should keep working (can become a thin wrapper).

### Phase 3 — Features (P2)
Add a basic intent router (text-first):
- Example intents: analyze roster, show highest salary, show youngest player, help.
- Add a CLI `python -m becky --help`.

## Definition of done
- `pytest` passes locally and in CI.
- No API key is required to run in print-only mode.
- Clear docs for setup + env vars.
- Code is modular and easy to extend with new intents.

## Deliverables in the PR
- Updated source with Phase 0-1 complete (Phase 2+ as time allows).
- Updated docs in README(s).

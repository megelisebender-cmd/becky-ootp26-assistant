# Becky Project

A small Python assistant ("Becky") that reads a baseball roster CSV export and produces a spoken (or printed) summary.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r Becky_Assistant_v1.0/requirements.txt
python Becky_Assistant_v1.0/launcher.py
```

## Environment variables

- `ELEVENLABS_API_KEY` (optional): enables real audio via ElevenLabs. If missing, Becky runs in print-only mode.
- `BECKY_VOICE_ID` (optional): ElevenLabs voice id override.
- `BECKY_ELEVEN_MODEL` (optional): ElevenLabs model override.

## Team roster CSV

Place your export at:

- `Becky_Assistant_v1.0/exports/team_roster.csv`

Expected columns:

- `Name`, `Age`, `Salary`

A sample file is provided:

- `Becky_Assistant_v1.0/exports/team_roster.sample.csv`

## Codex

Start here:

- `codex/PROMPT_FOR_CODEX.md`

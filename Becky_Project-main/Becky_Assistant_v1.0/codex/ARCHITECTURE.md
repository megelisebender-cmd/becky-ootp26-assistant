# Target architecture (proposed)

## Goals
- Separate **domain logic** from **I/O** (voice, CLI).
- Make analyses testable without ElevenLabs.
- Make intents easy to extend.

## Suggested module layout
- `assistant_gm.py`
  - “Orchestrator”: loads config, builds dependencies, runs loop.
- `becky_voice.py`
  - ElevenLabs adapter **only**.
- `io_console.py` (new)
  - Console input/output implementation (default fallback).
- `intents.py` (new)
  - Intent registry + routing (simple keyword/regex to start).
- `baseball/`
  - `analysis.py` (team metrics, roster insights)
  - `models.py` (typed dataclasses for Player, Team)
  - `ootp_exports.py` (robust CSV parsing + validation)
- `config.py` (new)
  - Load env vars / defaults (API key, voice id, export path, no-voice flag)

## Guiding principles
- No network calls in unit tests.
- Voice layer must be optional and injectable.
- Pure functions in analysis modules.

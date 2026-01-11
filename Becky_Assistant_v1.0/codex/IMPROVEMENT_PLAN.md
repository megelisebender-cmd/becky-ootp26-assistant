# Improvement plan (give Codex a concrete backlog)

## P0 — safety + dev-experience (must)
1) **Move secrets to environment**
   - Read `ELEVENLABS_API_KEY` from env (or `.env` if you choose to add it).
   - Never hard-code secrets.
   - If missing, run in `--no-voice` mode and print a clear message.

2) **Add a conversation loop**
   - Becky greets once, then accepts repeated user requests until "quit/exit".
   - Must work in console mode even without microphone/speech recognition.

3) **Intent routing**
   - Implement a minimal intent system:
     - `analyze team`
     - `average age`
     - `payroll`
     - `top salaries` (e.g., top 5)
     - `help`
   - Keyword/regex matching is fine for v1.

4) **Harden CSV parsing**
   - Gracefully handle missing files and missing columns.
   - Robustly parse salary (supports `$`, commas, blanks).
   - Allow passing the export path via CLI flag or config.

## P1 — quality (should)
5) **Introduce typed models**
   - Use `dataclasses` for `Player` (name, age, salary, optional position).
   - Convert `baseball_queries` into pure analysis functions returning strings/objects.

6) **Add unit tests**
   - `pytest` tests for:
     - salary parsing edge cases
     - CSV parsing with missing columns
     - analysis outputs for a small fixture roster

7) **Logging**
   - Replace prints with `logging` (keep prints only for UX if needed).

## P2 — product (nice)
8) **Speech recognition**
   - Optional: integrate an offline or simple STT path.
   - Must keep a fallback to console text input.

9) **Richer OOTP insights**
   - Age curve warnings
   - Positional depth
   - Budget warnings
   - “Players to watch” based on heuristics

## Acceptance criteria
- `python launcher.py` runs without crashing with or without `ELEVENLABS_API_KEY`.
- `pytest` passes.
- All domain logic testable without ElevenLabs.
- Clear CLI `--help` and a `help` intent.

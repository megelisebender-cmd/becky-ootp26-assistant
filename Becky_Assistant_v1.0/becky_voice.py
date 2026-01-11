"""Text-only output for Becky.

This project originally supported optional ElevenLabs speech output.
For the "text-only assistant" version, we intentionally *disable* audio
and always print to stdout.

Keep the public function: `speak(text: str) -> None` so the rest of the
app doesn't have to change.
"""

from __future__ import annotations


def speak(text: str) -> None:
    """Output Becky text to the console."""
    print(f"Becky: {text}")

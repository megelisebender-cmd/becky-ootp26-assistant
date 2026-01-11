"""Bootstrap a Codex perfection scaffold for the Becky repo.

Run from repo root:

    python tools/bootstrap_codex_scaffold.py

This script writes a set of scaffold files (CI, lint/test config, Codex prompt).
It is optional because you can also just commit the files directly.
"""

from __future__ import annotations


# NOTE: This file is intentionally minimal in this scaffold zip.
# If you want a single-script generator that embeds all file contents,
# say so and I'll generate the fully self-contained version.
def main() -> None:
    raise SystemExit(
        "This scaffold zip already contains the final files. "
        "Copy them into your repo and commit."
    )


if __name__ == "__main__":
    main()

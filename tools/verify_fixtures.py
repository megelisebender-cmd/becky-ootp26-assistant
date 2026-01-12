from __future__ import annotations

import subprocess
from pathlib import Path

FIXTURES_SUBDIR = Path("tests/fixtures/ootp_exports_26")


def load_allowlist(allowlist_path: Path) -> list[str]:
    if not allowlist_path.exists():
        raise SystemExit(f"Missing allowlist file: {allowlist_path}")

    entries: list[str] = []
    for line in allowlist_path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        entries.append(s)

    if not entries:
        raise SystemExit(f"Allowlist file is empty: {allowlist_path}")

    return entries


def git_ls_files(repo_root: Path, fixtures_root: Path) -> list[str]:
    rel = fixtures_root.as_posix()
    result = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "--", rel],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"git ls-files failed: {result.stderr.strip()}")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    allowlist_path = repo_root / "tools" / "fixture_allowlist.txt"
    allowlist = load_allowlist(allowlist_path)

    allowlist_set = set(allowlist)

    # Enforce scope: allowlist entries must stay under tests/fixtures/ootp_exports_26/
    prefix = FIXTURES_SUBDIR.as_posix().rstrip("/") + "/"
    bad_scope = sorted([p for p in allowlist if not p.replace("\\\\", "/").startswith(prefix)])
    if bad_scope:
        block = "\n".join(f" - {p}" for p in bad_scope)
        raise SystemExit(
            "Allowlist contains entries outside allowed scope (tests/fixtures/ootp_exports_26/):\n" + block
        )

    tracked = git_ls_files(repo_root, FIXTURES_SUBDIR)
    tracked_set = set(tracked)

    unknown = sorted(tracked_set - allowlist_set)
    if unknown:
        print("Found tracked fixture files not in allowlist:")
        for p in unknown:
            print(f" - {p}")
        print("\nTo fix (example):")
        for p in unknown:
            print(f"git rm --cached -- {p}")
        raise SystemExit(1)

    print(
        f"Fixture verification passed. {len(tracked)} tracked fixture files under ootp_exports_26; {len(allowlist)} allowlisted."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
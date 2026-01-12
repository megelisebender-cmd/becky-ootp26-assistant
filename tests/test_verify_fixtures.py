from __future__ import annotations

from pathlib import Path

import pytest

import tools.verify_fixtures as verify_fixtures


class DummyResult:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _set_repo_root(monkeypatch: pytest.MonkeyPatch, repo_root: Path) -> None:
    tools_dir = repo_root / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    fake_script = tools_dir / "verify_fixtures.py"
    fake_script.write_text("", encoding="utf-8")
    monkeypatch.setattr(verify_fixtures, "__file__", str(fake_script))


def _write_allowlist(repo_root: Path, content: str) -> None:
    allowlist_path = repo_root / "tools" / "fixture_allowlist.txt"
    allowlist_path.write_text(content, encoding="utf-8")


def test_load_allowlist_parsing(tmp_path: Path) -> None:
    allowlist_path = tmp_path / "fixture_allowlist.txt"
    allowlist_path.write_text("\n# comment\n  foo.csv  \n\nbar.csv\n", encoding="utf-8")
    assert verify_fixtures.load_allowlist(allowlist_path) == ["foo.csv", "bar.csv"]


def test_load_allowlist_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"
    with pytest.raises(SystemExit):
        verify_fixtures.load_allowlist(missing)


def test_load_allowlist_empty(tmp_path: Path) -> None:
    allowlist_path = tmp_path / "fixture_allowlist.txt"
    allowlist_path.write_text("\n# comment\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        verify_fixtures.load_allowlist(allowlist_path)


def test_verify_fixtures_passes_with_no_tracked_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _set_repo_root(monkeypatch, tmp_path)
    _write_allowlist(tmp_path, "tests/fixtures/ootp_exports_26/allowed.csv\n")

    def fake_run(*_args: object, **_kwargs: object) -> DummyResult:
        return DummyResult(0, stdout="", stderr="")

    monkeypatch.setattr(verify_fixtures.subprocess, "run", fake_run)
    assert verify_fixtures.main() == 0


def test_verify_fixtures_passes_with_allowlisted_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _set_repo_root(monkeypatch, tmp_path)
    _write_allowlist(tmp_path, "tests/fixtures/ootp_exports_26/allowed.csv\n")

    def fake_run(*_args: object, **_kwargs: object) -> DummyResult:
        stdout = "tests/fixtures/ootp_exports_26/allowed.csv\n"
        return DummyResult(0, stdout=stdout, stderr="")

    monkeypatch.setattr(verify_fixtures.subprocess, "run", fake_run)
    assert verify_fixtures.main() == 0


def test_verify_fixtures_fails_with_unallowlisted_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _set_repo_root(monkeypatch, tmp_path)
    _write_allowlist(tmp_path, "tests/fixtures/ootp_exports_26/allowed.csv\n")

    def fake_run(*_args: object, **_kwargs: object) -> DummyResult:
        stdout = "tests/fixtures/ootp_exports_26/offender.csv\n"
        return DummyResult(0, stdout=stdout, stderr="")

    monkeypatch.setattr(verify_fixtures.subprocess, "run", fake_run)

    with pytest.raises(SystemExit):
        verify_fixtures.main()

    captured = capsys.readouterr()
    assert "Found tracked fixture files not in allowlist:" in captured.out
    assert "git rm --cached -- tests/fixtures/ootp_exports_26/offender.csv" in captured.out


def test_verify_fixtures_fails_when_git_ls_files_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _set_repo_root(monkeypatch, tmp_path)
    _write_allowlist(tmp_path, "tests/fixtures/ootp_exports_26/allowed.csv\n")

    def fake_run(*_args: object, **_kwargs: object) -> DummyResult:
        return DummyResult(1, stdout="", stderr="boom")

    monkeypatch.setattr(verify_fixtures.subprocess, "run", fake_run)

    with pytest.raises(SystemExit) as excinfo:
        verify_fixtures.main()

    assert "git ls-files failed: boom" in str(excinfo.value)


def test_allowlist_scope_enforced(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _set_repo_root(monkeypatch, tmp_path)
    # outside allowed scope should fail
    _write_allowlist(tmp_path, "tests/fixtures/ootp_tables/Teams.csv\n")

    def fake_run(*_args: object, **_kwargs: object) -> DummyResult:
        return DummyResult(0, stdout="", stderr="")

    monkeypatch.setattr(verify_fixtures.subprocess, "run", fake_run)

    with pytest.raises(SystemExit):
        verify_fixtures.main()
import pathlib

import data_adapter


def test_load_team_data_missing_file(tmp_path: pathlib.Path) -> None:
    missing = tmp_path / "nope.csv"
    assert data_adapter.load_team_data(missing) == []


def test_load_team_data_parses_salary_and_fields(tmp_path: pathlib.Path) -> None:
    src = pathlib.Path(__file__).parent / "fixtures" / "team_roster.csv"
    dst = tmp_path / "team_roster.csv"
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    rows = data_adapter.load_team_data(dst)
    assert rows == [
        {"name": "Alice", "age": 25, "salary": 1_000_000},
        {"name": "Bob", "age": 30, "salary": 2_500_000},
    ]

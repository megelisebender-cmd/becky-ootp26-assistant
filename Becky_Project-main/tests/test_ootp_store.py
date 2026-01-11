import pathlib

from ootp.store import ExportStore


def test_store_discovers_csv_tables(tmp_path: pathlib.Path) -> None:
    # Copy fixture CSV into a temp folder
    src = pathlib.Path(__file__).parent / "fixtures" / "ootp_tables" / "Teams.csv"
    (tmp_path / "stats").mkdir()
    dst = tmp_path / "stats" / "Teams.csv"
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    store = ExportStore()
    store.load(tmp_path)
    names = store.table_names()
    assert "stats/Teams" in names

    info = store.get_table_info("stats/Teams")
    assert info is not None
    assert info.path.name == "Teams.csv"

    desc = store.describe("stats/Teams", sample_rows=1)
    assert desc is not None
    assert "teamID" in desc.columns
    assert len(desc.sample) == 1

    rows = store.find_rows("stats/Teams", {"teamID": "CLE"})
    assert rows
    assert rows[0]["name"] == "Cleveland Guardians"

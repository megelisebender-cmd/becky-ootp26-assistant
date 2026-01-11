from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .exports import PathLike, TableInfo, discover_csv_tables, read_csv_rows


@dataclass
class LoadedTable:
    """A lightweight representation of an export table."""

    info: TableInfo
    columns: list[str]
    sample: list[dict[str, str]]


class ExportStore:
    """Discovers and provides access to OOTP export CSVs.

    The goal is to be resilient to differing export setups.
    We discover what's available, expose introspection commands, and only
    provide "GM features" when the necessary data is present.
    """

    def __init__(self) -> None:
        self.root: Path | None = None
        self._tables: dict[str, TableInfo] = {}

    def load(self, root: PathLike) -> None:
        p = Path(root).expanduser()
        self.root = p
        self._tables = {t.name.replace("\\", "/"): t for t in discover_csv_tables(p)}

    def is_loaded(self) -> bool:
        return bool(self._tables)

    def table_names(self) -> list[str]:
        return sorted(k.replace("\\", "/") for k in self._tables.keys())


    def get_table_info(self, name: str) -> TableInfo | None:
        return self._tables.get(name)

    def describe(self, name: str, sample_rows: int = 5) -> LoadedTable | None:
        info = self.get_table_info(name)
        if info is None:
            return None
        sample = read_csv_rows(info.path, limit=sample_rows)
        cols: list[str] = []
        if sample:
            cols = list(sample[0].keys())
        else:
            # Try to read just header
            rows = read_csv_rows(info.path, limit=0)
            cols = list(rows[0].keys()) if rows else []
        return LoadedTable(info=info, columns=cols, sample=sample)

    def read(self, name: str, limit: int | None = None) -> list[dict[str, str]]:
        info = self.get_table_info(name)
        if info is None:
            return []
        return read_csv_rows(info.path, limit=limit)

    def find_rows(
        self,
        name: str,
        contains: dict[str, str],
        limit: int = 25,
    ) -> list[dict[str, str]]:
        """Find rows where each column contains a substring (case-insensitive)."""

        rows = self.read(name)
        if not rows:
            return []

        def ok(row: dict[str, str]) -> bool:
            for col, substr in contains.items():
                v = (row.get(col) or "").lower()
                if substr.lower() not in v:
                    return False
            return True

        out: list[dict[str, str]] = []
        for row in rows:
            if ok(row):
                out.append(row)
                if len(out) >= limit:
                    break
        return out


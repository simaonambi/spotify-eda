"""SQLite access layer for the dashboard."""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from src.load.loader import DEFAULT_DB_PATH
from src.visualization.queries import CuratedQuery


@dataclass(frozen=True)
class QueryResult:
    """Tabular query result."""

    columns: tuple[str, ...]
    rows: tuple[tuple[object, ...], ...]
    elapsed_ms: float


@dataclass(frozen=True)
class SummaryMetric:
    """Single KPI for the dashboard header."""

    label: str
    value: str


class DashboardRepository:
    """Read-only analytical repository backed by SQLite."""

    def __init__(self, database_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.database_path = Path(database_path)

    def fetch_summary(self) -> tuple[SummaryMetric, ...]:
        """Return compact dashboard metrics."""
        return (
            SummaryMetric("Artists", self._scalar("SELECT COUNT(*) FROM dim_artist")),
            SummaryMetric("Tracks", self._scalar("SELECT COUNT(*) FROM dim_track")),
            SummaryMetric("Facts", self._scalar("SELECT COUNT(*) FROM fact_plays")),
            SummaryMetric("Sources", self._scalar("SELECT COUNT(DISTINCT source) FROM fact_plays")),
        )

    def run_query(self, query: CuratedQuery) -> QueryResult:
        """Execute a curated analytical query."""
        started = time.perf_counter()
        with self._connect() as connection:
            cursor = connection.execute(query.sql)
            rows = cursor.fetchall()
            columns = tuple(column[0] for column in cursor.description or ())
        elapsed_ms = (time.perf_counter() - started) * 1000
        return QueryResult(columns=columns, rows=tuple(rows), elapsed_ms=elapsed_ms)

    def _scalar(self, sql: str) -> str:
        """Execute a scalar query and stringify the result."""
        with self._connect() as connection:
            value = connection.execute(sql).fetchone()[0]
        return f"{value:,}"

    def _connect(self) -> sqlite3.Connection:
        """Create a read-only SQLite connection."""
        if not self.database_path.exists():
            raise FileNotFoundError(f"Database not found: {self.database_path}")
        uri = f"file:{self.database_path.as_posix()}?mode=ro"
        connection = sqlite3.connect(uri, uri=True, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

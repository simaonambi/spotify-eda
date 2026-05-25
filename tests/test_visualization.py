"""Smoke tests for the Week 4 visualization layer."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.load.loader import DEFAULT_DB_PATH
from src.visualization.queries import CURATED_QUERIES
from src.visualization.repository import DashboardRepository


def test_curated_queries_return_rows() -> None:
    """Curated queries must execute against the warehouse."""
    repository = DashboardRepository(DEFAULT_DB_PATH)

    for query in CURATED_QUERIES:
        result = repository.run_query(query)
        assert result.columns
        assert result.elapsed_ms >= 0


def test_summary_metrics_are_available() -> None:
    """Top-line dashboard metrics must be readable."""
    repository = DashboardRepository(Path("data/spotify_dw.db"))
    metrics = repository.fetch_summary()
    assert len(metrics) == 4
    assert all(metric.value for metric in metrics)

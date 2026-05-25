"""Integration test for the Week 3 SQLite loader."""

from pathlib import Path
import sqlite3
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.load.loader import load_staging_to_sqlite


def test_load_counts_match_staging(tmp_path: Path) -> None:
    """The DW row counts must match the integrated staging datasets."""
    staging_dir = Path("data/staging")
    db_path = tmp_path / "spotify_dw_test.db"

    tracks_df = pd.read_parquet(staging_dir / "integrated_tracks.parquet")
    artists_df = pd.read_parquet(staging_dir / "integrated_artists.parquet")

    result = load_staging_to_sqlite(staging_dir=staging_dir, db_path=db_path)

    with sqlite3.connect(db_path) as connection:
        counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("dim_artist", "dim_track", "fact_plays")
        }
        fk_violations = connection.execute("PRAGMA foreign_key_check;").fetchall()

    expected_artist_count = len(
        set(artists_df["artist_name"].dropna().astype(str).str.strip())
        | set(tracks_df["artist_name"].dropna().astype(str).str.strip())
    )

    assert result.dim_artist_count == expected_artist_count
    assert result.dim_track_count == tracks_df.drop_duplicates(subset=["track_name", "artist_name"]).shape[0]
    assert result.fact_plays_count == len(tracks_df)
    assert counts["dim_artist"] == result.dim_artist_count
    assert counts["dim_track"] == result.dim_track_count
    assert counts["fact_plays"] == result.fact_plays_count
    assert fk_violations == []

#!/usr/bin/env python3
"""Load staging parquet files into a SQLite star schema."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAGING_DIR = PROJECT_ROOT / "data" / "staging"
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "spotify_dw.db"

TRACKS_FILE = "integrated_tracks.parquet"
ARTISTS_FILE = "integrated_artists.parquet"

REQUIRED_TRACK_COLUMNS = {"track_name", "artist_name", "source"}
REQUIRED_ARTIST_COLUMNS = {"artist_name"}


@dataclass
class LoadResult:
    """Summary of the load execution."""

    dim_artist_count: int
    dim_track_count: int
    fact_plays_count: int
    database_path: Path


class SQLiteStarSchemaLoader:
    """Load staging data into a SQLite dimensional model."""

    def __init__(self, staging_dir: Path | str = STAGING_DIR, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.staging_dir = Path(staging_dir)
        self.db_path = Path(db_path)

    def load(self) -> LoadResult:
        """Execute the complete load process.

        Returns:
            LoadResult: Row counts written to the data warehouse.

        Raises:
            FileNotFoundError: If required staging files are missing.
            ValueError: If required columns are missing.
            sqlite3.DatabaseError: If SQLite operations fail.
        """
        tracks_df, artists_df = self._read_staging_data()
        artist_dim = self._build_artist_dimension(artists_df, tracks_df)
        track_dim = self._build_track_dimension(tracks_df, artist_dim)
        fact_plays = self._build_fact_table(tracks_df, artist_dim, track_dim)

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON;")
            self._create_schema(connection)
            self._load_table(connection, "dim_artist", artist_dim)
            self._load_table(connection, "dim_track", track_dim)
            self._load_table(connection, "fact_plays", fact_plays)
            self._create_indexes(connection)
            violations = connection.execute("PRAGMA foreign_key_check;").fetchall()
            if violations:
                raise sqlite3.IntegrityError(f"Foreign key violations detected: {violations}")
            connection.commit()

        return LoadResult(
            dim_artist_count=len(artist_dim),
            dim_track_count=len(track_dim),
            fact_plays_count=len(fact_plays),
            database_path=self.db_path,
        )

    def _read_staging_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Read and validate required staging datasets."""
        tracks_path = self.staging_dir / TRACKS_FILE
        artists_path = self.staging_dir / ARTISTS_FILE

        if not tracks_path.exists():
            raise FileNotFoundError(f"Missing staging file: {tracks_path}")
        if not artists_path.exists():
            raise FileNotFoundError(f"Missing staging file: {artists_path}")

        tracks_df = pd.read_parquet(tracks_path)
        artists_df = pd.read_parquet(artists_path)

        missing_track_columns = REQUIRED_TRACK_COLUMNS - set(tracks_df.columns)
        missing_artist_columns = REQUIRED_ARTIST_COLUMNS - set(artists_df.columns)
        if missing_track_columns:
            raise ValueError(f"Tracks staging file is missing columns: {sorted(missing_track_columns)}")
        if missing_artist_columns:
            raise ValueError(f"Artists staging file is missing columns: {sorted(missing_artist_columns)}")

        tracks_df = tracks_df.copy()
        artists_df = artists_df.copy()
        tracks_df["track_name"] = tracks_df["track_name"].astype(str).str.strip()
        tracks_df["artist_name"] = tracks_df["artist_name"].astype(str).str.strip()
        artists_df["artist_name"] = artists_df["artist_name"].astype(str).str.strip()

        tracks_df = tracks_df[tracks_df["track_name"].ne("") & tracks_df["artist_name"].ne("")]
        artists_df = artists_df[artists_df["artist_name"].ne("")]

        return tracks_df, artists_df

    def _build_artist_dimension(self, artists_df: pd.DataFrame, tracks_df: pd.DataFrame) -> pd.DataFrame:
        """Create the artist dimension with surrogate keys."""
        artist_columns = [
            "artist_name",
            "artist_id",
            "mbid",
            "followers",
            "listeners",
            "playcount",
            "popularity",
            "genres",
            "tags",
            "bio",
            "source",
            "url",
        ]

        artist_dim = artists_df.copy()
        for column in artist_columns:
            if column not in artist_dim.columns:
                artist_dim[column] = None

        missing_artists = sorted(set(tracks_df["artist_name"]) - set(artist_dim["artist_name"]))
        if missing_artists:
            artist_dim = pd.concat(
                [artist_dim, pd.DataFrame({"artist_name": missing_artists})],
                ignore_index=True,
            )

        artist_dim = artist_dim[artist_columns].drop_duplicates(subset=["artist_name"], keep="first")
        for column in ["followers", "listeners", "playcount", "popularity"]:
            artist_dim[column] = self._to_nullable_int(artist_dim[column])

        artist_dim = artist_dim.sort_values("artist_name").reset_index(drop=True)
        artist_dim.insert(0, "artist_key", range(1, len(artist_dim) + 1))
        return self._sanitize_frame(artist_dim)

    def _build_track_dimension(self, tracks_df: pd.DataFrame, artist_dim: pd.DataFrame) -> pd.DataFrame:
        """Create the track dimension with surrogate keys and artist references."""
        track_columns = [
            "track_name",
            "artist_name",
            "track_id",
            "album_name",
            "release_year",
            "release_date",
            "duration_ms",
            "popularity",
            "source",
            "url",
        ]

        track_dim = tracks_df.copy()
        for column in track_columns:
            if column not in track_dim.columns:
                track_dim[column] = None

        track_dim = track_dim[track_columns].drop_duplicates(subset=["track_name", "artist_name"], keep="first")
        track_dim = track_dim.merge(
            artist_dim[["artist_key", "artist_name"]],
            on="artist_name",
            how="inner",
            validate="many_to_one",
        )
        track_dim["release_year"] = self._coerce_release_year(track_dim["release_year"])
        for column in ["duration_ms", "popularity"]:
            track_dim[column] = self._to_nullable_int(track_dim[column])

        track_dim = track_dim.sort_values(["artist_name", "track_name"]).reset_index(drop=True)
        track_dim.insert(0, "track_key", range(1, len(track_dim) + 1))
        track_dim = track_dim[
            [
                "track_key",
                "artist_key",
                "track_name",
                "track_id",
                "album_name",
                "release_year",
                "release_date",
                "duration_ms",
                "popularity",
                "source",
                "url",
            ]
        ]
        return self._sanitize_frame(track_dim)

    def _build_fact_table(
        self,
        tracks_df: pd.DataFrame,
        artist_dim: pd.DataFrame,
        track_dim: pd.DataFrame,
    ) -> pd.DataFrame:
        """Create the fact table using the integrated tracks dataset."""
        fact_plays = tracks_df.copy()
        fact_plays = fact_plays.merge(
            artist_dim[["artist_key", "artist_name"]],
            on="artist_name",
            how="inner",
            validate="many_to_one",
        )
        fact_plays = fact_plays.merge(
            track_dim[["track_key", "artist_key", "track_name"]],
            on=["track_name", "artist_key"],
            how="inner",
            validate="many_to_one",
        )

        for column in ["playcount", "listeners", "popularity", "duration_ms", "rank", "url"]:
            if column not in fact_plays.columns:
                fact_plays[column] = None

        fact_plays["rank"] = self._to_nullable_int(fact_plays["rank"])
        for column in ["playcount", "listeners", "popularity", "duration_ms"]:
            fact_plays[column] = self._to_nullable_int(fact_plays[column])

        fact_plays = fact_plays.reset_index(drop=True)
        fact_plays.insert(0, "play_key", range(1, len(fact_plays) + 1))
        fact_plays = fact_plays[
            [
                "play_key",
                "track_key",
                "artist_key",
                "source",
                "rank",
                "playcount",
                "listeners",
                "popularity",
                "duration_ms",
                "url",
            ]
        ]
        return self._sanitize_frame(fact_plays)

    def _create_schema(self, connection: sqlite3.Connection) -> None:
        """Recreate the star schema tables."""
        connection.executescript(
            """
            DROP TABLE IF EXISTS fact_plays;
            DROP TABLE IF EXISTS dim_track;
            DROP TABLE IF EXISTS dim_artist;

            CREATE TABLE dim_artist (
                artist_key INTEGER PRIMARY KEY,
                artist_name TEXT NOT NULL UNIQUE,
                artist_id TEXT,
                mbid TEXT,
                followers INTEGER,
                listeners INTEGER,
                playcount INTEGER,
                popularity INTEGER,
                genres TEXT,
                tags TEXT,
                bio TEXT,
                source TEXT,
                url TEXT
            );

            CREATE TABLE dim_track (
                track_key INTEGER PRIMARY KEY,
                artist_key INTEGER NOT NULL,
                track_name TEXT NOT NULL,
                track_id TEXT,
                album_name TEXT,
                release_year INTEGER,
                release_date TEXT,
                duration_ms INTEGER,
                popularity INTEGER,
                source TEXT,
                url TEXT,
                UNIQUE(track_key, artist_key),
                UNIQUE(track_name, artist_key),
                FOREIGN KEY (artist_key) REFERENCES dim_artist (artist_key)
            );

            CREATE TABLE fact_plays (
                play_key INTEGER PRIMARY KEY,
                track_key INTEGER NOT NULL,
                artist_key INTEGER NOT NULL,
                source TEXT NOT NULL,
                rank INTEGER,
                playcount INTEGER,
                listeners INTEGER,
                popularity INTEGER,
                duration_ms INTEGER,
                url TEXT,
                FOREIGN KEY (artist_key) REFERENCES dim_artist (artist_key),
                FOREIGN KEY (track_key, artist_key) REFERENCES dim_track (track_key, artist_key)
            );
            """
        )

    def _load_table(self, connection: sqlite3.Connection, table_name: str, dataframe: pd.DataFrame) -> None:
        """Insert dataframe rows into an existing SQLite table."""
        columns = list(dataframe.columns)
        placeholders = ", ".join(["?"] * len(columns))
        quoted_columns = ", ".join(columns)
        query = f"INSERT INTO {table_name} ({quoted_columns}) VALUES ({placeholders})"
        connection.executemany(query, self._row_iterator(dataframe, columns))

    @staticmethod
    def _create_indexes(connection: sqlite3.Connection) -> None:
        """Create analytical indexes for dashboard queries."""
        connection.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_artist_name ON dim_artist (artist_name);
            CREATE INDEX IF NOT EXISTS idx_track_artist_name ON dim_track (artist_key, track_name);
            CREATE INDEX IF NOT EXISTS idx_fact_source ON fact_plays (source);
            CREATE INDEX IF NOT EXISTS idx_fact_artist ON fact_plays (artist_key);
            CREATE INDEX IF NOT EXISTS idx_fact_track ON fact_plays (track_key);
            """
        )

    @staticmethod
    def _row_iterator(dataframe: pd.DataFrame, columns: list[str]) -> Iterable[tuple]:
        """Yield rows as tuples suitable for SQLite inserts."""
        for row in dataframe[columns].itertuples(index=False, name=None):
            yield row

    @staticmethod
    def _to_nullable_int(series: pd.Series) -> pd.Series:
        """Convert numeric values to nullable integer dtype."""
        return pd.to_numeric(series, errors="coerce").round().astype("Int64")

    @staticmethod
    def _coerce_release_year(series: pd.Series) -> pd.Series:
        """Extract a 4-digit year when available."""
        extracted = series.astype("string").str.extract(r"(?P<year>\d{4})")["year"]
        return pd.to_numeric(extracted, errors="coerce").astype("Int64")

    @staticmethod
    def _sanitize_frame(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Replace pandas missing values with Python None for SQLite compatibility."""
        return dataframe.astype(object).where(pd.notna(dataframe), None)


def load_staging_to_sqlite(
    staging_dir: Path | str = STAGING_DIR,
    db_path: Path | str = DEFAULT_DB_PATH,
) -> LoadResult:
    """Public helper to run the SQLite load."""
    loader = SQLiteStarSchemaLoader(staging_dir=staging_dir, db_path=db_path)
    return loader.load()


def main() -> None:
    """CLI entrypoint for the load stage."""
    result = load_staging_to_sqlite()
    print("WEEK 3 LOAD COMPLETE")
    print(f"dim_artist: {result.dim_artist_count}")
    print(f"dim_track: {result.dim_track_count}")
    print(f"fact_plays: {result.fact_plays_count}")
    print(f"database: {result.database_path}")


if __name__ == "__main__":
    main()

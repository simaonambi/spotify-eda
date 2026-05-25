"""Curated analytical queries for the dashboard."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CuratedQuery:
    """Immutable curated query definition."""

    key: str
    title: str
    description: str
    sql: str


CURATED_QUERIES = (
    CuratedQuery(
        key="artist_momentum",
        title="Artist Momentum",
        description="Highest cumulative playcount across all sources.",
        sql="""
        SELECT
            a.artist_name,
            COUNT(*) AS appearances,
            SUM(COALESCE(f.playcount, 0)) AS total_playcount,
            SUM(COALESCE(f.listeners, 0)) AS total_listeners
        FROM fact_plays AS f
        JOIN dim_artist AS a ON a.artist_key = f.artist_key
        GROUP BY a.artist_key, a.artist_name
        ORDER BY total_playcount DESC, total_listeners DESC
        LIMIT 15;
        """,
    ),
    CuratedQuery(
        key="track_reach",
        title="Track Reach",
        description="Tracks with the strongest listener footprint.",
        sql="""
        SELECT
            t.track_name,
            a.artist_name,
            SUM(COALESCE(f.listeners, 0)) AS total_listeners,
            MAX(COALESCE(f.popularity, 0)) AS peak_popularity
        FROM fact_plays AS f
        JOIN dim_track AS t ON t.track_key = f.track_key
        JOIN dim_artist AS a ON a.artist_key = f.artist_key
        GROUP BY t.track_key, t.track_name, a.artist_name
        ORDER BY total_listeners DESC, peak_popularity DESC
        LIMIT 15;
        """,
    ),
    CuratedQuery(
        key="source_mix",
        title="Source Mix",
        description="Operational view of volume and signal by upstream source.",
        sql="""
        SELECT
            f.source,
            COUNT(*) AS rows_loaded,
            SUM(COALESCE(f.playcount, 0)) AS total_playcount,
            AVG(COALESCE(f.listeners, 0)) AS avg_listeners
        FROM fact_plays AS f
        GROUP BY f.source
        ORDER BY rows_loaded DESC;
        """,
    ),
    CuratedQuery(
        key="catalog_timeline",
        title="Catalog Timeline",
        description="Release cadence for tracks with explicit release years.",
        sql="""
        SELECT
            t.release_year,
            COUNT(*) AS tracks_released,
            AVG(COALESCE(t.popularity, 0)) AS avg_popularity
        FROM dim_track AS t
        WHERE t.release_year IS NOT NULL
        GROUP BY t.release_year
        ORDER BY t.release_year DESC
        LIMIT 20;
        """,
    ),
)


def query_map() -> dict[str, CuratedQuery]:
    """Return curated queries keyed by identifier."""
    return {query.key: query for query in CURATED_QUERIES}

# Spotify EDA

Professional ETL pipeline for Spotify-adjacent public data. The project is organized as four deliberate steps: extract only what matters, normalize it once, load it into a dimensional model, and expose it through a single analytical surface.

Status: WEEK 4 COMPLETE

---

## Why This Architecture

The project uses a narrow data path because analytical systems degrade when every layer invents its own truth.

- Week 1 captures raw source fidelity in parquet.
- Week 2 standardizes and integrates records into staging outputs with explicit lineage.
- Week 3 loads a SQLite star schema so analytical joins are predictable and referential integrity is enforced.
- Week 4 keeps the dashboard read-only, curated and asynchronous so the UI never becomes an operational bottleneck.

The design goal is simple: one warehouse, one pane of glass, one set of curated questions.

---

## Project Status

| Week | Phase | Status | Output |
|------|-------|--------|--------|
| 1 | Extraction | COMPLETE | 8 raw parquet files |
| 2 | Transformation | COMPLETE | 18 staging parquet files |
| 3 | Load | COMPLETE | `data/spotify_dw.db` |
| 4 | Visualization | COMPLETE | Tkinter dashboard |

---

## Week 4

### Intent

Week 4 is not a generic GUI layer. It exists to reduce analytical friction:

- the dashboard is a single control surface
- the SQL console is curated, not open-ended
- every database read runs off the UI thread
- progress feedback lives inside the interface, not in noisy terminal output

### Delivery

- `dashboard/app.py`: launcher
- `src/visualization/queries.py`: high-value analytical SQL catalog
- `src/visualization/repository.py`: read-only SQLite access layer
- `src/visualization/services.py`: background execution for non-blocking I/O
- `src/visualization/ui.py`: Swiss-style Tkinter interface

### Curated Views

- `Artist Momentum`: cumulative playcount and listener weight by artist
- `Track Reach`: strongest listener footprint by track
- `Source Mix`: operational volume by upstream source
- `Catalog Timeline`: release cadence and popularity over time

---

## Data Model

The warehouse is a compact star schema.

### `dim_artist`

- Grain: one artist
- Key: `artist_key`
- Purpose: stable descriptive context for artist-level analysis

### `dim_track`

- Grain: one unique `(track_name, artist_name)`
- Key: `track_key`
- Purpose: track-level descriptive context tied to a single artist

### `fact_plays`

- Grain: one integrated play observation
- Key: `play_key`
- Purpose: measures such as `playcount`, `listeners`, `rank`, `popularity` and `duration_ms`

Foreign keys are enforced, and analytical indexes are created during load so the dashboard does not rely on full-table scans for common aggregations.

---

## Layout

```text
src/
  extract/
  transform/
  load/
  visualization/

dashboard/
  app.py

data/
  raw/
  staging/
  spotify_dw.db
```

---

## Run

### 1. Transformation

```bash
python -m src.transform.Week2_orchestrator
```

### 2. Load

```bash
python -m src.load.loader
```

### 3. Dashboard

```bash
python dashboard/app.py
```

---

## Verification

The repository includes narrow tests for the warehouse and the visualization access layer.

```bash
pytest tests/test_load.py tests/test_visualization.py
```

What this proves:

- row counts loaded from staging match warehouse counts
- foreign key integrity holds
- curated analytical queries execute successfully
- top-line dashboard metrics are available from the warehouse

---

## Current Outputs

- `dim_artist`: 218 rows
- `dim_track`: 521 rows
- `fact_plays`: 521 rows
- `sources`: 3 distinct upstream source labels

---

## Design Notes

The interface follows a high-contrast monochrome system with restrained typography and spacing. The point is not decoration. The point is to make the query, the result and the system state legible at a glance.

Less is more only works when the underlying structure is rigorous.

---

Last Updated: May 25, 2026  
Version: 4.0.0 - Week 4 Complete

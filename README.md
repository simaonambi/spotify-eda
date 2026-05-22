# Spotify EDA - Exploratory Data Analysis Pipeline

Exploratory Data Analysis of Spotify music data, integrating multiple public data sources with a professional ETL pipeline.

Status: WEEK 2 COMPLETE

---

## Project Status

| Week | Phase | Status | Records | Files |
|------|-------|--------|---------|-------|
| 1 | EXTRACTION | COMPLETE | 750 | 8 (raw) |
| 2 | TRANSFORMATION | COMPLETE | 750 | 18 (staged) |
| 3 | LOAD | PLANNED | - | DB |
| 4 | VISUALIZATION | PLANNED | - | Dashboard |

---

## Week 2 Summary

### Implemented Features

- Cleaning (cleaning.py): Removes nulls and duplicates
- Normalization (normalization.py): Standardizes text, dates, numbers
- Integration (week2_orchestrator.py): Combines 3 data sources
- Validation: Verifies data quality
- Reporting: Generates JSON quality report

### Week 2 Results

| Metric | Value |
|--------|-------|
| Datasets Cleaned | 8 |
| Datasets Normalized | 8 |
| Integrated Tracks (unique) | 100+ |
| Integrated Artists (unique) | 50+ |
| Validation Status | PASSED |
| Execution Time | 5-10 seconds |

---

## Architecture

### Folder Structure

```
spotify-eda/
|
+-- src/
|   |
|   +-- extract/              (Week 1 - COMPLETE)
|   |   |-- main_extract.py
|   |   |-- spotify_crawler.py
|   |   |-- spotify_charts.py
|   |   +-- lastfm_api.py
|   |
|   +-- transform/            (Week 2 - COMPLETE)
|   |   |-- __init__.py
|   |   |-- cleaning.py              (150 lines)
|   |   +-- normalization.py         (120 lines)
|   |
|   +-- orchestration/        (Week 2 - COMPLETE)
|   |   |-- __init__.py
|   |   +-- week2_orchestrator.py    (280 lines)
|   |
|   +-- config/               (Week 1 - COMPLETE)
|       |-- config.py
|       +-- logging_config.py
|
+-- data/
|   |
|   +-- raw/                  (Week 1 OUTPUT - 8 files)
|   |   |-- spotify_tracks.parquet
|   |   |-- spotify_artists.parquet
|   |   |-- spotify_playlists.parquet
|   |   |-- spotify_charts_tracks.parquet
|   |   |-- spotify_charts_artists.parquet
|   |   |-- spotify_charts_playlists.parquet
|   |   |-- lastfm_top_tracks.parquet
|   |   +-- lastfm_artists.parquet
|   |
|   +-- staging/              (Week 2 OUTPUT - 18 files)
|       |-- clean_*.parquet (8 files - cleaned data)
|       |-- norm_*.parquet (8 files - normalized data)
|       |-- integrated_tracks.parquet
|       +-- integrated_artists.parquet
|
+-- reports/                  (Week 2 OUTPUT)
|   +-- week2_quality_report.json
|
+-- requirements.txt
+-- README.md
+-- .gitignore
```

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip or conda
- Virtual environment (recommended)

### Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Execution

### Week 1: Data Extraction (Complete)

```bash
python src/extract/main_extract.py
```

Output: 8 Parquet files in `data/raw/` (750 records, 94.1 KB)

### Week 2: Data Transformation (Complete)

```bash
python src/orchestration/week2_orchestrator.py
```

This executes the complete pipeline:
1. Cleaning (removes nulls and duplicates)
2. Normalization (standardizes values)
3. Integration (combines 3 sources)
4. Validation (checks data quality)
5. Report Generation (JSON output)

Execution time: 5-10 seconds

Expected output:

```
======================================================================
SPOTIFY EDA - WEEK 2 COMPLETE
Clean -> Normalize -> Integrate -> Validate
======================================================================

STEP 1/4: CLEANING
CLEANING DONE: 8 datasets cleaned

STEP 2/4: NORMALIZATION
NORMALIZATION DONE: 8 datasets normalized

STEP 3/4: INTEGRATION
Result: 100+ unique tracks, 50+ unique artists

STEP 4/4: VALIDATION & REPORTS
All validations passed!
Report saved: reports/week2_quality_report.json

======================================================================
WEEK 2 COMPLETE
======================================================================

Output files: data/staging/ (18 files)
Report: reports/week2_quality_report.json
```

---

## Week 2 Modules

### 1. cleaning.py (150 lines)

Purpose: Remove nulls, duplicates, standardize data types

Class: DataCleaner

Methods:
- clean_tracks(df) - Cleans track data
- clean_artists(df) - Cleans artist data
- clean_playlists(df) - Cleans playlist data

Features:
- Removes rows with null values in critical fields
- Removes duplicate records (by ID or name)
- Converts data types (string to int, float)
- Replaces special values ('N/A', 'unknown', etc)

### 2. normalization.py (120 lines)

Purpose: Standardize text, dates, numbers

Class: DataNormalizer

Methods:
- normalize_text_fields(df) - Lowercase, trim, remove spaces
- normalize_dates(df) - Convert to ISO 8601 format
- normalize_numeric(df) - Standardize numeric types
- clamp_values(df) - Restrict to valid ranges

Features:
- Converts text to lowercase
- Removes extra spaces (trim, multiple spaces)
- Formats dates to YYYY-MM-DD
- Converts numerics to int64/float64
- Clamps popularity [0-100], duration [0-infinity]

### 3. week2_orchestrator.py (280 lines)

Purpose: Orchestrate complete transformation pipeline

Class: Week2Orchestrator

Executes:
1. Cleaning (8 datasets)
2. Normalization (8 datasets)
3. Integration (3 sources to 2 unified datasets)
4. Validation (quality checks)
5. Report generation (JSON)

Output:
- data/staging/clean_*.parquet (8 files)
- data/staging/norm_*.parquet (8 files)
- data/staging/integrated_tracks.parquet
- data/staging/integrated_artists.parquet
- reports/week2_quality_report.json

---

## Data Schema

### Tracks (After Normalization)

```
track_id: str                   # Unique identifier
track_name: str                 # Song name (lowercase, trimmed)
artist_name: str                # Artist name (lowercase, trimmed)
album_name: str                 # Album name
release_year: int64             # Release year [1900-2030]
popularity: int64               # Score [0-100] (clamped)
duration_ms: int64              # Duration in milliseconds [0-infinity]
playcount: int64                # Play count
listeners: int64                # Global listeners
source: str                     # Origin (spotify, charts, lastfm)
```

### Artists (After Normalization)

```
artist_id: str                  # Unique identifier
artist_name: str                # Name (lowercase, trimmed)
followers: int64                # Number of followers
popularity: int64               # Score [0-100] (clamped)
genres: str                     # Genres (comma-separated, lowercase)
playcount: int64                # Total plays
listeners: int64                # Total listeners
source: str                     # Origin
```

---

## Data Validation

### Applied Rules

| Field | Rule | Action if Failed |
|-------|------|------------------|
| track_name | NOT NULL | DROPPED |
| artist_name | NOT NULL | DROPPED |
| track_id | UNIQUE | REMOVED DUPLICATES |
| popularity | [0, 100] | CLAMPED |
| duration_ms | [0, infinity] | CLAMPED |

Status: ALL VALIDATIONS PASSED

---

## Week 2 Statistics

### Cleaning

- Nulls removed: 0-5 per dataset
- Duplicates removed: 0-10 per dataset
- Types standardized: 100%

### Normalization

- Text normalized: 100%
- Dates formatted: ISO 8601
- Numbers converted: 100%
- Values clamped: Popularity [0-100], Duration [0-infinity]

### Integration

- Track sources: Spotify (8), Charts (100), Last.fm (500)
- Unique tracks: 100+
- Duplicates removed: 5-10
- Artist sources: Spotify (8), Charts (49), Last.fm (50)
- Unique artists: 50+

---

## Quick Tests

```bash
# Test cleaning
python << 'EOF'
import pandas as pd
df = pd.read_parquet('data/staging/clean_spotify_tracks.parquet')
print(f"Records: {len(df)}")
print(f"Nulls: {df.isnull().sum().sum()}")
print(f"Duplicates: {df.duplicated().sum()}")
EOF

# Test normalization
python << 'EOF'
import pandas as pd
df = pd.read_parquet('data/staging/norm_spotify_tracks.parquet')
print(f"Records: {len(df)}")
print(f"Lowercase: {df['track_name'].str.islower().all()}")
print(df.head())
EOF

# Test integration
python << 'EOF'
import pandas as pd
tracks = pd.read_parquet('data/staging/integrated_tracks.parquet')
print(f"Integrated tracks: {len(tracks)}")
print(f"Sources: {tracks['source'].unique()}")
artists = pd.read_parquet('data/staging/integrated_artists.parquet')
print(f"Integrated artists: {len(artists)}")
EOF

# View report
python << 'EOF'
import json
with open('reports/week2_quality_report.json') as f:
    report = json.load(f)
    print(json.dumps(report, indent=2))
EOF
```

---

## Technical Decisions

### 1. Duplicate Removal Strategy
REMOVED (keep='first'): Keep first occurrence, remove rest
Rationale: Simplicity and traceability

### 2. Missing Values Strategy
DROPPED: Remove rows with nulls in critical fields
Rationale: Critical data cannot be estimated

### 3. Source Integration Strategy
MERGE WITH DEDUPLICATION: Combine 3 sources, remove exact duplicates
Key for tracks: (track_name, artist_name)
Key for artists: (artist_name)
Strategy: Keep first occurrence per source

### 4. Validation Approach
CUSTOM RULES: Validation in pure Python
Rationale: Simple, no extra dependencies

---

## Generated Files (Week 2)

### Cleaned Data (8 files)

```
data/staging/
|-- clean_spotify_tracks.parquet (8 records)
|-- clean_spotify_artists.parquet (8 records)
|-- clean_spotify_playlists.parquet (5 records)
|-- clean_spotify_charts_tracks.parquet (100 records)
|-- clean_spotify_charts_artists.parquet (49 records)
|-- clean_spotify_charts_playlists.parquet (30 records)
|-- clean_lastfm_top_tracks.parquet (500 records)
+-- clean_lastfm_artists.parquet (50 records)
```

### Normalized Data (8 files)

```
data/staging/
|-- norm_spotify_tracks.parquet (8 records)
|-- norm_spotify_artists.parquet (8 records)
|-- norm_spotify_playlists.parquet (5 records)
|-- norm_spotify_charts_tracks.parquet (100 records)
|-- norm_spotify_charts_artists.parquet (49 records)
|-- norm_spotify_charts_playlists.parquet (30 records)
|-- norm_lastfm_top_tracks.parquet (500 records)
+-- norm_lastfm_artists.parquet (50 records)
```

### Integrated Data (2 files)

```
data/staging/
|-- integrated_tracks.parquet (100+ unique records)
+-- integrated_artists.parquet (50+ unique records)
```

### Quality Report (1 file)

```
reports/
+-- week2_quality_report.json
```

Total: 18 staging files + 1 report

---

## Next Steps - Week 3 (LOAD)

Planned for next week:

1. Create data warehouse schema (star schema)
2. Implement loader for SQLite or PostgreSQL
3. Create tables: dim_artist, dim_track, fact_plays
4. Validate referential integrity

Expected output:
- Database with 3 tables
- Data quality checks
- Indexes and constraints

---

## Git Workflow

Commit Week 2 changes:

```bash
git add -A
git commit -m "feat: complete week 2 transformation (clean, normalize, integrate, validate)"
git push
```

Recommended commits:

```bash
git commit -m "feat: add cleaning module"
git commit -m "feat: add normalization module"
git commit -m "feat: add week2 orchestrator"
git commit -m "docs: update readme with week 2"
```

---

## Final Metrics (Week 1 + Week 2)

| Metric | Week 1 | Week 2 | Total |
|--------|--------|--------|-------|
| Time | 87.8s | 5-10s | ~95s |
| Files | 8 | 18 | 26 |
| Records | 750 | 750 | 750 |
| Size | 94.1 KB | ~50 KB | ~144 KB |
| Validation | Basic | Complete | PASSED |

---

## Team

- Simao Nambi (ID: 53558) - Lead Developer
- Tiago Neto (ID: a54172) - QA and Validation
- Institution: Universidade da Beira Interior (UBI), Covilha

---

## License

Educational project for Engenharia de Dados e Transformacao (ETL) course.

---

## Executive Summary

Spotify EDA is a professional ETL pipeline that:

COMPLETE - Week 1: Extracts 750 records from 3 public sources (87.8s)
COMPLETE - Week 2: Cleans, normalizes, integrates and validates data (5-10s)
PLANNED - Week 3: Load to data warehouse (next week)
PLANNED - Week 4: Visualization with dashboards and BI

Current Status: Week 1 + Week 2 COMPLETE

Next: Week 3 (Load to Database)

---

Last Updated: May 22, 2026
Version: 2.0.0 - Week 2 Complete
Status: READY FOR WEEK 3
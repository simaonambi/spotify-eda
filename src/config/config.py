#!/usr/bin/env python3
# src/config/config.py
"""
Configuration module for Spotify EDA project
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_PATH = str(DATA_DIR / "raw")
STAGING_PATH = str(DATA_DIR / "staging")
CURATED_PATH = str(DATA_DIR / "curated")
DOWNLOADS_PATH = str(DATA_DIR / "downloads")

# Create directories if they don't exist
for directory in [RAW_DATA_PATH, STAGING_PATH, CURATED_PATH, DOWNLOADS_PATH]:
    Path(directory).mkdir(parents=True, exist_ok=True)

# Database configuration
DB_PATH = os.getenv("DB_PATH", str(PROJECT_ROOT / "spotify.db"))

# Spotify API configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

# Last.fm API configuration
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_API_SECRET = os.getenv("LASTFM_API_SECRET")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = str(LOG_DIR / "spotify_eda.log")

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# API Configuration
API_RATE_LIMIT_DELAY = 0.5  # seconds
BATCH_SIZE = 50
REQUEST_TIMEOUT = 10  # seconds

# Data extraction configuration
SPOTIFY_TRACKS_LIMIT = 50
SPOTIFY_ARTISTS_LIMIT = 20
MPD_SAMPLE_SIZE = 1000  # Use sample for quick testing, set to None for full dataset
LASTFM_TRACKS_LIMIT = 500
LASTFM_ARTISTS_SAMPLE = True

# Display configuration
pd_display_max_columns = None
pd_display_max_rows = None

if __name__ == "__main__":
    print("Configuration loaded successfully!")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Raw data path: {RAW_DATA_PATH}")
    print(f"Staging path: {STAGING_PATH}")
    print(f"Curated path: {CURATED_PATH}")
    print(f"Log file: {LOG_FILE}")
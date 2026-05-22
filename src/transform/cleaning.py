#!/usr/bin/env python3
# src/transform/cleaning.py
"""
Data Cleaning Module for Spotify EDA - Week 2 - Day 1
Remove nulls, duplicates, standardize types
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict


class DataCleaner:
    """Clean raw data: remove nulls, duplicates, standardize types"""
    
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.stats = {}
    
    def clean_tracks(self, df):
        """Remove nulls/duplicates from tracks"""
        print("\n  🧹 Cleaning tracks...")
        initial = len(df)
        
        # Remove nulls
        df = df.dropna(subset=['track_name', 'artist_name'], how='any')
        nulls = initial - len(df)
        if nulls > 0:
            print(f"     ✓ Removed {nulls} rows with null values")
        
        # Remove duplicates
        before_dup = len(df)
        df = df.drop_duplicates(subset=['track_id'] if 'track_id' in df.columns else ['track_name', 'artist_name'], keep='first')
        dupes = before_dup - len(df)
        if dupes > 0:
            print(f"     ✓ Removed {dupes} duplicate rows")
        
        # Standardize types
        for col in ['playcount', 'listeners', 'duration_ms', 'popularity', 'release_year']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
        
        print(f"     ✅ Final: {len(df)} records (removed {initial - len(df)})")
        return df
    
    def clean_artists(self, df):
        """Remove nulls/duplicates from artists"""
        print("\n  🧹 Cleaning artists...")
        initial = len(df)
        
        # Remove nulls
        df = df.dropna(subset=['artist_name'], how='any')
        nulls = initial - len(df)
        if nulls > 0:
            print(f"     ✓ Removed {nulls} rows with null values")
        
        # Remove duplicates
        before_dup = len(df)
        df = df.drop_duplicates(subset=['artist_name'], keep='first')
        dupes = before_dup - len(df)
        if dupes > 0:
            print(f"     ✓ Removed {dupes} duplicate rows")
        
        # Standardize types
        for col in ['followers', 'playcount', 'listeners', 'popularity']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
        
        print(f"     ✅ Final: {len(df)} records (removed {initial - len(df)})")
        return df
    
    def clean_playlists(self, df):
        """Remove nulls/duplicates from playlists"""
        print("\n  🧹 Cleaning playlists...")
        initial = len(df)
        
        # Remove nulls
        df = df.dropna(subset=['playlist_name'], how='any')
        nulls = initial - len(df)
        if nulls > 0:
            print(f"     ✓ Removed {nulls} rows with null values")
        
        # Remove duplicates
        before_dup = len(df)
        df = df.drop_duplicates(subset=['playlist_id'] if 'playlist_id' in df.columns else ['playlist_name'], keep='first')
        dupes = before_dup - len(df)
        if dupes > 0:
            print(f"     ✓ Removed {dupes} duplicate rows")
        
        # Standardize types
        for col in ['num_tracks', 'followers']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
        
        print(f"     ✅ Final: {len(df)} records (removed {initial - len(df)})")
        return df


def clean_all_data(raw_path='data/raw', output_path='data/staging'):
    """
    Clean all raw data files
    
    Usage:
        cleaned = clean_all_data('data/raw', 'data/staging')
    """
    
    print("\n" + "="*70)
    print("🧹 DAY 1: DATA CLEANING")
    print("="*70)
    
    cleaner = DataCleaner(verbose=True)
    cleaned_data = {}
    raw_p = Path(raw_path)
    
    if not raw_p.exists():
        print(f"❌ Error: {raw_path} not found")
        return cleaned_data
    
    print(f"\n[LOADING] Files from {raw_path}...")
    
    files = {
        'spotify_tracks': 'tracks',
        'spotify_artists': 'artists',
        'spotify_playlists': 'playlists',
        'spotify_charts_tracks': 'tracks',
        'spotify_charts_artists': 'artists',
        'spotify_charts_playlists': 'playlists',
        'lastfm_top_tracks': 'tracks',
        'lastfm_artists': 'artists',
    }
    
    for name, dtype in files.items():
        filepath = raw_p / f"{name}.parquet"
        if not filepath.exists():
            continue
        
        try:
            df = pd.read_parquet(filepath)
            print(f"  ✓ {name}: {len(df)} records")
            
            if dtype == 'tracks':
                df = cleaner.clean_tracks(df)
            elif dtype == 'artists':
                df = cleaner.clean_artists(df)
            else:
                df = cleaner.clean_playlists(df)
            
            cleaned_data[name] = df
        
        except Exception as e:
            print(f"  ❌ Error loading {name}: {e}")
    
    # Save
    if cleaned_data:
        print(f"\n[SAVING] to {output_path}...")
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        for name, df in cleaned_data.items():
            out_file = Path(output_path) / f"clean_{name}.parquet"
            df.to_parquet(out_file, index=False, compression='snappy')
            print(f"  ✓ {out_file.name} ({len(df)} records)")
    
    print("\n" + "="*70)
    print(f"✅ CLEANING DONE: {len(cleaned_data)} datasets cleaned")
    print("="*70)
    
    return cleaned_data


if __name__ == "__main__":
    cleaned = clean_all_data('data/raw', 'data/staging')
    print(f"\n✓ Ready for next step: Normalization")
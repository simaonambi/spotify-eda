#!/usr/bin/env python3
# src/transform/normalization.py
"""
Data Normalization Module for Spotify EDA - Week 2 - Day 2
Normalize: text, dates, numbers, genres
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, List


class DataNormalizer:
    """Normalize data: lowercase, trim, format dates, clamp values"""
    
    def __init__(self, verbose=True):
        self.verbose = verbose
    
    @staticmethod
    def normalize_text(text):
        """Lowercase, trim, remove extra spaces"""
        if pd.isna(text) or text is None:
            return None
        text = str(text).strip()
        text = re.sub(r'\s+', ' ', text)
        return text.lower()
    
    def normalize_text_fields(self, df, columns=None):
        """Apply text normalization to columns"""
        if columns is None:
            columns = df.select_dtypes(include='object').columns.tolist()
        
        for col in columns:
            if col in df.columns:
                df[col] = df[col].apply(self.normalize_text)
        
        return df
    
    def normalize_dates(self, df):
        """Convert dates to ISO 8601 format"""
        for col in df.columns:
            if 'year' in col.lower() or 'date' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
                except:
                    pass
        return df
    
    def normalize_numeric(self, df):
        """Standardize numeric types"""
        for col in df.columns:
            if any(k in col.lower() for k in ['count', 'followers', 'popularity', 'duration']):
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
        return df
    
    def clamp_values(self, df):
        """Clamp values to valid ranges"""
        # Clamp popularity to 0-100
        if 'popularity' in df.columns:
            df['popularity'] = df['popularity'].clip(0, 100)
        
        # Clamp duration to positive
        if 'duration_ms' in df.columns:
            df['duration_ms'] = df['duration_ms'].clip(lower=0)
        
        return df


def normalize_all_data(input_path='data/staging', output_path='data/staging'):
    """
    Normalize all cleaned data
    
    Usage:
        normalize_all_data('data/staging', 'data/staging')
    """
    
    print("\n" + "="*70)
    print("🎯 DAY 2: DATA NORMALIZATION")
    print("="*70)
    
    normalizer = DataNormalizer()
    normalized_data = {}
    input_p = Path(input_path)
    
    if not input_p.exists():
        print(f"❌ Error: {input_path} not found")
        return normalized_data
    
    print(f"\n[LOADING] Files from {input_path}...")
    
    # Find all clean_*.parquet files
    for filepath in sorted(input_p.glob('clean_*.parquet')):
        name = filepath.stem.replace('clean_', '')
        
        try:
            df = pd.read_parquet(filepath)
            print(f"  ✓ {name}: {len(df)} records")
            
            print(f"\n  🎯 Normalizing {name}...")
            
            # Normalize text fields
            df = normalizer.normalize_text_fields(df)
            print(f"     ✓ Normalized text fields")
            
            # Normalize dates
            df = normalizer.normalize_dates(df)
            print(f"     ✓ Normalized dates")
            
            # Normalize numeric
            df = normalizer.normalize_numeric(df)
            print(f"     ✓ Normalized numeric types")
            
            # Clamp values
            df = normalizer.clamp_values(df)
            print(f"     ✓ Clamped values to valid ranges")
            
            print(f"      Final: {len(df)} records")
            
            normalized_data[name] = df
        
        except Exception as e:
            print(f"   Error: {e}")
    
    # Save
    if normalized_data:
        print(f"\n[SAVING] to {output_path}...")
        
        for name, df in normalized_data.items():
            out_file = Path(output_path) / f"norm_{name}.parquet"
            df.to_parquet(out_file, index=False, compression='snappy')
            print(f"  ✓ {out_file.name} ({len(df)} records)")
    
    print("\n" + "="*70)
    print(f" NORMALIZATION DONE: {len(normalized_data)} datasets normalized")
    print("="*70)
    
    return normalized_data


if __name__ == "__main__":
    normalized = normalize_all_data('data/staging', 'data/staging')
    print(f"\n✓ Ready for next step: Integration")
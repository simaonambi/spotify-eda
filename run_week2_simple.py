#!/usr/bin/env python3
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import pandas as pd
import json
from src.transform.cleaning import clean_all_data as clean
from src.transform.normalization import normalize_all_data as normalize


class DataIntegrator:
    @staticmethod
    def integrate_tracks(normalized_data):
        print("\n" + "="*70)
        print("STEP 3/4: DATA INTEGRATION")
        print("="*70)
        print("\n  Integrating tracks from 3 sources...")
        
        all_tracks = []
        for source_name, df in normalized_data.items():
            if 'track' in source_name and 'artist' not in source_name:
                df['source'] = source_name.replace('spotify_charts_', 'charts_').replace('lastfm_top_', 'lastfm_')
                all_tracks.append(df)
        
        if all_tracks:
            integrated = pd.concat(all_tracks, ignore_index=True)
            before = len(integrated)
            integrated = integrated.drop_duplicates(subset=['track_name', 'artist_name'], keep='first')
            removed = before - len(integrated)
            
            print(f"     OK Combined {len(all_tracks)} sources")
            print(f"     OK Removed {removed} exact duplicates")
            print(f"     OK Result: {len(integrated)} unique tracks")
            return integrated
        
        return pd.DataFrame()
    
    @staticmethod
    def integrate_artists(normalized_data):
        print("\n  Integrating artists from 3 sources...")
        all_artists = []
        
        for source_name, df in normalized_data.items():
            if 'artist' in source_name:
                df['source'] = source_name.replace('spotify_charts_', 'charts_').replace('lastfm_', 'lastfm_')
                all_artists.append(df)
        
        if all_artists:
            integrated = pd.concat(all_artists, ignore_index=True)
            before = len(integrated)
            integrated = integrated.drop_duplicates(subset=['artist_name'], keep='first')
            removed = before - len(integrated)
            
            print(f"     OK Combined {len(all_artists)} sources")
            print(f"     OK Removed {removed} exact duplicates")
            print(f"     OK Result: {len(integrated)} unique artists")
            return integrated
        
        return pd.DataFrame()


class DataValidator:
    @staticmethod
    def validate_tracks(df):
        print("\n" + "="*70)
        print("STEP 4/4: DATA VALIDATION & REPORTS")
        print("="*70)
        print("\n  Validating tracks...")
        
        issues = []
        null_track = df['track_name'].isnull().sum()
        null_artist = df['artist_name'].isnull().sum()
        
        if null_track > 0:
            issues.append(f"Found {null_track} null track names")
        if null_artist > 0:
            issues.append(f"Found {null_artist} null artist names")
        
        if 'popularity' in df.columns:
            out_of_range = df[(df['popularity'] < 0) | (df['popularity'] > 100)].shape[0]
            if out_of_range > 0:
                issues.append(f"Found {out_of_range} popularity values out of range [0,100]")
        
        if not issues:
            print(f"     OK All validations passed!")
        else:
            for issue in issues:
                print(f"     WARNING {issue}")
        
        return issues
    
    @staticmethod
    def validate_artists(df):
        print("\n  Validating artists...")
        issues = []
        
        null_artist = df['artist_name'].isnull().sum()
        if null_artist > 0:
            issues.append(f"Found {null_artist} null artist names")
        
        if 'popularity' in df.columns:
            out_of_range = df[(df['popularity'] < 0) | (df['popularity'] > 100)].shape[0]
            if out_of_range > 0:
                issues.append(f"Found {out_of_range} popularity values out of range [0,100]")
        
        if not issues:
            print(f"     OK All validations passed!")
        else:
            for issue in issues:
                print(f"     WARNING {issue}")
        
        return issues


class ReportGenerator:
    @staticmethod
    def generate_report(cleaned, normalized, integrated, issues_tracks, issues_artists):
        print("\n  Generating quality report...")
        
        report = {
            'week': 2,
            'phase': 'transformation',
            'datasets': {
                'cleaned': len(cleaned),
                'normalized': len(normalized),
                'integrated': 2
            },
            'records': {
                'integrated_tracks': len(integrated['tracks']),
                'integrated_artists': len(integrated['artists'])
            },
            'validation': {
                'tracks_issues': len(issues_tracks),
                'artists_issues': len(issues_artists)
            }
        }
        
        report_path = Path('reports/week2_quality_report.json')
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n     OK Report saved: {report_path}")
        
        print("\n" + "="*70)
        print("WEEK 2 SUMMARY")
        print("="*70)
        print(f"  Cleaned datasets: {report['datasets']['cleaned']}")
        print(f"  Normalized datasets: {report['datasets']['normalized']}")
        print(f"  Integrated tracks: {report['records']['integrated_tracks']}")
        print(f"  Integrated artists: {report['records']['integrated_artists']}")
        print(f"  Validation issues: {report['validation']['tracks_issues'] + report['validation']['artists_issues']}")
        print("="*70)
        
        return report


def main():
    print("\n\n")
    print("="*70)
    print("SPOTIFY EDA - WEEK 2 COMPLETE")
    print("Clean -> Normalize -> Integrate -> Validate")
    print("="*70)
    
    print("\nSTEP 1/4: CLEANING")
    cleaned = clean('data/raw', 'data/staging')
    
    print("\nSTEP 2/4: NORMALIZATION")
    normalized = normalize('data/staging', 'data/staging')
    
    print("\nSTEP 3/4: INTEGRATION")
    integrator = DataIntegrator()
    integrated_tracks = integrator.integrate_tracks(normalized)
    integrated_artists = integrator.integrate_artists(normalized)
    
    if not integrated_tracks.empty:
        integrated_tracks.to_parquet('data/staging/integrated_tracks.parquet', index=False)
        print(f"     OK Saved: integrated_tracks.parquet")
    
    if not integrated_artists.empty:
        integrated_artists.to_parquet('data/staging/integrated_artists.parquet', index=False)
        print(f"     OK Saved: integrated_artists.parquet")
    
    print("\nSTEP 4/4: VALIDATION & REPORTS")
    validator = DataValidator()
    issues_tracks = validator.validate_tracks(integrated_tracks)
    issues_artists = validator.validate_artists(integrated_artists)
    
    integrated = {
        'tracks': integrated_tracks,
        'artists': integrated_artists
    }
    report = ReportGenerator.generate_report(
        cleaned, normalized, integrated, 
        issues_tracks, issues_artists
    )
    
    print("\n" + "="*70)
    print("WEEK 2 COMPLETE")
    print("="*70)
    
    print("\nOutput files created in data/staging/:")
    print("   OK clean_*.parquet (8 files)")
    print("   OK norm_*.parquet (8 files)")
    print("   OK integrated_tracks.parquet")
    print("   OK integrated_artists.parquet")
    
    print("\nReport: reports/week2_quality_report.json")
    print("\nNext step: Week 3 (Load to Database)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

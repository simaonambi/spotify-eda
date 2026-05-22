#!/usr/bin/env python3
# src/transform/week2_orchestrator.py
"""
WEEK 2 COMPLETE ORCHESTRATOR
Executes: Cleaning -> Normalization -> Integration -> Validation -> Reports
Located in src/transform/
"""

import pandas as pd
import json
from pathlib import Path
from .cleaning import clean_all_data as clean
from .normalization import normalize_all_data as normalize


class DataIntegrator:
    """Integrate multiple data sources into unified datasets"""
    
    @staticmethod
    def integrate_tracks(normalized_data):
        """Combine tracks from 3 sources (Spotify, Charts, Last.fm)"""
        print("\n" + "="*70)
        print("STEP 3/4: DATA INTEGRATION")
        print("="*70)
        
        print("\n  Integrating tracks from 3 sources...")
        
        # Collect tracks from all sources
        all_tracks = []
        
        for source_name, df in normalized_data.items():
            if 'track' in source_name and 'artist' not in source_name:
                # Add source column
                df['source'] = source_name.replace('spotify_charts_', 'charts_').replace('lastfm_top_', 'lastfm_')
                all_tracks.append(df)
        
        if all_tracks:
            # Combine all tracks
            integrated = pd.concat(all_tracks, ignore_index=True)
            
            # Remove exact duplicates (same track AND artist)
            before = len(integrated)
            integrated = integrated.drop_duplicates(
                subset=['track_name', 'artist_name'], 
                keep='first'
            )
            removed = before - len(integrated)
            
            print(f"     OK Combined {len(all_tracks)} sources")
            print(f"     OK Removed {removed} exact duplicates")
            print(f"     OK Result: {len(integrated)} unique tracks")
            
            return integrated
        
        return pd.DataFrame()
    
    @staticmethod
    def integrate_artists(normalized_data):
        """Combine artists from 3 sources"""
        print("\n  Integrating artists from 3 sources...")
        
        # Collect artists
        all_artists = []
        
        for source_name, df in normalized_data.items():
            if 'artist' in source_name:
                df['source'] = source_name.replace('spotify_charts_', 'charts_').replace('lastfm_', 'lastfm_')
                all_artists.append(df)
        
        if all_artists:
            integrated = pd.concat(all_artists, ignore_index=True)
            
            # Remove duplicates
            before = len(integrated)
            integrated = integrated.drop_duplicates(
                subset=['artist_name'], 
                keep='first'
            )
            removed = before - len(integrated)
            
            print(f"     OK Combined {len(all_artists)} sources")
            print(f"     OK Removed {removed} exact duplicates")
            print(f"     OK Result: {len(integrated)} unique artists")
            
            return integrated
        
        return pd.DataFrame()


class DataValidator:
    """Validate data quality"""
    
    @staticmethod
    def validate_tracks(df):
        """Validate tracks dataset"""
        print("\n" + "="*70)
        print("STEP 4/4: DATA VALIDATION & REPORTS")
        print("="*70)
        
        print("\n  Validating tracks...")
        
        issues = []
        
        # Check nulls
        null_track = df['track_name'].isnull().sum()
        null_artist = df['artist_name'].isnull().sum()
        
        if null_track > 0:
            issues.append(f"Found {null_track} null track names")
        if null_artist > 0:
            issues.append(f"Found {null_artist} null artist names")
        
        # Check ranges
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
        """Validate artists dataset"""
        print("\n  Validating artists...")
        
        issues = []
        
        # Check nulls
        null_artist = df['artist_name'].isnull().sum()
        if null_artist > 0:
            issues.append(f"Found {null_artist} null artist names")
        
        # Check popularity range
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
    """Generate quality reports"""
    
    @staticmethod
    def generate_report(cleaned, normalized, integrated, issues_tracks, issues_artists):
        """Generate comprehensive report"""
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
            },
            'issues': {
                'tracks': issues_tracks,
                'artists': issues_artists
            }
        }
        
        # Save JSON report
        report_path = Path('reports/week2_quality_report.json')
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n     OK Report saved: {report_path}")
        
        # Print summary
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


class Week2Orchestrator:
    """Main orchestrator for Week 2 transformation"""
    
    def run(self):
        """Execute complete Week 2 pipeline"""
        
        print("\n\n")
        print("="*70)
        print("SPOTIFY EDA - WEEK 2 COMPLETE")
        print("Clean -> Normalize -> Integrate -> Validate")
        print("="*70)
        
        # Step 1: Clean
        print("\nSTEP 1/4: CLEANING")
        cleaned = clean('data/raw', 'data/staging')
        
        # Step 2: Normalize
        print("\nSTEP 2/4: NORMALIZATION")
        normalized = normalize('data/staging', 'data/staging')
        
        # Step 3: Integrate
        print("\nSTEP 3/4: INTEGRATION")
        integrator = DataIntegrator()
        integrated_tracks = integrator.integrate_tracks(normalized)
        integrated_artists = integrator.integrate_artists(normalized)
        
        # Save integrated data
        if not integrated_tracks.empty:
            integrated_tracks.to_parquet('data/staging/integrated_tracks.parquet', index=False)
            print(f"     OK Saved: integrated_tracks.parquet")
        
        if not integrated_artists.empty:
            integrated_artists.to_parquet('data/staging/integrated_artists.parquet', index=False)
            print(f"     OK Saved: integrated_artists.parquet")
        
        # Step 4: Validate
        print("\nSTEP 4/4: VALIDATION & REPORTS")
        validator = DataValidator()
        issues_tracks = validator.validate_tracks(integrated_tracks)
        issues_artists = validator.validate_artists(integrated_artists)
        
        # Generate reports
        integrated = {
            'tracks': integrated_tracks,
            'artists': integrated_artists
        }
        report = ReportGenerator.generate_report(
            cleaned, normalized, integrated, 
            issues_tracks, issues_artists
        )
        
        # Final message
        print("\n" + "="*70)
        print("WEEK 2 COMPLETE")
        print("="*70)
        
        print("\nOutput files created in data/staging/:")
        print("   OK clean_*.parquet (8 files - cleaned data)")
        print("   OK norm_*.parquet (8 files - normalized data)")
        print("   OK integrated_tracks.parquet")
        print("   OK integrated_artists.parquet")
        
        print("\nReport: reports/week2_quality_report.json")
        
        print("\nNext step: Week 3 (Load to Database)")
        
        return report


if __name__ == "__main__":
    try:
        orchestrator = Week2Orchestrator()
        report = orchestrator.run()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
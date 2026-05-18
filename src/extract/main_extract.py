#!/usr/bin/env python3
# src/extract/main_extract.py
"""
Main extraction module for Spotify EDA - Week 1 (LIGHTWEIGHT VERSION)
Orchestrates extraction from: Spotify Web Crawler, Spotify Charts, Last.fm API
"""

import sys
import os
from pathlib import Path
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.extract.spotify_crawler import SpotifyCrawler
from src.extract.spotify_charts import extract_spotify_charts
from src.extract.lastfm_api import extract_lastfm
from src.config.config import RAW_DATA_PATH
from src.config.logging_config import setup_logging

logger = setup_logging(__name__)
load_dotenv()


class ExtractionOrchestrator:
    """
    Orchestrates extraction from 3 sources (LIGHTWEIGHT):
    1. Spotify Web Crawler
    2. Spotify Charts (lightweight alternative to MPD)
    3. Last.fm API
    """
    
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or RAW_DATA_PATH
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.start_time = None
        self.end_time = None
        self.results = {}
    
    def run_extraction(self):
        self.start_time = datetime.now()
        
        print("\n" + "="*70)
        print(" SPOTIFY EDA - WEEK 1 (LIGHTWEIGHT VERSION) 🎵")
        print("="*70)
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Sources: Spotify Crawler + Spotify Charts + Last.fm API")
        print("="*70)
        
        try:
            spotify_result = self._extract_spotify()
            charts_result = self._extract_spotify_charts()
            lastfm_result = self._extract_lastfm()
            
            self._print_summary()
            
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
            
            print("\n" + "="*70)
            print("✓ EXTRACTION COMPLETE!")
            print("="*70)
            print(f" Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
            print(f" Output: {self.output_dir}")
            print("="*70 + "\n")
            
            return {
                'status': 'success',
                'duration': duration,
                'output_dir': self.output_dir,
                'results': self.results
            }
        
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            print(f"\n✗ EXTRACTION FAILED: {str(e)}\n")
            import traceback
            traceback.print_exc()
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _extract_spotify(self):
        print("\n" + "█"*70)
        print("STEP 1/3: SPOTIFY WEB CRAWLER")
        print("█"*70)
        
        try:
            logger.info("Starting Spotify Web Crawler extraction...")
            
            crawler = SpotifyCrawler()
            data = crawler.crawl_all(output_dir=self.output_dir)
            
            self.results['spotify'] = {
                'tracks': len(data['tracks']),
                'artists': len(data['artists']),
                'playlists': len(data['playlists']),
                'files': [
                    f'{self.output_dir}/spotify_tracks.parquet',
                    f'{self.output_dir}/spotify_artists.parquet',
                    f'{self.output_dir}/spotify_playlists.parquet'
                ]
            }
            
            logger.info(f"Spotify extraction complete: {self.results['spotify']}")
            return data
        
        except Exception as e:
            logger.error(f"Spotify extraction failed: {str(e)}")
            raise
    
    def _extract_spotify_charts(self):
        print("\n" + "█"*70)
        print("STEP 2/3: SPOTIFY CHARTS (Lightweight Alternative)")
        print("█"*70)
        
        try:
            logger.info("Starting Spotify Charts extraction...")
            
            print("\n✓ Extracting: trending playlists, popular tracks, artists\n")
            
            playlists_df, tracks_df, artists_df = extract_spotify_charts(
                output_dir=self.output_dir
            )
            
            self.results['spotify_charts'] = {
                'playlists': len(playlists_df),
                'tracks': len(tracks_df),
                'artists': len(artists_df),
                'mode': 'lightweight',
                'files': [
                    f'{self.output_dir}/spotify_charts_playlists.parquet',
                    f'{self.output_dir}/spotify_charts_tracks.parquet',
                    f'{self.output_dir}/spotify_charts_artists.parquet'
                ]
            }
            
            logger.info(f"Spotify Charts extraction complete: {self.results['spotify_charts']}")
            return playlists_df, tracks_df, artists_df
        
        except Exception as e:
            logger.error(f"Spotify Charts extraction failed: {str(e)}")
            print(f"\n  Spotify Charts extraction failed: {str(e)}")
            self.results['spotify_charts'] = {'status': 'failed', 'error': str(e)}
            return None, None, None
    
    def _extract_lastfm(self):
        print("\n" + "█"*70)
        print("STEP 3/3: LAST.FM API")
        print("█"*70)
        
        try:
            logger.info("Starting Last.fm API extraction...")
            
            api_key = os.getenv('LASTFM_API_KEY')
            api_secret = os.getenv('LASTFM_API_SECRET')
            
            if not api_key:
                raise ValueError("LASTFM_API_KEY not set in .env file")
            
            tracks_df, artists_df = extract_lastfm(
                api_key=api_key,
                api_secret=api_secret,
                output_dir=self.output_dir,
                tracks_limit=500,
                artist_sample=True
            )
            
            self.results['lastfm'] = {
                'tracks': len(tracks_df),
                'artists': len(artists_df),
                'files': [
                    f'{self.output_dir}/lastfm_top_tracks.parquet',
                    f'{self.output_dir}/lastfm_artists.parquet'
                ]
            }
            
            logger.info(f"Last.fm extraction complete: {self.results['lastfm']}")
            return tracks_df, artists_df
        
        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            print(f"\n✗ Last.fm configuration error: {str(e)}")
            self.results['lastfm'] = {'status': 'failed', 'error': str(e)}
            return None, None
        
        except Exception as e:
            logger.error(f"Last.fm extraction failed: {str(e)}")
            print(f"\n  Last.fm extraction skipped: {str(e)}")
            self.results['lastfm'] = {'status': 'failed', 'error': str(e)}
            return None, None
    
    def _print_summary(self):
        print("\n" + "="*70)
        print(" EXTRACTION SUMMARY")
        print("="*70)
        
        total_records = 0
        
        if 'spotify' in self.results:
            spotify = self.results['spotify']
            print(f"\n✓ SPOTIFY CRAWLER")
            print(f"  Tracks: {spotify['tracks']}")
            print(f"  Artists: {spotify['artists']}")
            print(f"  Playlists: {spotify['playlists']}")
            total_records += spotify['tracks'] + spotify['artists'] + spotify['playlists']
        
        if 'spotify_charts' in self.results:
            charts = self.results['spotify_charts']
            if 'playlists' in charts:
                print(f"\n✓ SPOTIFY CHARTS")
                print(f"  Playlists: {charts['playlists']}")
                print(f"  Tracks: {charts['tracks']}")
                print(f"  Artists: {charts['artists']}")
                total_records += charts['playlists'] + charts['tracks'] + charts['artists']
            else:
                print(f"\n  Spotify Charts: {charts.get('error', 'Failed')}")
        
        if 'lastfm' in self.results:
            lastfm = self.results['lastfm']
            if 'tracks' in lastfm:
                print(f"\n✓ LAST.FM API")
                print(f"  Top tracks: {lastfm['tracks']}")
                print(f"  Artists: {lastfm['artists']}")
                total_records += lastfm['tracks'] + lastfm['artists']
            else:
                print(f"\n  Last.fm: {lastfm.get('error', 'Not configured')}")
        
        print(f"\n TOTAL RECORDS: {total_records:,}")
        
        print("\n" + "="*70)
        print(" FILES CREATED:")
        print("="*70)
        
        all_files = []
        for source in ['spotify', 'spotify_charts', 'lastfm']:
            if source in self.results and 'files' in self.results[source]:
                for file in self.results[source]['files']:
                    if os.path.exists(file):
                        size_kb = os.path.getsize(file) / 1024
                        print(f"  ✓ {os.path.basename(file)} ({size_kb:.1f} KB)")
                        all_files.append(file)


def main():
    print("\n" + "="*70)
    print("🎵 SPOTIFY EDA - WEEK 1 EXTRACTION (LIGHTWEIGHT)")
    print("="*70)
    print("Sources:")
    print("  1. Spotify Web Crawler")
    print("  2. Spotify Charts (lightweight alternative)")
    print("  3. Last.fm API")
    print("="*70 + "\n")
    
    orchestrator = ExtractionOrchestrator()
    result = orchestrator.run_extraction()
    
    if result['status'] == 'success':
        print("\n✓ EXTRACTION SUCCESSFUL!")
        print(f"Duration: {result['duration']:.1f} seconds")
        print(f"Output: {result['output_dir']}")
        print("\n✓ Ready for Week 2 (Transform)\n")
        return 0
    else:
        print("\n✗ EXTRACTION FAILED!")
        print(f"Error: {result['error']}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
#!/usr/bin/env python3
# src/extract/lastfm_api.py
"""
Last.fm API Integration
Extracts data from Last.fm API for music metadata enrichment
"""

import requests
import pandas as pd
import time
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class LastfmAPI:
    """
    Last.fm API client for extracting music data
    """
    
    def __init__(self, api_key: str, api_secret: Optional[str] = None):
        """
        Initialize Last.fm API client
        
        Args:
            api_key: Last.fm API key
            api_secret: Last.fm API secret (optional, for authenticated requests)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'http://ws.audioscrobbler.com/2.0/'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
    
    def get_top_tracks(self, limit: int = 500, period: str = 'overall') -> List[Dict]:
        """
        Get global top tracks from Last.fm
        
        Args:
            limit: Number of tracks to retrieve (max 500)
            period: Period for chart ('overall', '12month', '6month', '3month', '1month', '7day')
            
        Returns:
            List of track dictionaries
        """
        
        print(f"\n[1/2] Fetching top {limit} tracks from Last.fm...")
        
        tracks_data = []
        
        try:
            params = {
                'method': 'chart.gettoptracks',
                'api_key': self.api_key,
                'format': 'json',
                'limit': min(limit, 500),  # API max is 500
                'period': period
            }
            
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'tracks' not in data or 'track' not in data['tracks']:
                logger.warning("No tracks found in Last.fm response")
                return tracks_data
            
            for track in data['tracks']['track']:
                try:
                    tracks_data.append({
                        'track_name': track.get('name', ''),
                        'artist_name': track.get('artist', {}).get('name', '') if isinstance(track.get('artist'), dict) else track.get('artist', ''),
                        'playcount': int(track.get('playcount', 0)),
                        'listeners': int(track.get('listeners', 0)),
                        'url': track.get('url', ''),
                        'rank': track.get('@attr', {}).get('rank', '') if isinstance(track.get('@attr'), dict) else ''
                    })
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing track: {e}")
                    continue
                
                time.sleep(0.05)  # Rate limiting
            
            print(f"✓ Retrieved {len(tracks_data)} top tracks")
            logger.info(f"Retrieved {len(tracks_data)} top tracks from Last.fm")
            
            return tracks_data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Last.fm API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting top tracks: {e}")
            raise
    
    def get_artist_info(self, artist_names: List[str]) -> List[Dict]:
        """
        Get artist information from Last.fm
        
        Args:
            artist_names: List of artist names
            
        Returns:
            List of artist dictionaries
        """
        
        print(f"\n[2/2] Fetching info for {len(artist_names)} artists...")
        
        artists_data = []
        
        for idx, artist_name in enumerate(artist_names):
            try:
                params = {
                    'method': 'artist.getinfo',
                    'artist': artist_name,
                    'api_key': self.api_key,
                    'format': 'json',
                    'autocorrect': 1
                }
                
                response = self.session.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if 'artist' not in data:
                    logger.warning(f"No data found for artist: {artist_name}")
                    continue
                
                artist_info = data['artist']
                
                # Extract tags
                tags = []
                if 'tags' in artist_info and 'tag' in artist_info['tags']:
                    tag_list = artist_info['tags']['tag']
                    if isinstance(tag_list, list):
                        tags = [tag.get('name', '') for tag in tag_list[:5]]
                    else:
                        tags = [tag_list.get('name', '')]
                
                artists_data.append({
                    'artist_name': artist_info.get('name', artist_name),
                    'mbid': artist_info.get('mbid', ''),
                    'listeners': int(artist_info.get('stats', {}).get('listeners', 0)) if isinstance(artist_info.get('stats'), dict) else 0,
                    'playcount': int(artist_info.get('stats', {}).get('playcount', 0)) if isinstance(artist_info.get('stats'), dict) else 0,
                    'url': artist_info.get('url', ''),
                    'tags': ', '.join(tags) if tags else '',
                    'bio': artist_info.get('bio', {}).get('summary', '') if isinstance(artist_info.get('bio'), dict) else ''
                })
                
                print(f"  ✓ [{idx + 1}/{len(artist_names)}] {artist_name}")
                
                time.sleep(0.5)  # Rate limiting
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"API error for artist {artist_name}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Error getting info for {artist_name}: {e}")
                continue
        
        print(f"✓ Retrieved info for {len(artists_data)} artists")
        logger.info(f"Retrieved info for {len(artists_data)} artists")
        
        return artists_data
    
    def get_similar_artists(self, artist_name: str, limit: int = 10) -> List[Dict]:
        """
        Get similar artists from Last.fm
        
        Args:
            artist_name: Name of artist
            limit: Number of similar artists to retrieve
            
        Returns:
            List of similar artist dictionaries
        """
        
        similar_artists = []
        
        try:
            params = {
                'method': 'artist.getsimilar',
                'artist': artist_name,
                'api_key': self.api_key,
                'format': 'json',
                'limit': limit,
                'autocorrect': 1
            }
            
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'similarartists' not in data or 'artist' not in data['similarartists']:
                return similar_artists
            
            for artist in data['similarartists']['artist']:
                similar_artists.append({
                    'artist_name': artist.get('name', ''),
                    'match': float(artist.get('match', 0)),
                    'url': artist.get('url', ''),
                    'image': artist.get('image', [{}])[-1].get('#text', '') if artist.get('image') else ''
                })
                
                time.sleep(0.1)
            
            logger.info(f"Retrieved {len(similar_artists)} similar artists for {artist_name}")
            
            return similar_artists
        
        except Exception as e:
            logger.warning(f"Error getting similar artists for {artist_name}: {e}")
            return similar_artists


def extract_lastfm(api_key: str, api_secret: Optional[str] = None,
                   output_dir: str = 'data/raw',
                   tracks_limit: int = 500,
                   artist_sample: bool = True) -> tuple:
    """
    Extract data from Last.fm API
    
    Args:
        api_key: Last.fm API key
        api_secret: Last.fm API secret (optional)
        output_dir: Directory to save Parquet files
        tracks_limit: Number of top tracks to retrieve
        artist_sample: Whether to get info for top artists
        
    Returns:
        Tuple of (tracks_df, artists_df)
    """
    
    print("\n" + "="*70)
    print("🎵 LAST.FM API EXTRACTION")
    print("="*70)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    api = LastfmAPI(api_key=api_key, api_secret=api_secret)
    
    # Get top tracks
    tracks_data = api.get_top_tracks(limit=tracks_limit)
    tracks_df = pd.DataFrame(tracks_data)
    
    # Get artist info
    artists_data = []
    if artist_sample and len(tracks_data) > 0:
        unique_artists = list(set([t['artist_name'] for t in tracks_data if t.get('artist_name')]))[:50]
        artists_data = api.get_artist_info(unique_artists)
    
    artists_df = pd.DataFrame(artists_data)
    
    # Save to Parquet
    print("\nSaving to Parquet...")
    tracks_path = f'{output_dir}/lastfm_top_tracks.parquet'
    artists_path = f'{output_dir}/lastfm_artists.parquet'
    
    tracks_df.to_parquet(tracks_path, index=False)
    artists_df.to_parquet(artists_path, index=False)
    
    print(f"✓ Saved: {tracks_path} ({len(tracks_df)} rows)")
    print(f"✓ Saved: {artists_path} ({len(artists_df)} rows)")
    
    logger.info(f"Last.fm extraction complete: {len(tracks_df)} tracks, {len(artists_df)} artists")
    
    return tracks_df, artists_df


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv('LASTFM_API_KEY')
    api_secret = os.getenv('LASTFM_API_SECRET')
    
    if not api_key:
        print("Error: LASTFM_API_KEY not set in .env file")
        exit(1)
    
    tracks_df, artists_df = extract_lastfm(api_key, api_secret)
    
    print("\n" + "="*70)
    print("SAMPLE DATA")
    print("="*70)
    
    print("\nTop Tracks:")
    print(tracks_df[['track_name', 'artist_name', 'playcount']].head())
    
    print("\nArtists:")
    print(artists_df[['artist_name', 'listeners', 'playcount']].head())

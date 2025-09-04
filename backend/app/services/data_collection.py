import spotipy
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

from app.models import User, Track, ListeningHistory
from app.schemas import TrackCreate

class DataCollectionService:
    def __init__(self, db: Session):
        self.db = db
    
    async def sync_user_listening_history(self, user_id: int, sp: spotipy.Spotify):
        """Sincroniza o histórico de escuta do usuário"""
        try:
            # Get recently played tracks
            recent_tracks = sp.current_user_recently_played(limit=50)
            
            for item in recent_tracks['items']:
                track_data = item['track']
                played_at = datetime.fromisoformat(item['played_at'].replace('Z', '+00:00'))
                
                # Check if track exists
                db_track = self.db.query(Track).filter(Track.spotify_id == track_data['id']).first()
                
                if not db_track:
                    # Get audio features
                    try:
                        audio_features = sp.audio_features(track_data['id'])[0]
                    except:
                        audio_features = None
                    
                    # Create track
                    db_track = Track(
                        spotify_id=track_data['id'],
                        name=track_data['name'],
                        artists=','.join([artist['name'] for artist in track_data['artists']]),
                        album=track_data['album']['name'],
                        duration_ms=track_data['duration_ms'],
                        popularity=track_data['popularity'],
                        explicit=track_data['explicit'],
                        preview_url=track_data.get('preview_url'),
                        external_urls=json.dumps(track_data['external_urls'])
                    )
                    
                    # Add audio features if available
                    if audio_features:
                        db_track.danceability = audio_features.get('danceability')
                        db_track.energy = audio_features.get('energy')
                        db_track.key = audio_features.get('key')
                        db_track.loudness = audio_features.get('loudness')
                        db_track.mode = audio_features.get('mode')
                        db_track.speechiness = audio_features.get('speechiness')
                        db_track.acousticness = audio_features.get('acousticness')
                        db_track.instrumentalness = audio_features.get('instrumentalness')
                        db_track.liveness = audio_features.get('liveness')
                        db_track.valence = audio_features.get('valence')
                        db_track.tempo = audio_features.get('tempo')
                        db_track.time_signature = audio_features.get('time_signature')
                    
                    self.db.add(db_track)
                    self.db.commit()
                    self.db.refresh(db_track)
                
                # Check if listening history entry exists
                existing_entry = self.db.query(ListeningHistory).filter(
                    ListeningHistory.user_id == user_id,
                    ListeningHistory.track_id == db_track.id,
                    ListeningHistory.played_at == played_at
                ).first()
                
                if not existing_entry:
                    # Create listening history entry
                    history_entry = ListeningHistory(
                        user_id=user_id,
                        track_id=db_track.id,
                        played_at=played_at,
                        context_type=item.get('context', {}).get('type'),
                        context_name=item.get('context', {}).get('name')
                    )
                    self.db.add(history_entry)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    async def get_user_top_tracks(self, user_id: int, sp: spotipy.Spotify, time_range: str = 'medium_term', limit: int = 50):
        """Obtém as músicas mais tocadas do usuário"""
        try:
            top_tracks = sp.current_user_top_tracks(limit=limit, time_range=time_range)
            
            tracks_data = []
            for track_data in top_tracks['items']:
                # Get or create track in database
                db_track = self.db.query(Track).filter(Track.spotify_id == track_data['id']).first()
                
                if not db_track:
                    # Get audio features
                    try:
                        audio_features = sp.audio_features(track_data['id'])[0]
                    except:
                        audio_features = None
                    
                    # Create track
                    db_track = Track(
                        spotify_id=track_data['id'],
                        name=track_data['name'],
                        artists=','.join([artist['name'] for artist in track_data['artists']]),
                        album=track_data['album']['name'],
                        duration_ms=track_data['duration_ms'],
                        popularity=track_data['popularity'],
                        explicit=track_data['explicit'],
                        preview_url=track_data.get('preview_url'),
                        external_urls=json.dumps(track_data['external_urls'])
                    )
                    
                    # Add audio features if available
                    if audio_features:
                        db_track.danceability = audio_features.get('danceability')
                        db_track.energy = audio_features.get('energy')
                        db_track.key = audio_features.get('key')
                        db_track.loudness = audio_features.get('loudness')
                        db_track.mode = audio_features.get('mode')
                        db_track.speechiness = audio_features.get('speechiness')
                        db_track.acousticness = audio_features.get('acousticness')
                        db_track.instrumentalness = audio_features.get('instrumentalness')
                        db_track.liveness = audio_features.get('liveness')
                        db_track.valence = audio_features.get('valence')
                        db_track.tempo = audio_features.get('tempo')
                        db_track.time_signature = audio_features.get('time_signature')
                    
                    self.db.add(db_track)
                    self.db.commit()
                    self.db.refresh(db_track)
                
                tracks_data.append({
                    'track': db_track,
                    'spotify_data': track_data
                })
            
            return tracks_data
            
        except Exception as e:
            raise e
    
    async def get_user_top_artists(self, user_id: int, sp: spotipy.Spotify, time_range: str = 'medium_term', limit: int = 50):
        """Obtém os artistas mais ouvidos do usuário"""
        try:
            top_artists = sp.current_user_top_artists(limit=limit, time_range=time_range)
            
            artists_data = []
            for artist_data in top_artists['items']:
                artists_data.append({
                    'id': artist_data['id'],
                    'name': artist_data['name'],
                    'genres': artist_data['genres'],
                    'popularity': artist_data['popularity'],
                    'followers': artist_data['followers']['total'],
                    'image_url': artist_data['images'][0]['url'] if artist_data['images'] else None,
                    'external_urls': artist_data['external_urls']
                })
            
            return artists_data
            
        except Exception as e:
            raise e


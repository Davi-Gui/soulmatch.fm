import spotipy
import pandas as pd
import os
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.models import Track, ListeningHistory

_tracks_df = None

def get_tracks_dataset():
    global _tracks_df
    if _tracks_df is None:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            csv_path = os.path.join(base_dir, 'data', 'spotify_features.csv')
            
            print(f"Tentando carregar dataset de: {csv_path}")
            
            if not os.path.exists(csv_path):
                print(f"ARQUIVO NÃO ENCONTRADO: {csv_path}")
                return pd.DataFrame()

            col_mapping = {'track_id': 'id'} 
            
            cols_to_load = [
                'track_id', 'danceability', 'energy', 'key', 'loudness', 'mode', 
                'speechiness', 'acousticness', 'instrumentalness', 'liveness', 
                'valence', 'tempo', 'time_signature'
            ]
            
            _tracks_df = pd.read_csv(csv_path, usecols=cols_to_load)
            _tracks_df.rename(columns=col_mapping, inplace=True)
            _tracks_df.set_index('id', inplace=True)
            
            print(f"Dataset carregado com sucesso ({len(_tracks_df)} músicas)")
            
        except ValueError as ve:
            print(f"Erro de colunas: {ve}")
            print("   Dica: verifique se o nome 'track_id' existe no seu CSV usando o script check_columns.py")
            _tracks_df = pd.DataFrame()
        except Exception as e:
            print(f"Erro ao carregar CSV: {e}")
            _tracks_df = pd.DataFrame()
            
    return _tracks_df

class DataCollectionService:
    def __init__(self, db: Session):
        self.db = db
        self.dataset = get_tracks_dataset()
    
    def _enrich_track_from_csv(self, db_track):
        # Try to get audio features from the CSV dataset if Spotify API doesn't have them
        if self.dataset.empty:
            return False

        spotify_id = db_track.spotify_id
        
        if spotify_id in self.dataset.index:
            try:
                features = self.dataset.loc[spotify_id]
                
                db_track.danceability = float(features['danceability'])
                db_track.energy = float(features['energy'])
                db_track.key = int(features['key'])
                db_track.loudness = float(features['loudness'])
                db_track.mode = int(features['mode'])
                db_track.speechiness = float(features['speechiness'])
                db_track.acousticness = float(features['acousticness'])
                db_track.instrumentalness = float(features['instrumentalness'])
                db_track.liveness = float(features['liveness'])
                db_track.valence = float(features['valence'])
                db_track.tempo = float(features['tempo'])
                db_track.time_signature = int(features['time_signature'])
                
                return True
            except Exception as e:
                print(f"⚠️ Erro ao ler dados do CSV para {spotify_id}: {e}")
        return False

    async def sync_user_listening_history(self, user_id: int, sp: spotipy.Spotify):
        """Sincroniza o histórico de escuta do usuário"""
        try:
            recent_tracks = sp.current_user_recently_played(limit=50)
            print(f"🔄 Processando {len(recent_tracks['items'])} músicas do histórico...")
            
            for item in recent_tracks['items']:
                track_data = item['track']
                played_at = datetime.fromisoformat(item['played_at'].replace('Z', '+00:00'))
                spotify_id = track_data['id']
                
                db_track = self.db.query(Track).filter(Track.spotify_id == spotify_id).first()
                track_modified = False  # Track if we need to commit changes to the track

                if not db_track:
                    # Create new track entry from Spotify data
                    db_track = Track(
                        spotify_id=spotify_id,
                        name=track_data['name'],
                        artists=','.join([artist['name'] for artist in track_data['artists']]),
                        album=track_data['album']['name'],
                        duration_ms=track_data['duration_ms'],
                        popularity=track_data['popularity'],
                        explicit=track_data['explicit'],
                        preview_url=track_data.get('preview_url'),
                        external_urls=json.dumps(track_data['external_urls'])
                    )
                    self.db.add(db_track)
                    track_modified = True
                
                # If track exists but missing audio features, try to get them from CSV
                if db_track.danceability is None:
                    found = self._enrich_track_from_csv(db_track)
                    if found:
                        print(f"Dados recuperados do CSV para: {db_track.name}")
                        track_modified = True

                # Only commit if we actually changed something
                if track_modified:
                    self.db.commit()
                    self.db.refresh(db_track)
                
                existing_entry = self.db.query(ListeningHistory).filter(
                    ListeningHistory.user_id == user_id,
                    ListeningHistory.track_id == db_track.id,
                    ListeningHistory.played_at == played_at
                ).first()
                
                if not existing_entry:
                    context = item.get('context') or {}
                    history_entry = ListeningHistory(
                        user_id=user_id,
                        track_id=db_track.id,
                        played_at=played_at,
                        context_type=context.get('type'),
                        context_name=context.get('name')
                    )
                    self.db.add(history_entry)
            
            self.db.commit()
            print("Sincronização concluída")
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro na sincronização: {e}")
            raise e
            
    async def get_user_top_tracks(self, user_id: int, sp: spotipy.Spotify, time_range: str = 'medium_term', limit: int = 50):
        pass
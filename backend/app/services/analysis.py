import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
import json
from collections import Counter

from app.models import User, Track, ListeningHistory, UserProfile, CompatibilityScore

class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_user_profile(self, user_id: int):
        """Gera o perfil musical do usuário"""
        try:
            # Get user's listening history
            listening_history = self.db.query(ListeningHistory).filter(
                ListeningHistory.user_id == user_id
            ).all()
            
            if not listening_history:
                raise ValueError("Nenhum histórico de escuta encontrado")
            
            # Get tracks with audio features
            track_ids = [entry.track_id for entry in listening_history]
            tracks = self.db.query(Track).filter(Track.id.in_(track_ids)).all()
            
            # Calculate audio features averages
            audio_features = []
            for track in tracks:
                if all([
                    track.danceability is not None,
                    track.energy is not None,
                    track.valence is not None,
                    track.acousticness is not None,
                    track.instrumentalness is not None,
                    track.liveness is not None,
                    track.speechiness is not None,
                    track.tempo is not None
                ]):
                    audio_features.append([
                        track.danceability,
                        track.energy,
                        track.valence,
                        track.acousticness,
                        track.instrumentalness,
                        track.liveness,
                        track.speechiness,
                        track.tempo
                    ])
            
            if not audio_features:
                raise ValueError("Dados de características de áudio insuficientes")
            
            # Calculate averages
            audio_features_array = np.array(audio_features)
            avg_features = np.mean(audio_features_array, axis=0)
            
            # Get top genres, artists, and tracks
            top_genres = self._get_top_genres(user_id)
            top_artists = self._get_top_artists(user_id)
            top_tracks = self._get_top_tracks(user_id)
            
            # Calculate listening patterns
            total_tracks = len(listening_history)
            unique_artists = len(set([entry.track.artists for entry in listening_history if entry.track.artists]))
            unique_genres = len(top_genres)
            
            # Get or create user profile
            profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            
            if not profile:
                profile = UserProfile(user_id=user_id)
                self.db.add(profile)
            
            # Update profile
            profile.top_genres = json.dumps(top_genres)
            profile.top_artists = json.dumps(top_artists)
            profile.top_tracks = json.dumps(top_tracks)
            profile.avg_danceability = float(avg_features[0])
            profile.avg_energy = float(avg_features[1])
            profile.avg_valence = float(avg_features[2])
            profile.avg_acousticness = float(avg_features[3])
            profile.avg_instrumentalness = float(avg_features[4])
            profile.avg_liveness = float(avg_features[5])
            profile.avg_speechiness = float(avg_features[6])
            profile.avg_tempo = float(avg_features[7])
            profile.total_tracks_played = total_tracks
            profile.unique_artists = unique_artists
            profile.unique_genres = unique_genres
            
            self.db.commit()
            self.db.refresh(profile)
            
            return profile
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def _get_top_genres(self, user_id: int, limit: int = 10) -> List[str]:
        """Obtém os gêneros mais ouvidos pelo usuário"""
        # This would require genre information from Spotify API
        # For now, return empty list
        return []
    
    def _get_top_artists(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Obtém os artistas mais ouvidos pelo usuário"""
        listening_history = self.db.query(ListeningHistory).filter(
            ListeningHistory.user_id == user_id
        ).all()
        
        artist_counts = Counter()
        for entry in listening_history:
            if entry.track.artists:
                artists = entry.track.artists.split(',')
                for artist in artists:
                    artist_counts[artist.strip()] += 1
        
        top_artists = []
        for artist, count in artist_counts.most_common(limit):
            top_artists.append({
                'name': artist,
                'play_count': count
            })
        
        return top_artists
    
    def _get_top_tracks(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Obtém as músicas mais ouvidas pelo usuário"""
        listening_history = self.db.query(ListeningHistory).filter(
            ListeningHistory.user_id == user_id
        ).all()
        
        track_counts = Counter()
        for entry in listening_history:
            track_counts[entry.track_id] += 1
        
        top_tracks = []
        for track_id, count in track_counts.most_common(limit):
            track = self.db.query(Track).filter(Track.id == track_id).first()
            if track:
                top_tracks.append({
                    'id': track.spotify_id,
                    'name': track.name,
                    'artists': track.artists,
                    'play_count': count
                })
        
        return top_tracks
    
    async def calculate_compatibility(self, user1_id: int, user2_id: int) -> Dict[str, Any]:
        """Calcula a compatibilidade entre dois usuários"""
        try:
            # Get user profiles
            profile1 = self.db.query(UserProfile).filter(UserProfile.user_id == user1_id).first()
            profile2 = self.db.query(UserProfile).filter(UserProfile.user_id == user2_id).first()
            
            if not profile1 or not profile2:
                raise ValueError("Perfis dos usuários não encontrados")
            
            # Calculate audio features similarity
            audio_features1 = [
                profile1.avg_danceability, profile1.avg_energy, profile1.avg_valence,
                profile1.avg_acousticness, profile1.avg_instrumentalness, profile1.avg_liveness,
                profile1.avg_speechiness, profile1.avg_tempo
            ]
            audio_features2 = [
                profile2.avg_danceability, profile2.avg_energy, profile2.avg_valence,
                profile2.avg_acousticness, profile2.avg_instrumentalness, profile2.avg_liveness,
                profile2.avg_speechiness, profile2.avg_tempo
            ]
            
            # Calculate cosine similarity
            audio_similarity = cosine_similarity([audio_features1], [audio_features2])[0][0]
            
            # Calculate artist similarity
            artists1 = json.loads(profile1.top_artists) if profile1.top_artists else []
            artists2 = json.loads(profile2.top_artists) if profile2.top_artists else []
            
            artist_similarity = self._calculate_artist_similarity(artists1, artists2)
            
            # Calculate common tracks
            common_tracks = self._get_common_tracks(user1_id, user2_id)
            
            # Calculate overall compatibility score
            overall_score = (audio_similarity * 0.4 + artist_similarity * 0.4 + 
                           (len(common_tracks) / 10) * 0.2)  # Normalize common tracks
            
            # Ensure score is between 0 and 1
            overall_score = min(1.0, max(0.0, overall_score))
            
            # Save compatibility score
            compatibility = CompatibilityScore(
                user1_id=user1_id,
                user2_id=user2_id,
                overall_score=overall_score,
                audio_features_similarity=audio_similarity,
                artist_similarity=artist_similarity,
                common_tracks=len(common_tracks)
            )
            
            self.db.add(compatibility)
            self.db.commit()
            
            return {
                'overall_score': overall_score,
                'audio_features_similarity': audio_similarity,
                'artist_similarity': artist_similarity,
                'common_tracks': common_tracks,
                'breakdown': {
                    'audio_features': audio_similarity,
                    'artists': artist_similarity,
                    'common_tracks': len(common_tracks) / 10
                }
            }
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def _calculate_artist_similarity(self, artists1: List[Dict], artists2: List[Dict]) -> float:
        """Calcula similaridade entre listas de artistas"""
        if not artists1 or not artists2:
            return 0.0
        
        names1 = set([artist['name'] for artist in artists1])
        names2 = set([artist['name'] for artist in artists2])
        
        intersection = len(names1.intersection(names2))
        union = len(names1.union(names2))
        
        return intersection / union if union > 0 else 0.0
    
    def _get_common_tracks(self, user1_id: int, user2_id: int) -> List[Dict[str, Any]]:
        """Obtém músicas em comum entre dois usuários"""
        # Get tracks for both users
        tracks1 = set([entry.track_id for entry in 
                      self.db.query(ListeningHistory).filter(ListeningHistory.user_id == user1_id).all()])
        tracks2 = set([entry.track_id for entry in 
                      self.db.query(ListeningHistory).filter(ListeningHistory.user_id == user2_id).all()])
        
        common_track_ids = tracks1.intersection(tracks2)
        
        common_tracks = []
        for track_id in common_track_ids:
            track = self.db.query(Track).filter(Track.id == track_id).first()
            if track:
                common_tracks.append({
                    'id': track.spotify_id,
                    'name': track.name,
                    'artists': track.artists
                })
        
        return common_tracks
    
    async def perform_clustering(self, min_users: int = 10):
        """Realiza clustering de usuários baseado em perfis musicais"""
        try:
            # Get all user profiles with sufficient data
            profiles = self.db.query(UserProfile).filter(
                UserProfile.avg_danceability.isnot(None),
                UserProfile.avg_energy.isnot(None),
                UserProfile.avg_valence.isnot(None)
            ).all()
            
            if len(profiles) < min_users:
                return {"message": f"Usuários insuficientes para clustering (mínimo: {min_users})"}
            
            # Prepare data for clustering
            features = []
            profile_ids = []
            
            for profile in profiles:
                features.append([
                    profile.avg_danceability,
                    profile.avg_energy,
                    profile.avg_valence,
                    profile.avg_acousticness,
                    profile.avg_instrumentalness,
                    profile.avg_liveness,
                    profile.avg_speechiness,
                    profile.avg_tempo
                ])
                profile_ids.append(profile.id)
            
            # Standardize features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Perform K-means clustering
            n_clusters = min(5, len(profiles) // 3)  # Adaptive number of clusters
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(features_scaled)
            
            # Update user profiles with cluster assignments
            for i, profile_id in enumerate(profile_ids):
                profile = self.db.query(UserProfile).filter(UserProfile.id == profile_id).first()
                if profile:
                    profile.cluster_id = int(cluster_labels[i])
            
            self.db.commit()
            
            return {
                "message": f"Clustering realizado com sucesso",
                "n_clusters": n_clusters,
                "n_users": len(profiles)
            }
            
        except Exception as e:
            self.db.rollback()
            raise e


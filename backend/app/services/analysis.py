import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
import json
import math
from collections import Counter

from app.models import User, Track, ListeningHistory, UserProfile, CompatibilityScore

class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_user_profile(self, user_id: int, sp: Any = None):
        """Gera o perfil musical do usuário"""
        try:
            # Get user's listening history
            listening_history = self.db.query(ListeningHistory).filter(
                ListeningHistory.user_id == user_id
            ).all()
            
            if not listening_history:
                return None
            
            # Get tracks with audio features
            track_ids = [entry.track_id for entry in listening_history]
            tracks = self.db.query(Track).filter(Track.id.in_(track_ids)).all()
            
            # Coleta flexível de características
            audio_features = []
            for track in tracks:
                has_any_feature = any([
                    track.danceability, track.energy, track.valence, track.tempo
                ])
                
                if has_any_feature:
                    audio_features.append([
                        track.danceability or 0.0,
                        track.energy or 0.0,
                        track.valence or 0.0,
                        track.acousticness or 0.0,
                        track.instrumentalness or 0.0,
                        track.liveness or 0.0,
                        track.speechiness or 0.0,
                        track.tempo or 0.0
                    ])
            
            if not audio_features:
                print("⚠️ AVISO: Nenhuma característica encontrada. Usando perfil neutro.")
                avg_features = np.zeros(8)
            else:
                audio_features_array = np.array(audio_features)
                avg_features = np.mean(audio_features_array, axis=0)
            
            top_genres = self._get_top_genres(user_id, sp)
            top_artists = self._get_top_artists(user_id)
            top_tracks = self._get_top_tracks(user_id)
            
            total_tracks = len(listening_history)
            unique_artists = len(set([entry.track.artists for entry in listening_history if entry.track.artists]))
            unique_genres = len(top_genres)
            
            profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            
            if not profile:
                profile = UserProfile(user_id=user_id)
                self.db.add(profile)
            
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
            print(f"Erro na análise: {str(e)}")
            raise e
    
    def _get_top_genres(self, user_id: int, sp: Any = None, limit: int = 10) -> List[str]:
        if not sp:
            return []
        try:
            top_artists_data = sp.current_user_top_artists(limit=50, time_range='medium_term')
            all_genres = []
            for artist in top_artists_data['items']:
                if artist.get('genres'):
                    all_genres.extend(artist['genres'])
            genre_counts = Counter(all_genres)
            return [genre for genre, count in genre_counts.most_common(limit)]
        except Exception as e:
            print(f"Erro ao buscar gêneros: {e}")
            return []
    
    def _get_top_artists(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
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
            top_artists.append({'name': artist, 'play_count': count})
        
        return top_artists
    
    def _get_top_tracks(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
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
        """Calcula a compatibilidade com algoritmos melhorados"""
        try:
            profile1 = self.db.query(UserProfile).filter(UserProfile.user_id == user1_id).first()
            profile2 = self.db.query(UserProfile).filter(UserProfile.user_id == user2_id).first()
            
            if not profile1 or not profile2:
                raise ValueError("Perfis dos usuários não encontrados")
            
            # --- 1. Audio Features Similarity (Cosine) ---
            # Peso: 40%
            audio_features1 = [
                profile1.avg_danceability or 0, profile1.avg_energy or 0, profile1.avg_valence or 0,
                profile1.avg_acousticness or 0, profile1.avg_instrumentalness or 0, profile1.avg_liveness or 0,
                profile1.avg_speechiness or 0, profile1.avg_tempo or 0
            ]
            audio_features2 = [
                profile2.avg_danceability or 0, profile2.avg_energy or 0, profile2.avg_valence or 0,
                profile2.avg_acousticness or 0, profile2.avg_instrumentalness or 0, profile2.avg_liveness or 0,
                profile2.avg_speechiness or 0, profile2.avg_tempo or 0
            ]
            
            # Verifica se os vetores não são zerados (evita divisão por zero)
            if np.sum(audio_features1) == 0 or np.sum(audio_features2) == 0:
                audio_similarity = 0.0
            else:
                audio_similarity = cosine_similarity([audio_features1], [audio_features2])[0][0]
            
            # --- 2. Artist Similarity (Weighted Jaccard) ---
            # Peso: 35%
            artists1 = json.loads(profile1.top_artists) if profile1.top_artists else []
            artists2 = json.loads(profile2.top_artists) if profile2.top_artists else []
            
            artist_similarity = self._calculate_artist_similarity(artists1, artists2)
            
            # --- 3. Common Tracks Similarity (Logarithmic) ---
            # Peso: 25%
            common_tracks = self._get_common_tracks(user1_id, user2_id)
            count_common = len(common_tracks)
            
            # Fórmula Logarítmica: Recompensa muito as primeiras 10 músicas, depois diminui o ganho.
            # 1 música = 0.1, 10 músicas = 0.5, 50 músicas = 0.85, 100 músicas = 1.0
            if count_common == 0:
                track_score = 0.0
            else:
                # log10(x) / 2 -> log10(100) = 2 -> 2/2 = 1.0 (Score máximo com 100 músicas em comum)
                track_score = min(1.0, math.log10(max(1, count_common) + 1) / 2.0)
            
            # --- CÁLCULO FINAL COM FATOR DE CONFIANÇA ---
            
            # Pesos Base
            raw_score = (audio_similarity * 0.40) + (artist_similarity * 0.35) + (track_score * 0.25)
            
            # Fator de Confiança (Confidence Factor)
            # Penaliza se os usuários tiverem poucos dados no histórico.
            # Ex: Se tiver 10 músicas, confiança é baixa (0.2). Se tiver 50+, confiança é total (1.0).
            total_tracks_1 = profile1.total_tracks_played or 0
            total_tracks_2 = profile2.total_tracks_played or 0
            
            # Mínimo de 50 músicas para ter 100% de confiança no algoritmo
            confidence1 = min(1.0, total_tracks_1 / 50.0)
            confidence2 = min(1.0, total_tracks_2 / 50.0)
            
            # A confiança final é a média entre os dois usuários
            confidence_factor = (confidence1 + confidence2) / 2
            
            # Score Final Ajustado
            final_score = raw_score * confidence_factor
            
            # Garante limites
            final_score = min(1.0, max(0.0, final_score))
            
            # Persistência
            compatibility = CompatibilityScore(
                user1_id=user1_id,
                user2_id=user2_id,
                overall_score=final_score,
                audio_features_similarity=audio_similarity,
                artist_similarity=artist_similarity,
                common_tracks=count_common
            )
            
            self.db.add(compatibility)
            self.db.commit()
            
            return {
                'overall_score': final_score,
                'audio_features_similarity': audio_similarity,
                'artist_similarity': artist_similarity,
                'common_tracks': common_tracks,
                'breakdown': {
                    'audio_features': audio_similarity,
                    'artists': artist_similarity,
                    'common_tracks_score': track_score,
                    'confidence_factor': confidence_factor
                }
            }
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def _calculate_artist_similarity(self, artists1: List[Dict], artists2: List[Dict]) -> float:
        """Calcula similaridade de artistas com penalidade para listas pequenas"""
        if not artists1 or not artists2:
            return 0.0
        
        names1 = set([artist['name'] for artist in artists1])
        names2 = set([artist['name'] for artist in artists2])
        
        intersection = len(names1.intersection(names2))
        union = len(names1.union(names2))
        
        if union == 0:
            return 0.0
            
        base_jaccard = intersection / union
        
        # PENALIDADE: Se a união for pequena (ex: 2 artistas), o Jaccard é enganoso.
        # Exigimos pelo menos 20 artistas únicos na união para dar o valor "cheio".
        # Se union=2, confidence=0.1. Se union=20, confidence=1.0.
        confidence = min(1.0, union / 20.0)
        
        return base_jaccard * confidence
    
    def _get_common_tracks(self, user1_id: int, user2_id: int) -> List[Dict[str, Any]]:
        # ... (código igual ao anterior) ...
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
    
    async def perform_clustering(self, min_users: int = 2):
        # ... (código igual ao anterior) ...
        try:
            profiles = self.db.query(UserProfile).all()
            valid_profiles = [p for p in profiles if p.avg_energy is not None or p.avg_danceability is not None]
            
            if len(valid_profiles) < min_users:
                return {"message": f"Usuários insuficientes para clustering (mínimo: {min_users})"}
            
            features = []
            profile_ids = []
            
            for profile in valid_profiles:
                features.append([
                    profile.avg_danceability or 0,
                    profile.avg_energy or 0,
                    profile.avg_valence or 0,
                    profile.avg_acousticness or 0,
                    profile.avg_instrumentalness or 0,
                    profile.avg_liveness or 0,
                    profile.avg_speechiness or 0,
                    profile.avg_tempo or 0
                ])
                profile_ids.append(profile.id)
            
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            n_clusters = min(5, max(2, len(valid_profiles) // 3))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(features_scaled)
            
            for i, profile_id in enumerate(profile_ids):
                profile = self.db.query(UserProfile).filter(UserProfile.id == profile_id).first()
                if profile:
                    profile.cluster_id = int(cluster_labels[i])
            
            self.db.commit()
            
            return {
                "message": f"Clustering realizado com sucesso",
                "n_clusters": n_clusters,
                "n_users": len(valid_profiles)
            }
            
        except Exception as e:
            self.db.rollback()
            raise e
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
        try:
            listening_history = self.db.query(ListeningHistory).filter(ListeningHistory.user_id == user_id).all()
            if not listening_history: return None
            
            track_ids = [entry.track_id for entry in listening_history]
            tracks = self.db.query(Track).filter(Track.id.in_(track_ids)).all()
            
            durations = [t.duration_ms for t in tracks if t.duration_ms]
            avg_duration = sum(durations) / len(durations) if durations else 0.0

            # Collect audio features, only include tracks that have at least some features
            audio_features = []
            for track in tracks:
                has_any = any([track.danceability, track.energy, track.valence, track.tempo])
                if has_any:
                    audio_features.append([
                        track.danceability or 0.0, track.energy or 0.0, track.valence or 0.0,
                        track.acousticness or 0.0, track.instrumentalness or 0.0, track.liveness or 0.0,
                        track.speechiness or 0.0, track.tempo or 0.0
                    ])
            
            # Calculate average across all tracks
            if not audio_features:
                avg_features = np.zeros(8)
            else:
                avg_features = np.mean(np.array(audio_features), axis=0)
                
            top_genres = self._get_top_genres(user_id, sp)
            top_artists = self._get_top_artists(user_id)
            top_tracks = self._get_top_tracks(user_id)
            
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
            profile.total_tracks_played = len(listening_history)
            profile.unique_artists = len(set([t.artists for t in tracks if t.artists]))
            profile.unique_genres = len(top_genres)
            profile.avg_session_duration = float(avg_duration)
            
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except Exception as e:
            self.db.rollback()
            print(f"Erro profile: {e}")
            raise e

    def _get_top_genres(self, user_id: int, sp: Any = None, limit: int = 10) -> List[str]:
        if not sp: return []
        try:
            data = sp.current_user_top_artists(limit=50, time_range='medium_term')
            genres = []
            for a in data['items']: 
                if a.get('genres'): genres.extend(a['genres'])
            return [g for g, c in Counter(genres).most_common(limit)]
        except: return []

    def _get_top_artists(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        history = self.db.query(ListeningHistory).filter(ListeningHistory.user_id == user_id).all()
        counts = Counter()
        for h in history:
            if h.track.artists:
                for a in h.track.artists.split(','): counts[a.strip()] += 1
        return [{'name': a, 'play_count': c} for a, c in counts.most_common(limit)]

    def _get_top_tracks(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        history = self.db.query(ListeningHistory).filter(ListeningHistory.user_id == user_id).all()
        counts = Counter([h.track_id for h in history])
        tracks = []
        for tid, c in counts.most_common(limit):
            t = self.db.query(Track).filter(Track.id == tid).first()
            if t: tracks.append({'id': t.spotify_id, 'name': t.name, 'artists': t.artists, 'play_count': c})
        return tracks

    async def calculate_compatibility(self, user1_id: int, user2_id: int) -> Dict[str, Any]:
        try:
            self.db.query(CompatibilityScore).filter(
                ((CompatibilityScore.user1_id == user1_id) & (CompatibilityScore.user2_id == user2_id)) |
                ((CompatibilityScore.user1_id == user2_id) & (CompatibilityScore.user2_id == user1_id))
            ).delete()
            
            profile1 = self.db.query(UserProfile).filter(UserProfile.user_id == user1_id).first()
            profile2 = self.db.query(UserProfile).filter(UserProfile.user_id == user2_id).first()
            
            if not profile1 or not profile2:
                raise ValueError("Perfis não encontrados")
            
            def get_vector(p):
                # Normalize tempo by dividing by 200 so it's in similar scale to other features (0-1 range)
                return [
                    p.avg_danceability or 0, 
                    p.avg_energy or 0, 
                    p.avg_valence or 0,
                    p.avg_acousticness or 0, 
                    p.avg_instrumentalness or 0, 
                    p.avg_liveness or 0,
                    p.avg_speechiness or 0, 
                    (p.avg_tempo or 0) / 200.0
                ]

            audio_features1 = get_vector(profile1)
            audio_features2 = get_vector(profile2)
            
            # Handle edge case where user has no audio features
            if np.sum(audio_features1) == 0 or np.sum(audio_features2) == 0:
                audio_similarity = 0.0
            else:
                audio_similarity = cosine_similarity([audio_features1], [audio_features2])[0][0]
            
            artists1 = json.loads(profile1.top_artists) if profile1.top_artists else []
            artists2 = json.loads(profile2.top_artists) if profile2.top_artists else []
            artist_similarity = self._calculate_artist_similarity(artists1, artists2)
            
            common_tracks = self._get_common_tracks(user1_id, user2_id)
            count_common = len(common_tracks)
            
            # Use logarithmic scaling so having 10 common tracks isn't 10x better than 1
            if count_common == 0:
                track_score = 0.0
            else:
                track_score = min(1.0, math.log10(max(1, count_common) + 1) / 2.0)
            
            # Weighted combination: audio features matter most, then artists, then common tracks
            raw_score = (audio_similarity * 0.40) + (artist_similarity * 0.35) + (track_score * 0.25)
            
            # Confidence factor based on listening history - need at least 50 tracks for full confidence
            total_tracks_1 = profile1.total_tracks_played or 0
            total_tracks_2 = profile2.total_tracks_played or 0
            confidence = (min(1.0, total_tracks_1 / 50.0) + min(1.0, total_tracks_2 / 50.0)) / 2
            
            final_score = raw_score * confidence
            final_score = min(1.0, max(0.0, final_score))  # Clamp between 0 and 1
            
            compatibility = CompatibilityScore(
                user1_id=user1_id, user2_id=user2_id, overall_score=final_score,
                audio_features_similarity=audio_similarity, artist_similarity=artist_similarity,
                common_tracks=count_common
            )
            self.db.add(compatibility)
            self.db.commit()
            
            def make_feature_dict(p):
                return {
                    "danceability": p.avg_danceability or 0,
                    "energy": p.avg_energy or 0,
                    "valence": p.avg_valence or 0,
                    "acousticness": p.avg_acousticness or 0,
                    "instrumentalness": p.avg_instrumentalness or 0,
                    "liveness": p.avg_liveness or 0,
                    "speechiness": p.avg_speechiness or 0
                }

            features1_dict = make_feature_dict(profile1)
            features2_dict = make_feature_dict(profile2)

            return {
                'overall_score': final_score,
                'audio_features_similarity': audio_similarity,
                'artist_similarity': artist_similarity,
                'common_tracks': common_tracks,
                'breakdown': {
                    'audio_features': audio_similarity,
                    'artists': artist_similarity,
                    'common_tracks_score': track_score
                },
                'user1_features': features1_dict,
                'user2_features': features2_dict
            }
            
        except Exception as e:
            self.db.rollback()
            raise e

    def _calculate_artist_similarity(self, artists1: List[Dict], artists2: List[Dict]) -> float:
        # Jaccard similarity with penalty if both users have too few artists
        if not artists1 or not artists2: return 0.0
        names1 = set([a['name'] for a in artists1])
        names2 = set([a['name'] for a in artists2])
        intersection = len(names1.intersection(names2))
        union = len(names1.union(names2))
        if union == 0: return 0.0
        return (intersection / union) * min(1.0, union / 20.0)

    def _get_common_tracks(self, user1_id: int, user2_id: int) -> List[Dict[str, Any]]:
        tracks1 = set([e.track_id for e in self.db.query(ListeningHistory).filter(ListeningHistory.user_id == user1_id).all()])
        tracks2 = set([e.track_id for e in self.db.query(ListeningHistory).filter(ListeningHistory.user_id == user2_id).all()])
        common_ids = tracks1.intersection(tracks2)
        return [
            {'id': t.spotify_id, 'name': t.name, 'artists': t.artists} 
            for t in self.db.query(Track).filter(Track.id.in_(common_ids)).all()
        ]

# ... (outros métodos da classe acima: generate_user_profile, calculate_compatibility, etc)

    # CORREÇÃO 1: Mantenha este método COM O MESMO RECUO (TAB) dos outros métodos da classe
    async def perform_clustering(self, min_users: int = 2): # Reduzi para 2 para facilitar testes
        try:
            print("🚀 Iniciando Clusterização...")
            profiles = self.db.query(UserProfile).all()
            
            # Filtra usuários que já têm médias calculadas
            valid_profiles = [p for p in profiles if p.avg_energy is not None]
            
            print(f"👥 Usuários válidos: {len(valid_profiles)}")

            # CORREÇÃO 3: Retorna JSON seguro mesmo com poucos usuários
            if len(valid_profiles) < min_users:
                print("⚠️ Usuários insuficientes. Cancelando clusterização de forma segura.")
                return {
                    "status": "skipped",
                    "message": f"Clusterização requer {min_users} usuários. Encontrados: {len(valid_profiles)}",
                    "clusters_formed": 0
                }

            # Prepara dados para o Scikit-Learn
            features = []
            p_ids = []
            for p in valid_profiles:
                features.append([
                    float(p.avg_danceability or 0), 
                    float(p.avg_energy or 0), 
                    float(p.avg_valence or 0),
                    float(p.avg_acousticness or 0), 
                    float(p.avg_instrumentalness or 0), 
                    float(p.avg_liveness or 0),
                    float(p.avg_speechiness or 0), 
                    float(p.avg_tempo or 0)
                ])
                p_ids.append(p.id)
                
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Lógica dinâmica de K (clusters)
            n_samples = len(valid_profiles)
            if n_samples < 2:
                # Segurança extra caso min_users seja alterado externamente
                return {"status": "skipped", "message": "Dados insuficientes para K-Means."}

            desired_k = min(5, max(2, n_samples // 3))
            k = min(desired_k, n_samples - 1) # Garante que K < N
            
            if k < 2: k = 2 # Força mínimo de 2 se houver usuários suficientes

            print(f"🧮 Rodando KMeans com k={k} para {n_samples} usuários...")
            
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(features_scaled)
            
            # Atualiza no banco
            for index, pid in enumerate(p_ids):
                user_to_update = next((p for p in valid_profiles if p.id == pid), None)
                if user_to_update:
                    # Se der erro aqui, é porque a coluna cluster_id não existe no DB
                    user_to_update.cluster_id = int(labels[index])
            
            self.db.commit()
            print("✅ Clusterização salva com sucesso!")
            
            return {
                "status": "success",
                "message": f"Clusterização concluída! {k} grupos formados.",
                "clusters_formed": k
            }
            
        except Exception as e:
            self.db.rollback()
            # ISSO VAI MOSTRAR O ERRO REAL NO SEU TERMINAL:
            import traceback
            traceback.print_exc() 
            print(f"🚨 ERRO FATAL NO CLUSTERING: {str(e)}")
            # Retorna um erro legível em vez de estourar 500 (opcional, ajuda o front)
            return {"status": "error", "message": str(e)}
        try:
            profiles = self.db.query(UserProfile).all()
            
            # Filtra usuários que já têm médias calculadas
            valid_profiles = [p for p in profiles if p.avg_energy is not None]
            
            # LOG PARA DEBUG
            print(f"👥 Usuários válidos para cluster: {len(valid_profiles)} (Mínimo exigido: {min_users})")

            if len(valid_profiles) < min_users:
                return {"message": f"Poucos usuários com dados ({len(valid_profiles)}/{min_users}). Continue sincronizando!"}
            
            # Se tivermos poucos usuários (ex: teste com 1 ou 2), não dá pra clusterizar
            if len(valid_profiles) < 2:
                 return {"message": "Clusterização requer pelo menos 2 usuários com dados."}

            # Build feature matrix
            features = []
            p_ids = []
            for p in valid_profiles:
                features.append([
                    float(p.avg_danceability or 0), 
                    float(p.avg_energy or 0), 
                    float(p.avg_valence or 0),
                    float(p.avg_acousticness or 0), 
                    float(p.avg_instrumentalness or 0), 
                    float(p.avg_liveness or 0),
                    float(p.avg_speechiness or 0), 
                    float(p.avg_tempo or 0)
                ])
                p_ids.append(p.id)
                
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # CORREÇÃO DO ERRO MATEMÁTICO:
            # O número de clusters (k) não pode ser maior que o número de amostras (n_samples)
            n_samples = len(valid_profiles)
            
            # Tenta criar 1 cluster a cada 3 pessoas, mas no mínimo 2 e no máximo 5
            desired_k = min(5, max(2, n_samples // 3))
            
            # Proteção final: K não pode ser maior que N-1 (idealmente) ou N
            k = min(desired_k, n_samples)
            
            # Se k for igual a n_samples, cada um fica no seu cluster (edge case)
            if k >= n_samples:
                k = max(1, n_samples - 1) 
            
            if k < 2:
                 return {"message": "Dados insuficientes para formar múltiplos clusters."}

            print(f"🧮 Rodando KMeans com {k} clusters para {n_samples} usuários...")
            
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(features_scaled)
            
            # Atualização otimizada
            for index, pid in enumerate(p_ids):
                # Não precisa buscar no banco de novo se você já tem o objeto na lista valid_profiles
                # Mas para garantir que estamos na sessão certa:
                user_to_update = next((p for p in valid_profiles if p.id == pid), None)
                if user_to_update:
                    user_to_update.cluster_id = int(labels[index])
            
            self.db.commit()
            return {"message": f"Clusterização concluída! {k} grupos formados."}
            
        except Exception as e:
                self.db.rollback()
                
                # --- ADICIONE ISTO ---
                print("\n🚨 ERRO NO CLUSTERING ENCONTRADO:")
                import traceback
                traceback.print_exc() # Imprime o erro detalhado no terminal
                print("🚨 FIM DO ERRO\n")
                # ---------------------
                
                raise e
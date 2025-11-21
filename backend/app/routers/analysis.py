from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json

from app.database import get_db
from app.models import User, UserProfile, ListeningHistory, Track
from app.schemas import UserAnalysis
from app.utils import get_current_user
from app.services.analysis import AnalysisService

router = APIRouter()

@router.get("/my-profile", response_model=UserAnalysis)
async def get_my_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna análise completa do perfil musical do usuário"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil musical não encontrado. Execute a sincronização primeiro."
        )
    
    # Parse JSON fields
    top_genres = json.loads(profile.top_genres) if profile.top_genres else []
    top_artists = json.loads(profile.top_artists) if profile.top_artists else []
    top_tracks = json.loads(profile.top_tracks) if profile.top_tracks else []
    
    # Audio features profile
    audio_features_profile = {
        "danceability": profile.avg_danceability,
        "energy": profile.avg_energy,
        "valence": profile.avg_valence,
        "acousticness": profile.avg_acousticness,
        "instrumentalness": profile.avg_instrumentalness,
        "liveness": profile.avg_liveness,
        "speechiness": profile.avg_speechiness,
        "tempo": profile.avg_tempo
    }
    
    # Listening patterns
    listening_patterns = {
        "total_tracks_played": profile.total_tracks_played,
        "unique_artists": profile.unique_artists,
        "unique_genres": profile.unique_genres,
        "avg_session_duration": profile.avg_session_duration
    }
    
    return UserAnalysis(
        user_id=current_user.id,
        top_genres=top_genres,
        top_artists=top_artists,
        top_tracks=top_tracks,
        audio_features_profile=audio_features_profile,
        listening_patterns=listening_patterns,
        cluster_assignment=profile.cluster_id
    )

@router.get("/clusters")
async def get_cluster_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna análise dos clusters de usuários"""
    # Get all clusters
    clusters = db.query(UserProfile.cluster_id).filter(
        UserProfile.cluster_id.isnot(None)
    ).distinct().all()
    
    cluster_analysis = []
    for (cluster_id,) in clusters:
        # Get users in this cluster
        cluster_users = db.query(UserProfile).filter(
            UserProfile.cluster_id == cluster_id
        ).all()
        
        if cluster_users:
            # Calculate cluster averages
            avg_features = {
                "danceability": sum(p.avg_danceability for p in cluster_users if p.avg_danceability) / len(cluster_users),
                "energy": sum(p.avg_energy for p in cluster_users if p.avg_energy) / len(cluster_users),
                "valence": sum(p.avg_valence for p in cluster_users if p.avg_valence) / len(cluster_users),
                "acousticness": sum(p.avg_acousticness for p in cluster_users if p.avg_acousticness) / len(cluster_users),
                "instrumentalness": sum(p.avg_instrumentalness for p in cluster_users if p.avg_instrumentalness) / len(cluster_users),
                "liveness": sum(p.avg_liveness for p in cluster_users if p.avg_liveness) / len(cluster_users),
                "speechiness": sum(p.avg_speechiness for p in cluster_users if p.avg_speechiness) / len(cluster_users),
                "tempo": sum(p.avg_tempo for p in cluster_users if p.avg_tempo) / len(cluster_users)
            }
            
            cluster_analysis.append({
                "cluster_id": cluster_id,
                "user_count": len(cluster_users),
                "avg_features": avg_features,
                "is_current_user_cluster": any(p.user_id == current_user.id for p in cluster_users)
            })
    
    return {"clusters": cluster_analysis}

@router.post("/clustering")
async def perform_clustering(
    min_users: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executa clustering de usuários"""
    try:
        analysis_service = AnalysisService(db)
        result = await analysis_service.perform_clustering(min_users)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar clustering: {str(e)}"
        )

@router.get("/listening-patterns")
async def get_listening_patterns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna padrões de escuta do usuário"""
    # Get listening history
    listening_history = db.query(ListeningHistory).filter(
        ListeningHistory.user_id == current_user.id
    ).order_by(ListeningHistory.played_at.desc()).limit(1000).all()
    
    if not listening_history:
        return {"message": "Nenhum histórico de escuta encontrado"}
    
    # Analyze listening patterns
    patterns = {
        "total_sessions": len(listening_history),
        "time_distribution": {},
        "context_analysis": {},
        "recent_activity": []
    }
    
    # Time distribution (hour of day)
    hour_counts = {}
    for entry in listening_history:
        hour = entry.played_at.hour
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
    
    patterns["time_distribution"] = hour_counts
    
    # Context analysis
    context_counts = {}
    for entry in listening_history:
        context_type = entry.context_type or "unknown"
        context_counts[context_type] = context_counts.get(context_type, 0) + 1
    
    patterns["context_analysis"] = context_counts
    
    # Recent activity (last 10 tracks)
    recent_tracks = []
    for entry in listening_history[:10]:
        recent_tracks.append({
            "track_name": entry.track.name,
            "artists": entry.track.artists,
            "played_at": entry.played_at.isoformat(),
            "context": entry.context_name
        })
    
    patterns["recent_activity"] = recent_tracks
    
    return patterns

@router.get("/genre-analysis")
async def get_genre_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna análise de gêneros musicais"""
    # This would require genre information from Spotify API
    # For now, return a placeholder
    return {
        "message": "Análise de gêneros não implementada ainda",
        "note": "Requer integração com API do Spotify para obter informações de gênero"
    }

@router.get("/audio-features-radar")
async def get_audio_features_radar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna dados para gráfico radar de características de áudio"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_F,
            detail="Perfil musical não encontrado"
        )
    
    # Prepare data for radar chart
    radar_data = {
        "categories": [
            "Danceability", "Energy", "Valence", "Acousticness",
            "Instrumentalness", "Liveness", "Speechiness"
        ],
        "values": [
            profile.avg_danceability or 0,
            profile.avg_energy or 0,
            profile.avg_valence or 0,
            profile.avg_acousticness or 0,
            profile.avg_instrumentalness or 0,
            profile.avg_liveness or 0,
            profile.avg_speechiness or 0
        ]
    }
    
    return radar_data


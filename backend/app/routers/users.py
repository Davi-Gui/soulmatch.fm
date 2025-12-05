from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import spotipy
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, Track, ListeningHistory, UserProfile
from app.schemas import User as UserSchema, Track as TrackSchema, UserProfile as UserProfileSchema
from app.utils import get_current_user, get_spotify_client, refresh_spotify_token
from app.services.data_collection import DataCollectionService
from app.services.analysis import AnalysisService

router = APIRouter()

@router.get("/me", response_model=UserSchema)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Retorna o perfil do usuário atual"""
    return current_user

@router.get("/me/profile", response_model=UserProfileSchema)
async def get_my_musical_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna o perfil musical do usuário"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil musical não encontrado. Execute a análise primeiro."
        )
    return profile

@router.post("/me/sync")
async def sync_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sincroniza dados do usuário com o Spotify"""
    try:
        # Get Spotify client
        try:
            sp = get_spotify_client(current_user)
        except HTTPException:
            # Try to refresh token
            sp = refresh_spotify_token(current_user, db)
        
        # Initialize data collection service
        data_service = DataCollectionService(db)
        
        # Sync user data
        await data_service.sync_user_listening_history(current_user.id, sp)
        
        # Generate/update user profile
        # MUDANÇA AQUI: Passamos o 'sp' para o generate_user_profile
        analysis_service = AnalysisService(db)
        await analysis_service.generate_user_profile(current_user.id, sp)
        
        return {"message": "Dados sincronizados com sucesso"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao sincronizar dados: {str(e)}"
        )

@router.get("/me/tracks", response_model=List[TrackSchema])
async def get_my_tracks(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna as músicas mais tocadas do usuário"""
    try:
        sp = get_spotify_client(current_user)
        
        # Get top tracks from Spotify
        top_tracks = sp.current_user_top_tracks(limit=limit, offset=offset, time_range='medium_term')
        
        tracks = []
        for track_data in top_tracks['items']:
            # Check if track exists in database
            db_track = db.query(Track).filter(Track.spotify_id == track_data['id']).first()
            
            if not db_track:
                # Create new track
                db_track = Track(
                    spotify_id=track_data['id'],
                    name=track_data['name'],
                    artists=','.join([artist['name'] for artist in track_data['artists']]),
                    album=track_data['album']['name'],
                    duration_ms=track_data['duration_ms'],
                    popularity=track_data['popularity'],
                    explicit=track_data['explicit'],
                    preview_url=track_data.get('preview_url'),
                    external_urls=str(track_data['external_urls'])
                )
                db.add(db_track)
                db.commit()
                db.refresh(db_track)
            
            tracks.append(db_track)
        
        return tracks
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter músicas: {str(e)}"
        )

@router.get("/me/artists")
async def get_my_artists(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Retorna os artistas mais ouvidos do usuário"""
    try:
        sp = get_spotify_client(current_user)
        
        top_artists = sp.current_user_top_artists(limit=limit, offset=offset, time_range='medium_term')
        
        artists = []
        for artist_data in top_artists['items']:
            artists.append({
                "id": artist_data['id'],
                "name": artist_data['name'],
                "genres": artist_data['genres'],
                "popularity": artist_data['popularity'],
                "followers": artist_data['followers']['total'],
                "image_url": artist_data['images'][0]['url'] if artist_data['images'] else None,
                "external_urls": artist_data['external_urls']
            })
        
        return {"artists": artists, "total": top_artists['total']}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter artistas: {str(e)}"
        )

@router.get("/me/recent")
async def get_recent_tracks(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Retorna as músicas tocadas recentemente"""
    try:
        sp = get_spotify_client(current_user)
        
        recent_tracks = sp.current_user_recently_played(limit=limit)
        
        tracks = []
        for item in recent_tracks['items']:
            track_data = item['track']
            tracks.append({
                "id": track_data['id'],
                "name": track_data['name'],
                "artists": [artist['name'] for artist in track_data['artists']],
                "album": track_data['album']['name'],
                "played_at": item['played_at'],
                "context": item.get('context', {}),
                "external_urls": track_data['external_urls']
            })
        
        return {"tracks": tracks}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter músicas recentes: {str(e)}"
        )

@router.get("/search", response_model=List[UserSchema])
async def search_users(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Busca usuários pelo nome (case insensitive)"""
    if len(query) < 2:
        return []
        
    # Busca por nome similar, excluindo o próprio usuário logado
    users = db.query(User).filter(
        User.display_name.ilike(f"%{query}%"),
        User.id != current_user.id
    ).limit(10).all()
    
    return users

@router.get("/{user_id}", response_model=UserSchema)
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna o perfil de um usuário específico"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user


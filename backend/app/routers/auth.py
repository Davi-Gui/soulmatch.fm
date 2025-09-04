from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import json

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, User as UserSchema
from app.config import settings
from app.utils import create_access_token, get_current_user

router = APIRouter()

# Spotify OAuth configuration
sp_oauth = SpotifyOAuth(
    client_id=settings.spotify_client_id,
    client_secret=settings.spotify_client_secret,
    redirect_uri=settings.spotify_redirect_uri,
    scope="user-read-recently-played user-top-read user-read-private user-read-email"
)

@router.get("/login")
async def spotify_login():
    """Inicia o processo de autenticação com Spotify"""
    auth_url = sp_oauth.get_authorize_url()
    return {"auth_url": auth_url}

@router.get("/callback")
async def spotify_callback(code: str, db: Session = Depends(get_db)):
    """Callback do Spotify OAuth"""
    try:
        # Exchange code for token
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        refresh_token = token_info.get('refresh_token')
        expires_at = datetime.now() + timedelta(seconds=token_info['expires_in'])
        
        # Get user info from Spotify
        sp = spotipy.Spotify(auth=access_token)
        spotify_user = sp.current_user()
        
        # Check if user exists in database
        db_user = db.query(User).filter(User.spotify_id == spotify_user['id']).first()
        
        if db_user:
            # Update existing user
            db_user.access_token = access_token
            db_user.refresh_token = refresh_token
            db_user.token_expires_at = expires_at
            db_user.display_name = spotify_user.get('display_name')
            db_user.email = spotify_user.get('email')
            db_user.country = spotify_user.get('country')
            db_user.followers = spotify_user.get('followers', {}).get('total', 0)
            if spotify_user.get('images'):
                db_user.image_url = spotify_user['images'][0]['url']
        else:
            # Create new user
            db_user = User(
                spotify_id=spotify_user['id'],
                display_name=spotify_user.get('display_name'),
                email=spotify_user.get('email'),
                country=spotify_user.get('country'),
                followers=spotify_user.get('followers', {}).get('total', 0),
                image_url=spotify_user['images'][0]['url'] if spotify_user.get('images') else None,
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=expires_at
            )
            db.add(db_user)
        
        db.commit()
        db.refresh(db_user)
        
        # Create JWT token for our API
        jwt_token = create_access_token(data={"sub": str(db_user.id)})
        
        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": UserSchema.from_orm(db_user)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro na autenticação: {str(e)}"
        )

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Retorna informações do usuário atual"""
    return UserSchema.from_orm(current_user)

@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Atualiza o token de acesso do Spotify"""
    try:
        if not current_user.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token não disponível"
            )
        
        # Refresh Spotify token
        token_info = sp_oauth.refresh_access_token(current_user.refresh_token)
        access_token = token_info['access_token']
        expires_at = datetime.now() + timedelta(seconds=token_info['expires_in'])
        
        # Update user in database
        current_user.access_token = access_token
        current_user.token_expires_at = expires_at
        db.commit()
        
        return {"message": "Token atualizado com sucesso"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar token: {str(e)}"
        )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Remove tokens do usuário"""
    current_user.access_token = None
    current_user.refresh_token = None
    current_user.token_expires_at = None
    db.commit()
    
    return {"message": "Logout realizado com sucesso"}


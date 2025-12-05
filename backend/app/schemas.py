from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    spotify_id: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    followers: Optional[int] = 0
    image_url: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserInfo(BaseModel):
    id: int
    display_name: Optional[str] = None
    image_url: Optional[str] = None
    
    class Config:
        from_attributes = True

# Track Schemas
class TrackBase(BaseModel):
    spotify_id: str
    name: str
    artists: Optional[str] = None
    album: Optional[str] = None
    duration_ms: Optional[int] = None
    popularity: Optional[int] = None
    explicit: Optional[bool] = False
    preview_url: Optional[str] = None
    external_urls: Optional[str] = None

class TrackCreate(TrackBase):
    # Audio features
    danceability: Optional[float] = None
    energy: Optional[float] = None
    key: Optional[int] = None
    loudness: Optional[float] = None
    mode: Optional[int] = None
    speechiness: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    valence: Optional[float] = None
    tempo: Optional[float] = None
    time_signature: Optional[int] = None

class Track(TrackBase):
    id: int
    danceability: Optional[float] = None
    energy: Optional[float] = None
    key: Optional[int] = None
    loudness: Optional[float] = None
    mode: Optional[int] = None
    speechiness: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    valence: Optional[float] = None
    tempo: Optional[float] = None
    time_signature: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Listening History Schemas
class ListeningHistoryBase(BaseModel):
    user_id: int
    track_id: int
    played_at: datetime
    context_type: Optional[str] = None
    context_name: Optional[str] = None

class ListeningHistoryCreate(ListeningHistoryBase):
    pass

class ListeningHistory(ListeningHistoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Compatibility Score Schemas
class CompatibilityScoreBase(BaseModel):
    user1_id: int
    user2_id: int
    overall_score: float
    genre_similarity: Optional[float] = None
    artist_similarity: Optional[float] = None
    audio_features_similarity: Optional[float] = None
    listening_time_similarity: Optional[float] = None
    common_tracks: Optional[int] = 0

class CompatibilityScoreCreate(CompatibilityScoreBase):
    pass

class CompatibilityScore(CompatibilityScoreBase):
    id: int
    analysis_date: datetime
    user1: Optional[UserInfo] = None
    user2: Optional[UserInfo] = None
    
    class Config:
        from_attributes = True

# User Profile Schemas
class UserProfileBase(BaseModel):
    user_id: int
    top_genres: Optional[str] = None
    top_artists: Optional[str] = None
    top_tracks: Optional[str] = None
    avg_danceability: Optional[float] = None
    avg_energy: Optional[float] = None
    avg_valence: Optional[float] = None
    avg_acousticness: Optional[float] = None
    avg_instrumentalness: Optional[float] = None
    avg_liveness: Optional[float] = None
    avg_speechiness: Optional[float] = None
    avg_tempo: Optional[float] = None
    total_tracks_played: Optional[int] = 0
    unique_artists: Optional[int] = 0
    unique_genres: Optional[int] = 0
    avg_session_duration: Optional[float] = None
    cluster_id: Optional[int] = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfile(UserProfileBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Analysis Schemas
class CompatibilityAnalysis(BaseModel):
    user1_id: int
    user2_id: int
    overall_score: float
    breakdown: Dict[str, float]
    common_tracks: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]

class UserAnalysis(BaseModel):
    user_id: int
    top_genres: List[str]
    top_artists: List[Dict[str, Any]]
    top_tracks: List[Dict[str, Any]]
    audio_features_profile: Dict[str, float]
    listening_patterns: Dict[str, Any]
    cluster_assignment: Optional[int] = None

# Spotify API Schemas
class SpotifyTrack(BaseModel):
    id: str
    name: str
    artists: List[Dict[str, Any]]
    album: Dict[str, Any]
    duration_ms: int
    popularity: int
    explicit: bool
    preview_url: Optional[str] = None
    external_urls: Dict[str, str]

class SpotifyAudioFeatures(BaseModel):
    danceability: float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float
    time_signature: int

class SpotifyUser(BaseModel):
    id: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    followers: Dict[str, int]
    images: List[Dict[str, Any]]


from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    country = Column(String, nullable=True)
    followers = Column(Integer, default=0)
    image_url = Column(String, nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    listening_history = relationship("ListeningHistory", back_populates="user")
    compatibility_scores = relationship("CompatibilityScore", back_populates="user1")

class Track(Base):
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    artists = Column(Text, nullable=True)  # JSON string of artists
    album = Column(String, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    popularity = Column(Integer, nullable=True)
    explicit = Column(Boolean, default=False)
    preview_url = Column(String, nullable=True)
    external_urls = Column(Text, nullable=True)  # JSON string
    
    # Audio features
    danceability = Column(Float, nullable=True)
    energy = Column(Float, nullable=True)
    key = Column(Integer, nullable=True)
    loudness = Column(Float, nullable=True)
    mode = Column(Integer, nullable=True)
    speechiness = Column(Float, nullable=True)
    acousticness = Column(Float, nullable=True)
    instrumentalness = Column(Float, nullable=True)
    liveness = Column(Float, nullable=True)
    valence = Column(Float, nullable=True)
    tempo = Column(Float, nullable=True)
    time_signature = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    listening_history = relationship("ListeningHistory", back_populates="track")

class ListeningHistory(Base):
    __tablename__ = "listening_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    played_at = Column(DateTime, nullable=False)
    context_type = Column(String, nullable=True)  # playlist, album, artist, etc.
    context_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="listening_history")
    track = relationship("Track", back_populates="listening_history")

class CompatibilityScore(Base):
    __tablename__ = "compatibility_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    overall_score = Column(Float, nullable=False)
    genre_similarity = Column(Float, nullable=True)
    artist_similarity = Column(Float, nullable=True)
    audio_features_similarity = Column(Float, nullable=True)
    listening_time_similarity = Column(Float, nullable=True)
    common_tracks = Column(Integer, default=0)
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="compatibility_scores")
    user2 = relationship("User", foreign_keys=[user2_id])

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Musical preferences
    top_genres = Column(Text, nullable=True)  # JSON string
    top_artists = Column(Text, nullable=True)  # JSON string
    top_tracks = Column(Text, nullable=True)  # JSON string
    
    # Audio features averages
    avg_danceability = Column(Float, nullable=True)
    avg_energy = Column(Float, nullable=True)
    avg_valence = Column(Float, nullable=True)
    avg_acousticness = Column(Float, nullable=True)
    avg_instrumentalness = Column(Float, nullable=True)
    avg_liveness = Column(Float, nullable=True)
    avg_speechiness = Column(Float, nullable=True)
    avg_tempo = Column(Float, nullable=True)
    
    # Listening patterns
    total_tracks_played = Column(Integer, default=0)
    unique_artists = Column(Integer, default=0)
    unique_genres = Column(Integer, default=0)
    avg_session_duration = Column(Float, nullable=True)
    
    # Clustering information
    cluster_id = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.config import settings
import os

from app.routers import auth, users, compatibility, analysis
from app.database import engine, Base

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SoulMatch.fm API",
    description="API para análise de compatibilidade musical entre usuários do Spotify",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(compatibility.router, prefix="/compatibility", tags=["compatibility"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])

@app.get("/")
async def root():
    return {"message": "SoulMatch.fm API - Análise de Compatibilidade Musical"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import User, CompatibilityScore, UserProfile
from app.schemas import CompatibilityScore as CompatibilityScoreSchema, CompatibilityAnalysis
from app.utils import get_current_user
from app.services.analysis import AnalysisService

router = APIRouter()

@router.post("/calculate/{user2_id}", response_model=CompatibilityAnalysis)
async def calculate_compatibility(
    user2_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calcula compatibilidade entre o usuário atual e outro usuário"""
    if current_user.id == user2_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível calcular compatibilidade consigo mesmo"
        )
    
    user2 = db.query(User).filter(User.id == user2_id).first()
    if not user2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Both users need to have synced their data first
    profile1 = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    profile2 = db.query(UserProfile).filter(UserProfile.user_id == user2_id).first()
    
    if not profile1 or not profile2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Um ou ambos os usuários não possuem perfil musical. Execute a sincronização primeiro."
        )
    
    try:
        analysis_service = AnalysisService(db)
        compatibility_data = await analysis_service.calculate_compatibility(current_user.id, user2_id)
        
        return CompatibilityAnalysis(
            user1_id=current_user.id,
            user2_id=user2_id,
            overall_score=compatibility_data['overall_score'],
            breakdown=compatibility_data['breakdown'],
            common_tracks=compatibility_data['common_tracks'],
            recommendations=[],
            user1_features=compatibility_data.get('user1_features'),
            user2_features=compatibility_data.get('user2_features')
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular compatibilidade: {str(e)}"
        )

@router.get("/scores", response_model=List[CompatibilityScoreSchema])
async def get_compatibility_scores(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna os scores de compatibilidade do usuário atual"""
    scores = db.query(CompatibilityScore).filter(
        (CompatibilityScore.user1_id == current_user.id) | 
        (CompatibilityScore.user2_id == current_user.id)
    ).order_by(CompatibilityScore.overall_score.desc()).offset(offset).limit(limit).all()
    
    return scores

@router.get("/top-matches", response_model=List[CompatibilityScoreSchema])
async def get_top_matches(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna os melhores matches do usuário atual com detalhes dos usuários"""
    # Use joinedload to avoid N+1 query problem when accessing user data
    scores = db.query(CompatibilityScore).options(
        joinedload(CompatibilityScore.user1),
        joinedload(CompatibilityScore.user2)
    ).filter(
        (CompatibilityScore.user1_id == current_user.id) | 
        (CompatibilityScore.user2_id == current_user.id)
    ).order_by(CompatibilityScore.overall_score.desc()).limit(limit).all()
    
    return scores

@router.get("/with/{user_id}", response_model=CompatibilityScoreSchema)
async def get_compatibility_with_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna o score de compatibilidade com um usuário específico"""
    score = db.query(CompatibilityScore).filter(
        ((CompatibilityScore.user1_id == current_user.id) & (CompatibilityScore.user2_id == user_id)) |
        ((CompatibilityScore.user1_id == user_id) & (CompatibilityScore.user2_id == current_user.id))
    ).first()
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score de compatibilidade não encontrado"
        )
    
    return score

@router.get("/similar-users")
async def get_similar_users(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna usuários com perfil musical similar"""
    current_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not current_profile or current_profile.cluster_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não foi clusterizado. Execute a análise de clustering primeiro."
        )
    
    similar_profiles = db.query(UserProfile).filter(
        UserProfile.cluster_id == current_profile.cluster_id,
        UserProfile.user_id != current_user.id
    ).limit(limit).all()
    
    similar_users = []
    for profile in similar_profiles:
        user = db.query(User).filter(User.id == profile.user_id).first()
        if user:
            similar_users.append({
                "id": user.id,
                "display_name": user.display_name,
                "image_url": user.image_url,
                "cluster_id": profile.cluster_id
            })
    
    return {"similar_users": similar_users}

@router.delete("/scores/{score_id}")
async def delete_compatibility_score(
    score_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove um score de compatibilidade"""
    score = db.query(CompatibilityScore).filter(
        CompatibilityScore.id == score_id,
        (CompatibilityScore.user1_id == current_user.id) | 
        (CompatibilityScore.user2_id == current_user.id)
    ).first()
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score de compatibilidade não encontrado"
        )
    
    db.delete(score)
    db.commit()
    
    return {"message": "Score de compatibilidade removido com sucesso"}


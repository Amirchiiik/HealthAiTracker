from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.schemas import (
    HealthAnalysisResponse,
    ChatInteractionResponse,
    UserHistoryResponse,
    InteractionType
)
from app.services.database_service import DatabaseService

router = APIRouter()

@router.get("/me/analyses", response_model=List[HealthAnalysisResponse])
def get_my_health_analyses(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's health analysis history"""
    
    analyses = DatabaseService.get_user_health_analyses(
        db, current_user.id, limit, offset
    )
    
    return [HealthAnalysisResponse.from_orm(analysis) for analysis in analyses]

@router.get("/me/analyses/{analysis_id}", response_model=HealthAnalysisResponse)
def get_my_health_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific health analysis by ID"""
    
    analysis = DatabaseService.get_health_analysis_by_id(
        db, analysis_id, current_user.id
    )
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health analysis not found"
        )
    
    return HealthAnalysisResponse.from_orm(analysis)

@router.delete("/me/analyses/{analysis_id}")
def delete_my_health_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a health analysis"""
    
    success = DatabaseService.delete_health_analysis(
        db, analysis_id, current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health analysis not found"
        )
    
    return {"message": "Health analysis deleted successfully"}

@router.get("/me/chats", response_model=List[ChatInteractionResponse])
def get_my_chat_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    interaction_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's chat interaction history"""
    
    # Validate interaction type if provided
    if interaction_type and interaction_type not in [t.value for t in InteractionType]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid interaction type. Must be one of: {[t.value for t in InteractionType]}"
        )
    
    chats = DatabaseService.get_user_chat_interactions(
        db, current_user.id, limit, offset, interaction_type
    )
    
    return [ChatInteractionResponse.from_orm(chat) for chat in chats]

@router.get("/me/history", response_model=UserHistoryResponse)
def get_my_complete_history(
    analyses_limit: int = Query(20, ge=1, le=50),
    chats_limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete user history including both analyses and chats"""
    
    # Get recent analyses and chats
    analyses = DatabaseService.get_user_health_analyses(
        db, current_user.id, analyses_limit, 0
    )
    chats = DatabaseService.get_user_chat_interactions(
        db, current_user.id, chats_limit, 0
    )
    
    # Get total counts
    total_analyses = DatabaseService.count_user_analyses(db, current_user.id)
    total_chats = DatabaseService.count_user_chats(db, current_user.id)
    
    return UserHistoryResponse(
        health_analyses=[HealthAnalysisResponse.from_orm(a) for a in analyses],
        chat_interactions=[ChatInteractionResponse.from_orm(c) for c in chats],
        total_analyses=total_analyses,
        total_chats=total_chats
    )

@router.get("/me/activity")
def get_my_recent_activity(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent activity summary"""
    
    activity = DatabaseService.get_recent_user_activity(
        db, current_user.id, days
    )
    
    return {
        "user_id": current_user.id,
        "user_name": current_user.full_name,
        "activity": activity
    }

@router.get("/me/stats")
def get_my_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics and metrics"""
    
    total_analyses = DatabaseService.count_user_analyses(db, current_user.id)
    total_chats = DatabaseService.count_user_chats(db, current_user.id)
    
    # Get recent activity
    recent_activity = DatabaseService.get_recent_user_activity(db, current_user.id, 30)
    
    # Calculate engagement metrics
    engagement_rate = 0
    if total_analyses > 0:
        engagement_rate = (recent_activity["recent_analyses"] / total_analyses) * 100
    
    return {
        "user_id": current_user.id,
        "total_health_analyses": total_analyses,
        "total_chat_interactions": total_chats,
        "recent_30_days": recent_activity,
        "engagement_rate_30d": round(engagement_rate, 2),
        "account_age_days": (current_user.created_at - current_user.created_at).days if current_user.created_at else 0
    } 
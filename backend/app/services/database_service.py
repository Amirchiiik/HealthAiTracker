from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import User, HealthAnalysis, ChatInteraction, DiseasePrediction
from app.schemas import (
    HealthAnalysisCreate, 
    ChatInteractionCreate,
    HealthAnalysisResponse,
    ChatInteractionResponse,
    InteractionType,
    DiseasePredictionCreate,
    DiseasePredictionResponse
)

class DatabaseService:
    """Database service for managing user data"""
    
    @staticmethod
    def create_health_analysis(
        db: Session, 
        user_id: int, 
        analysis_data: HealthAnalysisCreate
    ) -> HealthAnalysis:
        """Create a new health analysis record"""
        
        db_analysis = HealthAnalysis(
            user_id=user_id,
            filename=analysis_data.filename,
            extracted_text=analysis_data.extracted_text,
            metrics=analysis_data.metrics,
            overall_summary=analysis_data.overall_summary,
            analysis_data=analysis_data.analysis_data
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        return db_analysis
    
    @staticmethod
    def get_user_health_analyses(
        db: Session, 
        user_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[HealthAnalysis]:
        """Get user's health analyses with pagination"""
        
        return db.query(HealthAnalysis)\
            .filter(HealthAnalysis.user_id == user_id)\
            .order_by(desc(HealthAnalysis.created_at))\
            .offset(offset)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_health_analysis_by_id(
        db: Session, 
        analysis_id: int, 
        user_id: int
    ) -> Optional[HealthAnalysis]:
        """Get specific health analysis by ID (ensuring user ownership)"""
        
        return db.query(HealthAnalysis)\
            .filter(
                HealthAnalysis.id == analysis_id,
                HealthAnalysis.user_id == user_id
            )\
            .first()
    
    @staticmethod
    def create_chat_interaction(
        db: Session,
        user_id: int,
        interaction_data: ChatInteractionCreate
    ) -> ChatInteraction:
        """Create a new chat interaction record"""
        
        db_interaction = ChatInteraction(
            user_id=user_id,
            prompt=interaction_data.prompt,
            response=interaction_data.response,
            interaction_type=interaction_data.interaction_type.value
        )
        
        db.add(db_interaction)
        db.commit()
        db.refresh(db_interaction)
        return db_interaction
    
    @staticmethod
    def get_user_chat_interactions(
        db: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        interaction_type: Optional[str] = None
    ) -> List[ChatInteraction]:
        """Get user's chat interactions with optional filtering"""
        
        query = db.query(ChatInteraction)\
            .filter(ChatInteraction.user_id == user_id)
        
        if interaction_type:
            query = query.filter(ChatInteraction.interaction_type == interaction_type)
        
        return query.order_by(desc(ChatInteraction.created_at))\
            .offset(offset)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def count_user_analyses(db: Session, user_id: int) -> int:
        """Count total health analyses for user"""
        return db.query(HealthAnalysis)\
            .filter(HealthAnalysis.user_id == user_id)\
            .count()
    
    @staticmethod
    def count_user_chats(db: Session, user_id: int) -> int:
        """Count total chat interactions for user"""
        return db.query(ChatInteraction)\
            .filter(ChatInteraction.user_id == user_id)\
            .count()
    
    @staticmethod
    def delete_health_analysis(
        db: Session,
        analysis_id: int,
        user_id: int
    ) -> bool:
        """Delete a health analysis (ensuring user ownership)"""
        
        analysis = db.query(HealthAnalysis)\
            .filter(
                HealthAnalysis.id == analysis_id,
                HealthAnalysis.user_id == user_id
            )\
            .first()
        
        if analysis:
            db.delete(analysis)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_recent_user_activity(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> dict:
        """Get recent user activity summary"""
        from datetime import datetime, timedelta
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        recent_analyses = db.query(HealthAnalysis)\
            .filter(
                HealthAnalysis.user_id == user_id,
                HealthAnalysis.created_at >= since_date
            )\
            .count()
        
        recent_chats = db.query(ChatInteraction)\
            .filter(
                ChatInteraction.user_id == user_id,
                ChatInteraction.created_at >= since_date
            )\
            .count()
        
        return {
            "recent_analyses": recent_analyses,
            "recent_chats": recent_chats,
            "period_days": days
        }

# Helper functions for easy access
def save_analysis_to_history(
    db: Session,
    user_id: int,
    filename: Optional[str],
    extracted_text: str,
    metrics: list,
    overall_summary: str,
    analysis_data: dict
) -> HealthAnalysis:
    """Save a health analysis to user's history"""
    
    analysis_create = HealthAnalysisCreate(
        filename=filename,
        extracted_text=extracted_text,
        metrics=metrics,
        overall_summary=overall_summary,
        analysis_data=analysis_data
    )
    
    return DatabaseService.create_health_analysis(db, user_id, analysis_create)

def save_chat_to_history(
    db: Session,
    user_id: int,
    prompt: str,
    response: str,
    interaction_type: InteractionType = InteractionType.GENERAL
) -> ChatInteraction:
    """Save a chat interaction to user's history"""
    
    chat_create = ChatInteractionCreate(
        prompt=prompt,
        response=response,
        interaction_type=interaction_type
    )
    
    return DatabaseService.create_chat_interaction(db, user_id, chat_create)

    @staticmethod
    def create_disease_prediction(
        db: Session,
        user_id: int,
        prediction_data: DiseasePredictionCreate
    ) -> DiseasePrediction:
        """Create a new disease prediction record"""
        
        db_prediction = DiseasePrediction(
            user_id=user_id,
            health_analysis_id=prediction_data.health_analysis_id,
            predicted_diseases=[disease.dict() for disease in prediction_data.predicted_diseases],
            risk_factors=[factor.dict() for factor in prediction_data.risk_factors],
            confidence_scores=prediction_data.confidence_scores,
            overall_risk_level=prediction_data.overall_risk_level.value,
            recommendations=prediction_data.recommendations,
            medical_disclaimer=prediction_data.medical_disclaimer
        )
        
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        return db_prediction
    
    @staticmethod
    def get_user_disease_predictions(
        db: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[DiseasePrediction]:
        """Get user's disease predictions with pagination"""
        
        return db.query(DiseasePrediction)\
            .filter(DiseasePrediction.user_id == user_id)\
            .order_by(desc(DiseasePrediction.created_at))\
            .offset(offset)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_disease_prediction_by_id(
        db: Session,
        prediction_id: int,
        user_id: int
    ) -> Optional[DiseasePrediction]:
        """Get specific disease prediction by ID (ensuring user ownership)"""
        
        return db.query(DiseasePrediction)\
            .filter(
                DiseasePrediction.id == prediction_id,
                DiseasePrediction.user_id == user_id
            )\
            .first()
    
    @staticmethod
    def count_user_predictions(db: Session, user_id: int) -> int:
        """Count total disease predictions for user"""
        return db.query(DiseasePrediction)\
            .filter(DiseasePrediction.user_id == user_id)\
            .count()
    
    @staticmethod
    def count_user_predictions_by_risk_level(
        db: Session, 
        user_id: int, 
        risk_level: str
    ) -> int:
        """Count user predictions by risk level"""
        return db.query(DiseasePrediction)\
            .filter(
                DiseasePrediction.user_id == user_id,
                DiseasePrediction.overall_risk_level == risk_level
            )\
            .count()
    
    @staticmethod
    def get_latest_user_prediction(
        db: Session,
        user_id: int
    ) -> Optional[DiseasePrediction]:
        """Get user's most recent disease prediction"""
        
        return db.query(DiseasePrediction)\
            .filter(DiseasePrediction.user_id == user_id)\
            .order_by(desc(DiseasePrediction.created_at))\
            .first()
    
    @staticmethod
    def delete_disease_prediction(
        db: Session,
        prediction_id: int,
        user_id: int
    ) -> bool:
        """Delete a disease prediction (ensuring user ownership)"""
        
        prediction = db.query(DiseasePrediction)\
            .filter(
                DiseasePrediction.id == prediction_id,
                DiseasePrediction.user_id == user_id
            )\
            .first()
        
        if prediction:
            db.delete(prediction)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_user_prediction_statistics(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> dict:
        """Get user's disease prediction statistics"""
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        recent_predictions = db.query(DiseasePrediction)\
            .filter(
                DiseasePrediction.user_id == user_id,
                DiseasePrediction.created_at >= since_date
            )\
            .count()
        
        high_risk_predictions = db.query(DiseasePrediction)\
            .filter(
                DiseasePrediction.user_id == user_id,
                DiseasePrediction.overall_risk_level == "high",
                DiseasePrediction.created_at >= since_date
            )\
            .count()
        
        return {
            "recent_predictions": recent_predictions,
            "high_risk_predictions": high_risk_predictions,
            "period_days": days
        }

# Helper function for disease predictions
def save_disease_prediction_to_history(
    db: Session,
    user_id: int,
    prediction_data: DiseasePredictionCreate
) -> DiseasePrediction:
    """Save a disease prediction to user's history"""
    
    return DatabaseService.create_disease_prediction(db, user_id, prediction_data) 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
from datetime import datetime, timedelta

from app.database import get_db
from app.auth import get_current_user
from app.models import User, DiseasePrediction
from app.schemas import (
    DiseasePredictionRequest, DiseasePredictionResponse, 
    DiseasePredictionHistory, MetricInput
)
from app.services.disease_prediction_service import DiseasePredictionService
from app.services.llm_service import generate_disease_explanation

router = APIRouter(prefix="/predict", tags=["Disease Prediction"])
logger = logging.getLogger(__name__)

# Rate limiting: 10 predictions per hour per user
RATE_LIMIT_PREDICTIONS = 10
RATE_LIMIT_WINDOW_HOURS = 1

def check_rate_limit(user_id: int, db: Session):
    """Check if user has exceeded rate limit for predictions."""
    cutoff_time = datetime.utcnow() - timedelta(hours=RATE_LIMIT_WINDOW_HOURS)
    
    recent_predictions = db.query(DiseasePrediction).filter(
        DiseasePrediction.user_id == user_id,
        DiseasePrediction.created_at >= cutoff_time
    ).count()
    
    if recent_predictions >= RATE_LIMIT_PREDICTIONS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_PREDICTIONS} predictions per hour allowed."
        )

@router.post("/disease", response_model=DiseasePredictionResponse)
async def predict_disease_risk(
    request: DiseasePredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predict disease risks based on health metrics.
    
    This endpoint analyzes health metrics and predicts potential disease risks
    using rule-based algorithms and medical knowledge base.
    
    **Rate Limit**: 10 predictions per hour per user
    
    **Medical Disclaimer**: Results are for informational purposes only.
    Always consult healthcare professionals for medical decisions.
    """
    try:
        # Check rate limiting
        check_rate_limit(current_user.id, db)
        
        logger.info(f"Disease prediction request from user {current_user.id} with {len(request.metrics)} metrics")
        
        # Initialize prediction service
        prediction_service = DiseasePredictionService()
        
        # Perform disease prediction
        prediction_data = prediction_service.predict_diseases(request.metrics)
        
        # Generate AI explanation if requested
        ai_explanation = None
        if request.include_explanations:
            try:
                ai_explanation = await generate_disease_explanation(
                    prediction_data.predicted_diseases,
                    prediction_data.overall_risk_level
                )
            except Exception as e:
                logger.warning(f"Failed to generate AI explanation: {e}")
                ai_explanation = "AI explanation unavailable at this time."
        
        # Save prediction to database
        db_prediction = DiseasePrediction(
            user_id=current_user.id,
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
        
        logger.info(f"Disease prediction completed for user {current_user.id}. Risk level: {prediction_data.overall_risk_level.value}")
        
        # Return response
        return DiseasePredictionResponse(
            id=db_prediction.id,
            user_id=current_user.id,
            health_analysis_id=None,
            predicted_diseases=prediction_data.predicted_diseases,
            overall_risk_level=prediction_data.overall_risk_level,
            recommendations=prediction_data.recommendations,
            medical_disclaimer=prediction_data.medical_disclaimer,
            ai_explanation=ai_explanation,
            created_at=db_prediction.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disease prediction failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Disease prediction service temporarily unavailable. Please try again later."
        )

@router.get("/history", response_model=DiseasePredictionHistory)
async def get_prediction_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's disease prediction history.
    
    Returns a paginated list of all disease predictions made by the current user,
    including risk level statistics.
    """
    try:
        # Get total count
        total_count = db.query(DiseasePrediction).filter(
            DiseasePrediction.user_id == current_user.id
        ).count()
        
        # Get predictions with pagination
        predictions = db.query(DiseasePrediction).filter(
            DiseasePrediction.user_id == current_user.id
        ).order_by(DiseasePrediction.created_at.desc()).offset(offset).limit(limit).all()
        
        # Count risk levels
        high_risk_count = db.query(DiseasePrediction).filter(
            DiseasePrediction.user_id == current_user.id,
            DiseasePrediction.overall_risk_level == "high"
        ).count()
        
        moderate_risk_count = db.query(DiseasePrediction).filter(
            DiseasePrediction.user_id == current_user.id,
            DiseasePrediction.overall_risk_level == "moderate"
        ).count()
        
        low_risk_count = db.query(DiseasePrediction).filter(
            DiseasePrediction.user_id == current_user.id,
            DiseasePrediction.overall_risk_level == "low"
        ).count()
        
        # Convert to response format
        prediction_responses = []
        for pred in predictions:
            # Convert JSON fields back to objects
            predicted_diseases = [
                {
                    "disease_name": disease.get("disease_name", ""),
                    "risk_level": disease.get("risk_level", "low"),
                    "confidence": disease.get("confidence", 0.0),
                    "contributing_factors": disease.get("contributing_factors", []),
                    "description": disease.get("description", ""),
                    "symptoms_to_watch": disease.get("symptoms_to_watch", [])
                }
                for disease in pred.predicted_diseases
            ]
            
            prediction_responses.append(DiseasePredictionResponse(
                id=pred.id,
                user_id=pred.user_id,
                health_analysis_id=pred.health_analysis_id,
                predicted_diseases=predicted_diseases,
                overall_risk_level=pred.overall_risk_level,
                recommendations=pred.recommendations,
                medical_disclaimer=pred.medical_disclaimer,
                ai_explanation=None,  # Don't include explanation in history for performance
                created_at=pred.created_at
            ))
        
        return DiseasePredictionHistory(
            predictions=prediction_responses,
            total_count=total_count,
            high_risk_count=high_risk_count,
            moderate_risk_count=moderate_risk_count,
            low_risk_count=low_risk_count
        )
        
    except Exception as e:
        logger.error(f"Failed to get prediction history for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prediction history."
        )

@router.get("/latest", response_model=DiseasePredictionResponse)
async def get_latest_prediction(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the user's most recent disease prediction.
    
    Returns the latest prediction made by the current user, or 404 if no predictions exist.
    """
    try:
        latest_prediction = db.query(DiseasePrediction).filter(
            DiseasePrediction.user_id == current_user.id
        ).order_by(DiseasePrediction.created_at.desc()).first()
        
        if not latest_prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No predictions found for this user."
            )
        
        # Convert JSON fields back to objects
        predicted_diseases = [
            {
                "disease_name": disease.get("disease_name", ""),
                "risk_level": disease.get("risk_level", "low"),
                "confidence": disease.get("confidence", 0.0),
                "contributing_factors": disease.get("contributing_factors", []),
                "description": disease.get("description", ""),
                "symptoms_to_watch": disease.get("symptoms_to_watch", [])
            }
            for disease in latest_prediction.predicted_diseases
        ]
        
        return DiseasePredictionResponse(
            id=latest_prediction.id,
            user_id=latest_prediction.user_id,
            health_analysis_id=latest_prediction.health_analysis_id,
            predicted_diseases=predicted_diseases,
            overall_risk_level=latest_prediction.overall_risk_level,
            recommendations=latest_prediction.recommendations,
            medical_disclaimer=latest_prediction.medical_disclaimer,
            ai_explanation=None,
            created_at=latest_prediction.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get latest prediction for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve latest prediction."
        )

@router.delete("/history/{prediction_id}")
async def delete_prediction(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific disease prediction.
    
    Users can only delete their own predictions.
    """
    try:
        prediction = db.query(DiseasePrediction).filter(
            DiseasePrediction.id == prediction_id,
            DiseasePrediction.user_id == current_user.id
        ).first()
        
        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prediction not found or you don't have permission to delete it."
            )
        
        db.delete(prediction)
        db.commit()
        
        logger.info(f"User {current_user.id} deleted prediction {prediction_id}")
        
        return {"message": "Prediction deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete prediction {prediction_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete prediction."
        ) 
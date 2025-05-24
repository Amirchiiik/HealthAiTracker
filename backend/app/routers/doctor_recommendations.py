"""
Doctor Recommendations Router

Provides API endpoints for intelligent doctor/specialist recommendations
based on health metric analysis from OCR results.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import logging

from ..services.doctor_recommendation_service import doctor_recommendation_service
from ..auth import get_current_user
from ..models import User
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["Doctor Recommendations"])


class HealthMetric(BaseModel):
    """Health metric model for API input validation."""
    name: str = Field(..., description="Metric name (e.g., ALT, glucose, cholesterol)")
    value: float = Field(..., description="Numeric value of the metric")
    unit: str = Field(..., description="Unit of measurement (e.g., Ед/л, ммоль/л)")
    reference_range: str = Field(..., description="Normal reference range")
    status: str = Field(..., description="Status: normal, high, low, elevated, etc.")


class RecommendationRequest(BaseModel):
    """Request model for doctor recommendations."""
    metrics: List[HealthMetric] = Field(..., description="List of health metrics from analysis")


class SpecialistRecommendation(BaseModel):
    """Model for individual specialist recommendation."""
    type: str = Field(..., description="Type of medical specialist")
    reason: str = Field(..., description="Detailed reason for recommendation")
    priority: str = Field(..., description="Priority level: high, medium, low")
    metrics_involved: List[str] = Field(..., description="Names of metrics that triggered this recommendation")
    description: str = Field(..., description="Description of what this specialist does")
    when_to_consult: str = Field(..., description="When to consult this specialist")


class RecommendationResponse(BaseModel):
    """Response model for doctor recommendations."""
    recommended_specialists: List[SpecialistRecommendation] = Field(..., description="List of recommended specialists")
    next_steps: List[str] = Field(..., description="Actionable next steps for the patient")
    abnormal_metrics_count: int = Field(..., description="Number of abnormal metrics found")
    priority_level: str = Field(..., description="Overall priority level")
    disclaimer: str = Field(..., description="Medical disclaimer")
    emergency_note: str = Field(..., description="Emergency consultation note")


@router.post("/analyze", response_model=RecommendationResponse)
async def get_doctor_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze health metrics and provide intelligent doctor/specialist recommendations.
    
    This endpoint analyzes health metrics from OCR analysis and maps abnormal values
    to appropriate medical specialists based on detected conditions.
    
    **Important**: This service provides recommendations only and does not diagnose.
    Always consult a licensed physician for proper medical evaluation.
    """
    try:
        logger.info(f"Analyzing {len(request.metrics)} metrics for user {current_user.id}")
        
        # Convert Pydantic models to dictionaries for service processing
        metrics_data = [metric.dict() for metric in request.metrics]
        
        # Get recommendations from the service
        recommendations = doctor_recommendation_service.analyze_and_recommend(metrics_data)
        
        logger.info(f"Generated {len(recommendations.get('recommended_specialists', []))} specialist recommendations")
        
        return RecommendationResponse(**recommendations)
        
    except Exception as e:
        logger.error(f"Error generating doctor recommendations for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate doctor recommendations. Please try again later."
        )


@router.post("/analyze-from-ocr", response_model=RecommendationResponse)
async def get_recommendations_from_ocr_analysis(
    ocr_analysis: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Get doctor recommendations directly from OCR analysis results.
    
    This endpoint accepts the full OCR analysis response (from /ocr/{filename}/with-explanations)
    and extracts the metrics to provide specialist recommendations.
    
    Expected input format:
    ```json
    {
        "analysis": {
            "metrics": [
                {
                    "name": "ALT",
                    "value": 66.19,
                    "unit": "Ед/л",
                    "reference_range": "3 - 45",
                    "status": "high"
                }
            ]
        }
    }
    ```
    """
    try:
        # Extract metrics from OCR analysis
        analysis = ocr_analysis.get("analysis", {})
        metrics = analysis.get("metrics", [])
        
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No metrics found in OCR analysis. Please provide valid analysis data."
            )
        
        logger.info(f"Processing OCR analysis with {len(metrics)} metrics for user {current_user.id}")
        
        # Validate that metrics have required fields
        validated_metrics = []
        for metric in metrics:
            if all(key in metric for key in ['name', 'value', 'unit', 'status']):
                # Ensure reference_range exists
                if 'reference_range' not in metric:
                    metric['reference_range'] = 'Not specified'
                validated_metrics.append(metric)
            else:
                logger.warning(f"Skipping invalid metric: {metric}")
        
        if not validated_metrics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid metrics found in analysis. Metrics must include name, value, unit, and status."
            )
        
        # Get recommendations from the service
        recommendations = doctor_recommendation_service.analyze_and_recommend(validated_metrics)
        
        logger.info(f"Generated {len(recommendations.get('recommended_specialists', []))} specialist recommendations from OCR analysis")
        
        return RecommendationResponse(**recommendations)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing OCR analysis for recommendations for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process OCR analysis for recommendations. Please try again later."
        )


@router.get("/specialists")
async def get_available_specialists(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about available medical specialists.
    
    Returns a list of all medical specialists that the recommendation system
    can suggest, along with their descriptions and when to consult them.
    """
    try:
        # Get specialist information from the service
        specialist_info = doctor_recommendation_service.specialist_info
        
        specialists = []
        for specialist_type, info in specialist_info.items():
            specialists.append({
                "type": specialist_type,
                "description": info.get("description", ""),
                "when_to_consult": info.get("when_to_consult", "")
            })
        
        return {
            "specialists": specialists,
            "total_count": len(specialists),
            "note": "This list represents specialists that our recommendation system can suggest based on laboratory results."
        }
        
    except Exception as e:
        logger.error(f"Error getting specialist information: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve specialist information."
        )


@router.get("/conditions")
async def get_mapped_conditions(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about medical conditions that the system can detect.
    
    Returns a list of medical conditions that the recommendation system
    can identify from laboratory results, along with associated metrics.
    """
    try:
        # Get condition mapping from the service
        metric_condition_map = doctor_recommendation_service.metric_condition_map
        
        conditions = {}
        for metric, condition_info in metric_condition_map.items():
            condition_type = condition_info.get('type')
            condition_name = condition_info.get('condition_name')
            
            if condition_type not in conditions:
                conditions[condition_type] = {
                    "condition_name": condition_name,
                    "description": condition_info.get('description', ''),
                    "severity": condition_info.get('base_severity', 'medium'),
                    "associated_metrics": []
                }
            
            conditions[condition_type]["associated_metrics"].append(metric.upper())
        
        return {
            "conditions": conditions,
            "total_conditions": len(conditions),
            "note": "These conditions can be detected from laboratory value patterns."
        }
        
    except Exception as e:
        logger.error(f"Error getting condition information: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve condition information."
        ) 
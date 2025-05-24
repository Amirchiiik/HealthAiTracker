"""
Intelligent Health Agent Router

Provides API endpoints for the intelligent health agent that analyzes medical data
and automatically recommends and books appointments with specialists.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import logging

from ..database import get_db
from ..auth import get_current_user, get_current_patient
from ..models import User, HealthAnalysis, AgentRecommendation
from ..schemas import (
    IntelligentAgentRequest, IntelligentAgentResponse,
    AgentRecommendationResponse
)
from ..services.intelligent_health_agent import IntelligentHealthAgent
from ..services.localization_service import localization_service, Language

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["Intelligent Health Agent"])

@router.post("/analyze-and-act", response_model=IntelligentAgentResponse)
async def analyze_and_act(
    request: IntelligentAgentRequest,
    current_user: User = Depends(get_current_patient),  # Only patients can trigger agent
    db: Session = Depends(get_db)
):
    """
    🧠 Main Intelligent Health Agent Endpoint
    
    Analyzes health metrics from a completed health analysis and takes automated actions:
    
    1. **Analyzes Health Metrics**: Uses the existing doctor recommendation service
    2. **Detects Critical Values**: Identifies values requiring urgent attention
    3. **Enhanced AI Analysis**: Uses OpenRouter API for deeper insights (if configured)
    4. **Automatic Booking**: Books appointments for critical cases
    5. **Sends Notifications**: Alerts patient and assigned doctors
    6. **Records Actions**: Saves all recommendations and actions to database
    
    **Flow Example:**
    - Patient uploads medical report via OCR
    - OCR extracts metrics with status ("high", "critical", etc.)
    - Agent detects critical ALT levels
    - Agent automatically books with gastroenterologist
    - Patient and doctor receive notifications
    
    **Critical Auto-Booking Triggers:**
    - Glucose > 11.0 mmol/L → Urgent endocrinologist
    - Liver enzymes > 100 U/L → Gastroenterologist
    - Creatinine > 150 μmol/L → Nephrologist
    - Positive hepatitis markers → Infectious disease specialist
    """
    try:
        logger.info(f"Intelligent agent analysis requested by patient {current_user.id} for analysis {request.health_analysis_id}")
        
        # Verify the health analysis belongs to the current user
        health_analysis = db.query(HealthAnalysis).filter(
            HealthAnalysis.id == request.health_analysis_id,
            HealthAnalysis.user_id == current_user.id
        ).first()
        
        if not health_analysis:
            # Determine language for error message
            lang = Language.RUSSIAN if request.language == "ru" else Language.ENGLISH
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=localization_service.get_text("analysis_not_found", lang)
            )
        
        # Initialize the intelligent health agent
        agent = IntelligentHealthAgent(db)
        
        # Run the intelligent analysis and actions
        result = agent.analyze_and_act(
            patient_id=current_user.id,
            health_analysis_id=request.health_analysis_id,
            auto_book_critical=request.auto_book_critical,
            preferred_datetime=request.preferred_datetime,
            language=request.language
        )
        
        logger.info(f"Intelligent agent analysis completed for patient {current_user.id}. Actions taken: {len(result.actions_taken)}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in intelligent agent analysis for patient {current_user.id}: {e}")
        # Try to determine language for error message
        lang = Language.RUSSIAN if hasattr(request, 'language') and request.language == "ru" else Language.RUSSIAN
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=localization_service.get_text("unable_to_analyze", lang)
        )

@router.post("/process-ocr-analysis")
async def process_ocr_analysis(
    ocr_analysis: Dict[str, Any],
    auto_book_critical: bool = True,
    language: str = "ru",
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """
    🔗 Process OCR Analysis with Intelligent Agent
    
    Directly processes OCR analysis results and triggers intelligent agent actions.
    This creates a seamless workflow from document upload to specialist recommendations.
    
    **Expected Input Format** (from /ocr/{filename}/with-explanations):
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
        },
        "analysis_id": 123
    }
    ```
    
    **Complete End-to-End Workflow:**
    1. Patient uploads medical document
    2. OCR extracts and analyzes metrics  
    3. This endpoint triggers intelligent agent
    4. Agent detects critical values and books appointments
    5. Notifications sent to all parties
    """
    try:
        # Extract analysis ID and verify it exists
        analysis_id = ocr_analysis.get("analysis_id")
        if not analysis_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="analysis_id is required in OCR analysis data"
            )
        
        # Verify the analysis belongs to the current user
        health_analysis = db.query(HealthAnalysis).filter(
            HealthAnalysis.id == analysis_id,
            HealthAnalysis.user_id == current_user.id
        ).first()
        
        if not health_analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health analysis not found or unauthorized"
            )
        
        logger.info(f"Processing OCR analysis {analysis_id} with intelligent agent for patient {current_user.id}")
        
        # Initialize and run the intelligent agent
        agent = IntelligentHealthAgent(db)
        
        result = agent.analyze_and_act(
            patient_id=current_user.id,
            health_analysis_id=analysis_id,
            auto_book_critical=auto_book_critical,
            preferred_datetime=None,
            language=language
        )
        
        logger.info(f"OCR analysis processing completed for patient {current_user.id}. Critical metrics: {result.analysis_summary.get('critical_metrics', 0)}")
        
        return {
            "message": "OCR analysis processed successfully by intelligent agent",
            "agent_analysis": result,
            "workflow_completed": True,
            "critical_detected": result.analysis_summary.get('critical_metrics', 0) > 0,
            "appointment_booked": result.appointment_booked is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing OCR analysis with agent for patient {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process OCR analysis with intelligent agent."
        )

@router.get("/recommendations/{analysis_id}", response_model=AgentRecommendationResponse)
async def get_agent_recommendations(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get intelligent agent recommendations for a specific health analysis.
    
    Returns the stored agent recommendations including:
    - Recommended specialists
    - Critical metrics detected
    - Actions taken by the agent
    - Enhanced AI reasoning (if available)
    """
    try:
        # Get the agent recommendation
        agent_rec = db.query(AgentRecommendation).filter(
            AgentRecommendation.health_analysis_id == analysis_id
        ).first()
        
        if not agent_rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No agent recommendations found for this analysis"
            )
        
        # Verify access permissions
        if current_user.role == 'patient' and agent_rec.patient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized to access this recommendation"
            )
        elif current_user.role == 'doctor':
            # Doctors can see recommendations for their patients if they have an appointment
            from ..models import Appointment
            appointment = db.query(Appointment).filter(
                Appointment.health_analysis_id == analysis_id,
                Appointment.doctor_id == current_user.id
            ).first()
            
            if not appointment:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized to access this recommendation"
                )
        
        return AgentRecommendationResponse.from_orm(agent_rec)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent recommendations for analysis {analysis_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve agent recommendations."
        )

@router.get("/my-recommendations", response_model=List[AgentRecommendationResponse])
async def get_my_agent_recommendations(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """
    Get all intelligent agent recommendations for the current patient.
    
    Returns a list of all agent analyses and recommendations for the patient's
    health analyses, ordered by most recent first.
    """
    try:
        agent_recommendations = db.query(AgentRecommendation).filter(
            AgentRecommendation.patient_id == current_user.id
        ).order_by(AgentRecommendation.processed_at.desc()).offset(offset).limit(limit).all()
        
        return [AgentRecommendationResponse.from_orm(rec) for rec in agent_recommendations]
        
    except Exception as e:
        logger.error(f"Error getting patient agent recommendations for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve agent recommendations."
        )

@router.get("/statistics")
async def get_agent_statistics(
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """
    Get statistics about intelligent agent usage for the current patient.
    
    Returns summary statistics including:
    - Total agent analyses
    - Critical cases detected
    - Appointments automatically booked
    - Most recommended specialists
    """
    try:
        # Get agent recommendations for this patient
        agent_recs = db.query(AgentRecommendation).filter(
            AgentRecommendation.patient_id == current_user.id
        ).all()
        
        if not agent_recs:
            return {
                "total_analyses": 0,
                "critical_cases": 0,
                "appointments_booked": 0,
                "booking_attempts": 0,
                "most_recommended_specialists": [],
                "priority_breakdown": {"high": 0, "medium": 0, "low": 0}
            }
        
        # Calculate statistics
        total_analyses = len(agent_recs)
        critical_cases = len([r for r in agent_recs if r.priority_level == 'high'])
        appointments_booked = len([r for r in agent_recs if r.action_taken == 'appointment_booked'])
        booking_attempts = len([r for r in agent_recs if r.action_taken in ['appointment_booked', 'booking_attempted']])
        
        # Count recommended specialists
        specialist_counts = {}
        for rec in agent_recs:
            for specialist in rec.recommended_specialists:
                spec_type = specialist.get('type', 'Unknown')
                specialist_counts[spec_type] = specialist_counts.get(spec_type, 0) + 1
        
        # Sort specialists by frequency
        most_recommended = sorted(specialist_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Priority breakdown
        priority_breakdown = {
            "high": len([r for r in agent_recs if r.priority_level == 'high']),
            "medium": len([r for r in agent_recs if r.priority_level == 'medium']),
            "low": len([r for r in agent_recs if r.priority_level == 'low'])
        }
        
        return {
            "total_analyses": total_analyses,
            "critical_cases": critical_cases,
            "appointments_booked": appointments_booked,
            "booking_attempts": booking_attempts,
            "booking_success_rate": round((appointments_booked / booking_attempts * 100) if booking_attempts > 0 else 0, 1),
            "most_recommended_specialists": [{"specialist": spec, "count": count} for spec, count in most_recommended],
            "priority_breakdown": priority_breakdown
        }
        
    except Exception as e:
        logger.error(f"Error getting agent statistics for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve agent statistics."
        ) 
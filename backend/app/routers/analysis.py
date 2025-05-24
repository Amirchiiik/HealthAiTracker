from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services import analysis_service, llm_service

router = APIRouter()

class AnalyzeTextRequest(BaseModel):
    raw_text: str

class MetricExplanationResponse(BaseModel):
    metrics: List[Dict[str, Any]]
    overall_summary: str
    analysis: Dict[str, Any]

class IndividualExplainRequest(BaseModel):
    metrics: List[Dict[str, Any]]

@router.post("/text", response_model=MetricExplanationResponse)
async def analyze_text_with_explanations(request: AnalyzeTextRequest):
    """
    Analyze raw text and provide individual explanations for each detected metric
    """
    try:
        result = analysis_service.analyze_metrics_from_text_with_explanations(request.raw_text)
        return MetricExplanationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing text: {str(e)}")

@router.post("/metrics/explain")
async def explain_individual_metrics(request: IndividualExplainRequest):
    """
    Generate individual explanations for provided metrics
    """
    try:
        if not request.metrics:
            raise HTTPException(status_code=400, detail="No metrics provided")
        
        explained_metrics = llm_service.generate_individual_metric_explanations(request.metrics)
        
        # Generate overall summary
        total_metrics = len(explained_metrics)
        normal_count = len([m for m in explained_metrics if m.get('status') == 'normal'])
        attention_needed = total_metrics - normal_count
        
        overall_summary = f"{total_metrics} показателей проанализировано. "
        if normal_count > 0:
            overall_summary += f"{normal_count} в норме. "
        if attention_needed > 0:
            overall_summary += f"{attention_needed} требуют внимания."
        
        return {
            "metrics": explained_metrics,
            "overall_summary": overall_summary,
            "total_metrics": total_metrics,
            "metrics_needing_attention": attention_needed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining metrics: {str(e)}")

@router.get("/metrics/status/{status}")
async def get_metrics_by_status(status: str, metrics: List[Dict] = None):
    """
    Filter metrics by status (normal, low, high, elevated)
    """
    if not metrics:
        return {"metrics": [], "message": "No metrics provided"}
    
    valid_statuses = ['normal', 'low', 'high', 'elevated']
    if status.lower() not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    filtered_metrics = [m for m in metrics if m.get('status', '').lower() == status.lower()]
    
    return {
        "metrics": filtered_metrics,
        "count": len(filtered_metrics),
        "status": status
    }

@router.post("/summary")
async def generate_metrics_summary(request: IndividualExplainRequest):
    """
    Generate a detailed summary of all metrics without individual explanations
    """
    try:
        if not request.metrics:
            raise HTTPException(status_code=400, detail="No metrics provided")
        
        grouped_metrics = analysis_service.get_metrics_by_status(request.metrics)
        
        summary = {
            "total_metrics": len(request.metrics),
            "by_status": {
                "normal": {
                    "count": len(grouped_metrics['normal']),
                    "metrics": [m['name'] for m in grouped_metrics['normal']]
                },
                "low": {
                    "count": len(grouped_metrics['low']),
                    "metrics": [m['name'] for m in grouped_metrics['low']]
                },
                "high": {
                    "count": len(grouped_metrics['high']),
                    "metrics": [m['name'] for m in grouped_metrics['high']]
                },
                "elevated": {
                    "count": len(grouped_metrics['elevated']),
                    "metrics": [m['name'] for m in grouped_metrics['elevated']]
                }
            },
            "needs_attention": len(request.metrics) - len(grouped_metrics['normal']),
            "recommendation": "Консультация с врачом рекомендуется для интерпретации отклонений от нормы." if len(request.metrics) - len(grouped_metrics['normal']) > 0 else "Все показатели в норме."
        }
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}") 
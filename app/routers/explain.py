from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.services.llm_service import generate_explanation_async, generate_explanation

router = APIRouter()

class ExplainRequest(BaseModel):
    raw_text: str

class ExplainResponseTask(BaseModel):
    task_id: str
    status: str
    explanation: str = None

@router.post("/")
async def explain_analysis(data: ExplainRequest):
    try:
        # Use the async version that returns immediately with fallback or cached response
        explanation = generate_explanation_async(data.raw_text)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoint - keep for backward compatibility
@router.post("/sync")
async def explain_analysis_sync(data: ExplainRequest):
    try:
        # This will block until completion
        explanation = generate_explanation(data.raw_text)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

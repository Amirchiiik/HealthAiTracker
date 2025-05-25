from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import time
import asyncio
from typing import Dict, Any, Optional
import aiofiles
import requests
import uuid
import jwt
from app.services import ocr_service, explain_service, analysis_service
from app.routers import analysis, auth, users, chat, disease_prediction, doctor_recommendations, appointments, health_agent
from app.database import connect_db, disconnect_db, create_tables, get_db
from app.models import User
from app.auth import get_current_user, SECRET_KEY, ALGORITHM
from app.services.database_service import save_analysis_to_history, save_chat_to_history
from app.schemas import InteractionType, AnalysisWithExplanationResponse
from app.websocket import manager

app = FastAPI(
    title="AI Health Tracker",
    description="Backend API for AI-powered health analysis with authentication, disease risk prediction, intelligent doctor recommendations, and automated appointment booking",
    version="3.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
app.include_router(chat.router)  # Chat router with its own prefix
app.include_router(disease_prediction.router)  # Disease prediction router
app.include_router(doctor_recommendations.router)  # Doctor recommendations router
app.include_router(appointments.router)  # Appointments router
app.include_router(health_agent.router)  # Intelligent health agent router

# Database lifecycle events
@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    create_tables()
    await connect_db()

@app.on_event("shutdown") 
async def shutdown():
    """Clean up database connections on shutdown"""
    await disconnect_db()

# Root endpoint
@app.get("/")
def root():
    return {"message": "AI Health Tracker backend is running 🚀"}

# Global cache for explain responses
explain_cache: Dict[str, str] = {}
processing_tasks: Dict[str, asyncio.Task] = {}

@app.get("/health")
def health_check():
    """Check if the server is running and healthy."""
    return {"status": "ok", "message": "Server is running"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a medical document file (requires authentication)"""
    try:
        file_extension = file.filename.split('.')[-1].lower()
        allowed_extensions = ['jpg', 'jpeg', 'png', 'pdf', 'heic']
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}")
        
        # Create user-specific uploads directory
        user_upload_dir = f"uploads/user_{current_user.id}"
        os.makedirs(user_upload_dir, exist_ok=True)
        
        # Generate a unique filename
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"{user_upload_dir}/{unique_filename}"
        
        # Save the file
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        return {
            "filename": unique_filename, 
            "message": "File uploaded successfully",
            "user_id": current_user.id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ocr/{filename}")
def process_ocr(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process OCR on uploaded file (requires authentication)"""
    try:
        # Construct file path with user-specific directory
        file_path = f"uploads/user_{current_user.id}/{filename}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Process the file with OCR
        result = ocr_service.extract_text_from_file(file_path)
        
        # Save to user's history
        if result.get("analysis", {}).get("metrics"):
            saved_analysis = save_analysis_to_history(
                db=db,
                user_id=current_user.id,
                filename=filename,
                extracted_text=result["extracted_text"],
                metrics=result["analysis"]["metrics"],
                overall_summary=result["analysis"].get("summary", ""),
                analysis_data=result["analysis"]
            )
            
            return {
                "filename": filename,
                "extracted_text": result["extracted_text"],
                "analysis": result["analysis"],
                "saved_to_history": True,
                "analysis_id": saved_analysis.id
            }
        
        return {
            "filename": filename,
            "extracted_text": result["extracted_text"],
            "analysis": result["analysis"],
            "saved_to_history": False
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ocr/{filename}/with-explanations", response_model=AnalysisWithExplanationResponse)
def process_ocr_with_explanations(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enhanced OCR endpoint that includes individual metric explanations (requires authentication)
    """
    try:
        # Construct file path with user-specific directory
        file_path = f"uploads/user_{current_user.id}/{filename}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Process the file with enhanced analysis including individual explanations
        result = analysis_service.analyze_medical_document_with_explanations(file_path)
        
        # Save to user's history
        saved_analysis = save_analysis_to_history(
            db=db,
            user_id=current_user.id,
            filename=filename,
            extracted_text=result["extracted_text"],
            metrics=result["metrics"],
            overall_summary=result["overall_summary"],
            analysis_data=result["analysis"]
        )
        
        return AnalysisWithExplanationResponse(
            filename=filename,
            extracted_text=result["extracted_text"],
            metrics=result["metrics"],
            overall_summary=result["overall_summary"],
            analysis=result["analysis"],
            saved_to_history=True,
            analysis_id=saved_analysis.id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ExplainRequest(BaseModel):
    raw_text: str

async def process_explanation_in_background(request_id: str, text: str, user_id: int, db: Session):
    try:
        # Call the actual explanation service
        explanation = explain_service.generate_explanation(text)
        
        # Save to chat history
        save_chat_to_history(
            db=db,
            user_id=user_id,
            prompt=text,
            response=explanation,
            interaction_type=InteractionType.EXPLANATION
        )
        
        # Store the result in the cache
        explain_cache[request_id] = explanation
    except Exception as e:
        error_msg = f"Error generating explanation: {str(e)}"
        # Store error message in case of failure
        explain_cache[request_id] = error_msg
        
        # Save error to chat history as well
        try:
            save_chat_to_history(
                db=db,
                user_id=user_id,
                prompt=text,
                response=error_msg,
                interaction_type=InteractionType.EXPLANATION
            )
        except:
            pass  # Don't fail if we can't save the error
    finally:
        # Clean up the task reference
        if request_id in processing_tasks:
            del processing_tasks[request_id]

@app.post("/explain")
async def explain_text(
    request: ExplainRequest, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate explanation for medical text (requires authentication)"""
    # Generate a unique ID for this request
    request_id = str(uuid.uuid4())
    
    # Start the explanation processing in the background
    task = asyncio.create_task(process_explanation_in_background(
        request_id, request.raw_text, current_user.id, db
    ))
    processing_tasks[request_id] = task
    
    # Wait for a short time to see if we get a quick result
    try:
        await asyncio.wait_for(asyncio.shield(task), timeout=5.0)
    except asyncio.TimeoutError:
        # If it's taking too long, return a placeholder
        return {
            "explanation": "We're still analyzing your medical data. This can take up to a minute. Please check back for detailed insights.",
            "processing": True,
            "request_id": request_id
        }
    
    # If we get here, the task completed within the timeout
    if request_id in explain_cache:
        explanation = explain_cache[request_id]
        del explain_cache[request_id]
        return {"explanation": explanation, "processing": False}
    else:
        # This should not happen, but just in case
        return {
            "explanation": "There was an issue processing your request. Please try again.",
            "processing": False
        }

@app.get("/explain/status/{request_id}")
def check_explanation_status(request_id: str):
    if request_id in explain_cache:
        explanation = explain_cache[request_id]
        del explain_cache[request_id]
        return {"explanation": explanation, "processing": False}
    elif request_id in processing_tasks:
        return {
            "explanation": "Still processing your request. Please check back in a moment.",
            "processing": True
        }
    else:
        raise HTTPException(status_code=404, detail="Request not found or expired")

@app.post("/explain/metrics")
async def explain_metrics_individually(
    request: ExplainRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enhanced explain endpoint that provides individual explanations for each metric (requires authentication)
    """
    try:
        # Use the new analysis service to get individual explanations
        result = analysis_service.analyze_metrics_from_text_with_explanations(request.raw_text)
        
        # Save to chat history
        save_chat_to_history(
            db=db,
            user_id=current_user.id,
            prompt=request.raw_text,
            response=result["overall_summary"],
            interaction_type=InteractionType.ANALYSIS
        )
        
        return {
            "metrics": result["metrics"],
            "overall_summary": result["overall_summary"],
            "analysis": result["analysis"],
            "processing": False,
            "saved_to_history": True
        }
    except Exception as e:
        error_msg = f"Error explaining metrics: {str(e)}"
        
        # Save error to chat history
        try:
            save_chat_to_history(
                db=db,
                user_id=current_user.id,
                prompt=request.raw_text,
                response=error_msg,
                interaction_type=InteractionType.ANALYSIS
            )
        except:
            pass
        
        raise HTTPException(status_code=500, detail=error_msg)

# WebSocket endpoint for real-time chat
@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """WebSocket endpoint for real-time chat communication"""
    try:
        # Decode the JWT token to get user info
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        user_role: str = payload.get("role")
        
        if user_id is None or user_role is None:
            await websocket.close(code=4001, reason="Invalid token")
            return
            
    except jwt.PyJWTError:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    # Connect the user
    await manager.connect(websocket, user_id, user_role)
    
    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            
            # For now, we'll just echo back a confirmation
            # In a full implementation, you might handle different message types here
            await websocket.send_text(f"Message received: {data}")
            
    except WebSocketDisconnect:
        # Handle disconnection
        manager.disconnect(user_id)
        await manager.broadcast_user_status(user_id, "offline")

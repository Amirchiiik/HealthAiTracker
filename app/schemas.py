from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Enums
class UserRole(str, Enum):
    DOCTOR = "doctor"
    PATIENT = "patient"

class InteractionType(str, Enum):
    EXPLANATION = "explanation"
    ANALYSIS = "analysis"
    GENERAL = "general"

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"

# User schemas
class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['doctor', 'patient']:
            raise ValueError('Role must be either "doctor" or "patient"')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Health Analysis schemas
class HealthAnalysisBase(BaseModel):
    filename: Optional[str] = None
    extracted_text: Optional[str] = None
    metrics: Optional[List[Any]] = None
    overall_summary: Optional[str] = None
    analysis_data: Optional[Any] = None

class HealthAnalysisCreate(HealthAnalysisBase):
    pass

class HealthAnalysisResponse(HealthAnalysisBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat Interaction schemas (AI interactions)
class ChatInteractionBase(BaseModel):
    prompt: str
    response: str
    interaction_type: Optional[str] = None

class ChatInteractionCreate(ChatInteractionBase):
    pass

class ChatInteractionResponse(ChatInteractionBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# User statistics schema
class UserStats(BaseModel):
    total_analyses: int
    total_chats: int
    recent_activity: List[dict]

# Chat Message schemas (User-to-user communication)
class ChatMessageBase(BaseModel):
    message_text: str = Field(..., min_length=1, max_length=5000, description="Message content")

class ChatMessageCreate(ChatMessageBase):
    receiver_id: int = Field(..., description="ID of the message recipient")

class ChatAttachment(BaseModel):
    filename: str
    file_size: int
    file_type: str
    uploaded_at: datetime

class ChatMessageResponse(ChatMessageBase):
    id: int
    sender_id: int
    receiver_id: int
    attachment_filename: Optional[str] = None
    attachment_size: Optional[int] = None
    attachment_type: Optional[str] = None
    is_read: str
    created_at: datetime
    sender: UserResponse
    receiver: UserResponse
    
    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
    total_count: int
    has_more: bool
    
class ChatParticipant(BaseModel):
    user_id: int
    full_name: str
    role: str
    last_message_at: Optional[datetime] = None
    unread_count: int = 0

class ChatConversationList(BaseModel):
    conversations: List[ChatParticipant]

# Combined response schemas
class UserHistoryResponse(BaseModel):
    health_analyses: List[HealthAnalysisResponse]
    chat_interactions: List[ChatInteractionResponse]
    total_analyses: int
    total_chats: int

class AnalysisWithExplanationResponse(BaseModel):
    """Response for OCR analysis that gets saved to user history"""
    filename: Optional[str]
    extracted_text: str
    metrics: List[Dict[str, Any]]
    overall_summary: str
    analysis: Dict[str, Any]
    saved_to_history: bool = True
    analysis_id: int

# Disease Prediction schemas
class MetricInput(BaseModel):
    name: str = Field(..., description="Metric name (e.g., 'hemoglobin', 'glucose')")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement (e.g., 'g/dL', 'mg/dL')")
    reference_range: Optional[str] = Field(None, description="Normal reference range")
    
    @validator('name')
    def validate_metric_name(cls, v):
        # Convert to lowercase and replace spaces with underscores for consistency
        return v.lower().replace(' ', '_').replace('-', '_')

class RiskFactor(BaseModel):
    metric_name: str = Field(..., description="Name of the contributing metric")
    metric_value: float = Field(..., description="Value of the metric")
    normal_range: str = Field(..., description="Normal reference range")
    deviation_severity: str = Field(..., description="How far from normal: mild, moderate, severe")
    contribution_weight: float = Field(..., ge=0.0, le=1.0, description="Weight of this factor in prediction")

class DiseaseRisk(BaseModel):
    disease_name: str = Field(..., description="Name of the predicted disease")
    risk_level: RiskLevel = Field(..., description="Risk level: low, moderate, high")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    contributing_factors: List[RiskFactor] = Field(..., description="Factors contributing to this risk")
    description: str = Field(..., description="Brief description of the disease")
    symptoms_to_watch: List[str] = Field(default=[], description="Symptoms to monitor")

class DiseasePredictionRequest(BaseModel):
    metrics: List[MetricInput] = Field(..., min_items=1, description="Health metrics for analysis")
    include_explanations: bool = Field(default=True, description="Whether to include AI-generated explanations")
    
    @validator('metrics')
    def validate_metrics(cls, v):
        if not v:
            raise ValueError('At least one metric is required')
        
        # Check for duplicate metric names
        metric_names = [metric.name for metric in v]
        if len(metric_names) != len(set(metric_names)):
            raise ValueError('Duplicate metric names are not allowed')
        
        return v

class DiseasePredictionResponse(BaseModel):
    id: int
    user_id: int
    health_analysis_id: Optional[int] = None
    predicted_diseases: List[DiseaseRisk]
    overall_risk_level: RiskLevel
    recommendations: Optional[str] = None
    medical_disclaimer: str
    ai_explanation: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class DiseasePredictionCreate(BaseModel):
    predicted_diseases: List[DiseaseRisk]
    risk_factors: List[RiskFactor] 
    confidence_scores: Dict[str, float]
    overall_risk_level: RiskLevel
    recommendations: Optional[str] = None
    medical_disclaimer: str
    health_analysis_id: Optional[int] = None

class DiseasePredictionHistory(BaseModel):
    predictions: List[DiseasePredictionResponse]
    total_count: int
    high_risk_count: int
    moderate_risk_count: int
    low_risk_count: int

class EnhancedAnalysisResponse(BaseModel):
    """Enhanced OCR analysis with disease predictions"""
    filename: Optional[str]
    extracted_text: str
    metrics: List[Dict[str, Any]]
    overall_summary: str
    analysis: Dict[str, Any]
    disease_predictions: Optional[DiseasePredictionResponse] = None
    saved_to_history: bool = True
    analysis_id: int 
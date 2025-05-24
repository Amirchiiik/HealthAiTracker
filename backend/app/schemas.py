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

class AppointmentType(str, Enum):
    URGENT = "urgent"
    ROUTINE = "routine"
    FOLLOW_UP = "follow_up"

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class BookingMethod(str, Enum):
    MANUAL = "manual"
    AUTO_AGENT = "auto_agent"

class AgentAction(str, Enum):
    NONE = "none"
    BOOKING_ATTEMPTED = "booking_attempted"
    APPOINTMENT_BOOKED = "appointment_booked"

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

# Appointment schemas
class DoctorAvailabilityBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    is_active: bool = Field(default=True)

class DoctorAvailabilityCreate(DoctorAvailabilityBase):
    pass

class DoctorAvailabilityResponse(DoctorAvailabilityBase):
    id: int
    doctor_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class AppointmentBase(BaseModel):
    appointment_datetime: datetime = Field(..., description="Appointment date and time")
    duration_minutes: int = Field(default=60, ge=15, le=240, description="Appointment duration in minutes")
    appointment_type: AppointmentType = Field(..., description="Type of appointment")
    reason: Optional[str] = Field(None, description="Reason for appointment")
    specialist_type: Optional[str] = Field(None, description="Required specialist type")
    priority_level: PriorityLevel = Field(..., description="Priority level")
    notes: Optional[str] = Field(None, description="Additional notes")

class AppointmentCreate(AppointmentBase):
    doctor_id: int = Field(..., description="ID of the doctor")
    health_analysis_id: Optional[int] = Field(None, description="Related health analysis ID")

class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    appointment_datetime: Optional[datetime] = None

class AppointmentResponse(AppointmentBase):
    id: int
    patient_id: int
    doctor_id: int
    health_analysis_id: Optional[int]
    status: AppointmentStatus
    booking_method: BookingMethod
    created_at: datetime
    updated_at: datetime
    patient: UserResponse
    doctor: UserResponse
    
    class Config:
        from_attributes = True

class DoctorProfileResponse(UserResponse):
    medical_specialty: Optional[str]
    is_available_for_booking: bool
    availability: Optional[List[DoctorAvailabilityResponse]] = []

class AvailableDoctorsResponse(BaseModel):
    doctors: List[DoctorProfileResponse]
    specialty: Optional[str]
    total_count: int

# Intelligent Agent schemas
class AgentRecommendationBase(BaseModel):
    recommended_specialists: List[Dict[str, Any]] = Field(..., description="List of recommended specialists")
    critical_metrics: List[Dict[str, Any]] = Field(..., description="Metrics that triggered recommendations")
    priority_level: PriorityLevel = Field(..., description="Overall priority level")
    agent_reasoning: Optional[str] = Field(None, description="Why the agent made these recommendations")
    next_steps: Optional[List[str]] = Field(None, description="Recommended next steps")

class AgentRecommendationCreate(AgentRecommendationBase):
    action_taken: AgentAction = Field(..., description="Action taken by the agent")
    appointment_id: Optional[int] = Field(None, description="ID of booked appointment if any")

class AgentRecommendationResponse(AgentRecommendationBase):
    id: int
    patient_id: int
    health_analysis_id: int
    action_taken: AgentAction
    appointment_id: Optional[int]
    processed_at: datetime
    patient: UserResponse
    appointment: Optional[AppointmentResponse] = None
    
    class Config:
        from_attributes = True

class IntelligentAgentRequest(BaseModel):
    health_analysis_id: int = Field(..., description="ID of the health analysis to process")
    auto_book_critical: bool = Field(default=True, description="Whether to automatically book appointments for critical cases")
    preferred_datetime: Optional[datetime] = Field(None, description="Preferred appointment time")
    language: Optional[str] = Field(default="ru", description="Response language (ru/en)")
    
    @validator('language')
    def validate_language(cls, v):
        if v and v not in ['ru', 'en']:
            raise ValueError('Language must be either "ru" or "en"')
        return v or "ru"

class IntelligentAgentResponse(BaseModel):
    analysis_summary: Dict[str, Any] = Field(..., description="Summary of the health analysis")
    recommendations: AgentRecommendationResponse = Field(..., description="Agent recommendations")
    actions_taken: List[str] = Field(..., description="List of actions taken by the agent")
    notifications_sent: List[str] = Field(..., description="List of notifications sent")
    appointment_booked: Optional[AppointmentResponse] = Field(None, description="Appointment details if booked")
    
class AutoBookingRequest(BaseModel):
    specialist_type: str = Field(..., description="Type of specialist needed")
    priority_level: PriorityLevel = Field(..., description="Priority level for booking")
    reason: str = Field(..., description="Reason for appointment")
    health_analysis_id: int = Field(..., description="Related health analysis ID")
    preferred_datetime: Optional[datetime] = Field(None, description="Preferred appointment time")

class AutoBookingResponse(BaseModel):
    success: bool = Field(..., description="Whether booking was successful")
    appointment: Optional[AppointmentResponse] = Field(None, description="Appointment details if booked")
    available_doctors: List[DoctorProfileResponse] = Field(default=[], description="Available doctors if booking failed")
    message: str = Field(..., description="Status message")
    next_available_slot: Optional[datetime] = Field(None, description="Next available appointment slot") 
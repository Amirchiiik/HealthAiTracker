from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, CheckConstraint, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    # Add medical specialty for doctors
    medical_specialty = Column(String(100), nullable=True)  # e.g., 'Gastroenterologist', 'Cardiologist'
    is_available_for_booking = Column(Boolean, default=True)  # Doctors can disable booking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Add constraint to ensure role is either 'doctor' or 'patient'
    __table_args__ = (
        CheckConstraint("role IN ('doctor', 'patient')", name='check_role'),
    )
    
    # Relationships
    health_analyses = relationship("HealthAnalysis", back_populates="user")
    chat_interactions = relationship("ChatInteraction", back_populates="user")
    sent_messages = relationship("ChatMessage", foreign_keys="ChatMessage.sender_id", back_populates="sender")
    received_messages = relationship("ChatMessage", foreign_keys="ChatMessage.receiver_id", back_populates="receiver")
    disease_predictions = relationship("DiseasePrediction", back_populates="user")
    # Appointment relationships
    patient_appointments = relationship("Appointment", foreign_keys="Appointment.patient_id", back_populates="patient")
    doctor_appointments = relationship("Appointment", foreign_keys="Appointment.doctor_id", back_populates="doctor")
    doctor_availability = relationship("DoctorAvailability", back_populates="doctor")
    agent_recommendations = relationship("AgentRecommendation", back_populates="patient")

class HealthAnalysis(Base):
    __tablename__ = "health_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255))
    extracted_text = Column(Text)
    metrics = Column(JSON)  # Store the metrics array as JSON
    overall_summary = Column(Text)
    analysis_data = Column(JSON)  # Store complete analysis data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="health_analyses")
    disease_predictions = relationship("DiseasePrediction", back_populates="health_analysis")

class ChatInteraction(Base):
    __tablename__ = "chat_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    interaction_type = Column(String(50))  # 'explanation', 'analysis', 'general', etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="chat_interactions")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message_text = Column(Text, nullable=False)
    attachment_filename = Column(String(255), nullable=True)
    attachment_path = Column(String(500), nullable=True)
    attachment_size = Column(Integer, nullable=True)  # File size in bytes
    attachment_type = Column(String(50), nullable=True)  # MIME type
    is_read = Column(String(10), default='false')  # Track if message has been read
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
    
    # Add indexes for efficient querying
    __table_args__ = (
        # Ensure sender and receiver are different users
        CheckConstraint("sender_id != receiver_id", name='check_different_users'),
    ) 

class DiseasePrediction(Base):
    __tablename__ = "disease_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    health_analysis_id = Column(Integer, ForeignKey("health_analyses.id"), nullable=True, index=True)
    predicted_diseases = Column(JSON, nullable=False)  # Array of disease predictions
    risk_factors = Column(JSON, nullable=False)        # Contributing metrics and values
    confidence_scores = Column(JSON, nullable=False)   # Confidence levels per disease
    overall_risk_level = Column(String(20), nullable=False)  # 'low', 'moderate', 'high'
    recommendations = Column(Text, nullable=True)      # Medical recommendations
    medical_disclaimer = Column(Text, nullable=False)  # Legal disclaimer
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="disease_predictions")
    health_analysis = relationship("HealthAnalysis", back_populates="disease_predictions")
    
    # Add constraint to ensure overall_risk_level is valid
    __table_args__ = (
        CheckConstraint("overall_risk_level IN ('low', 'moderate', 'high')", name='check_risk_level'),
    )

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    health_analysis_id = Column(Integer, ForeignKey("health_analyses.id"), nullable=True, index=True)
    appointment_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, default=60)  # Appointment duration
    appointment_type = Column(String(50), nullable=False)  # 'urgent', 'routine', 'follow_up'
    status = Column(String(20), default='scheduled')  # 'scheduled', 'confirmed', 'completed', 'cancelled'
    reason = Column(Text, nullable=True)  # Reason for appointment
    specialist_type = Column(String(100), nullable=True)  # e.g., 'Gastroenterologist'
    booking_method = Column(String(20), default='manual')  # 'manual', 'auto_agent'
    priority_level = Column(String(10), nullable=False)  # 'low', 'medium', 'high'
    notes = Column(Text, nullable=True)  # Additional notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_appointments")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_appointments")
    health_analysis = relationship("HealthAnalysis")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("patient_id != doctor_id", name='check_different_appointment_users'),
        CheckConstraint("appointment_type IN ('urgent', 'routine', 'follow_up')", name='check_appointment_type'),
        CheckConstraint("status IN ('scheduled', 'confirmed', 'completed', 'cancelled')", name='check_appointment_status'),
        CheckConstraint("priority_level IN ('low', 'medium', 'high')", name='check_appointment_priority'),
        CheckConstraint("booking_method IN ('manual', 'auto_agent')", name='check_booking_method'),
    )

class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(String(10), nullable=False)  # e.g., "09:00"
    end_time = Column(String(10), nullable=False)    # e.g., "17:00"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    doctor = relationship("User", back_populates="doctor_availability")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("day_of_week >= 0 AND day_of_week <= 6", name='check_day_of_week'),
    )

class AgentRecommendation(Base):
    __tablename__ = "agent_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    health_analysis_id = Column(Integer, ForeignKey("health_analyses.id"), nullable=False, index=True)
    recommended_specialists = Column(JSON, nullable=False)  # List of recommended specialists
    critical_metrics = Column(JSON, nullable=False)  # Metrics that triggered recommendations
    priority_level = Column(String(10), nullable=False)  # 'low', 'medium', 'high'
    action_taken = Column(String(20), nullable=False)  # 'none', 'booking_attempted', 'appointment_booked'
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True, index=True)
    agent_reasoning = Column(Text, nullable=True)  # Why the agent made these recommendations
    next_steps = Column(JSON, nullable=True)  # Recommended next steps
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("User", back_populates="agent_recommendations")
    health_analysis = relationship("HealthAnalysis")
    appointment = relationship("Appointment")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("priority_level IN ('low', 'medium', 'high')", name='check_agent_priority'),
        CheckConstraint("action_taken IN ('none', 'booking_attempted', 'appointment_booked')", name='check_action_taken'),
    ) 
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, CheckConstraint, Float
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
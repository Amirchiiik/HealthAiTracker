"""
Intelligent Health Agent Service

Main service that analyzes health metrics from OCR analysis, detects critical values,
recommends specialists, and automatically books appointments when appropriate.
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from ..models import User, HealthAnalysis, AgentRecommendation, Appointment
from ..schemas import (
    PriorityLevel, AgentAction, AppointmentType, 
    IntelligentAgentRequest, IntelligentAgentResponse,
    AgentRecommendationCreate, UserRole
)
from ..services.doctor_recommendation_service import doctor_recommendation_service
from ..services.appointment_service import AppointmentService
from ..services.notification_service import notification_service
from ..services.localization_service import localization_service, Language

logger = logging.getLogger(__name__)

class IntelligentHealthAgent:
    """
    Main intelligent agent that analyzes health metrics and takes automated actions.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.appointment_service = AppointmentService(db)
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        
        # Critical value thresholds for automatic booking
        self.critical_thresholds = {
            'glucose': {'high': 11.0, 'very_high': 15.0},  # mmol/L
            'alt': {'high': 100, 'very_high': 200},         # U/L
            'ast': {'high': 100, 'very_high': 200},         # U/L
            'creatinine': {'high': 150, 'very_high': 300},  # μmol/L
            'hemoglobin': {'low': 90, 'very_low': 70},      # g/L
            'platelets': {'low': 100, 'very_low': 50},      # x10^9/L
        }
        
        # Specialist mapping for auto-booking
        self.specialist_mapping = {
            'Gastroenterologist': ['alt', 'ast', 'alp', 'ggt', 'total_bilirubin'],
            'Endocrinologist': ['glucose', 'glycated_hemoglobin', 'thyroid_stimulating_hormone'],
            'Nephrologist': ['creatinine', 'urea'],
            'Hematologist': ['hemoglobin', 'white_blood_cells', 'platelets'],
            'Cardiologist': ['total_cholesterol', 'ldl_cholesterol', 'triglycerides'],
        }
    
    def analyze_and_act(self, patient_id: int, health_analysis_id: int,
                       auto_book_critical: bool = True,
                       preferred_datetime: Optional[datetime] = None,
                       language: str = "ru") -> IntelligentAgentResponse:
        """
        Main method that analyzes health data and takes appropriate actions.
        """
        try:
            logger.info(f"Starting intelligent analysis for patient {patient_id}, analysis {health_analysis_id}")
            
            # Convert language string to Language enum
            lang = Language.RUSSIAN if language == "ru" else Language.ENGLISH
            
            # Get the health analysis
            health_analysis = self.db.query(HealthAnalysis).filter(
                HealthAnalysis.id == health_analysis_id,
                HealthAnalysis.user_id == patient_id
            ).first()
            
            if not health_analysis:
                raise ValueError(localization_service.get_text("analysis_not_found", lang))
            
            # Get patient information
            patient = self.db.query(User).filter(
                User.id == patient_id,
                User.role == UserRole.PATIENT
            ).first()
            
            if not patient:
                raise ValueError(localization_service.get_text("patient_not_found", lang))
            
            # Extract metrics from the health analysis
            metrics = health_analysis.metrics or []
            
            if not metrics:
                logger.warning(f"No metrics found in health analysis {health_analysis_id}")
                return self._create_no_metrics_response(health_analysis, lang)
            
            # Step 1: Analyze with doctor recommendation service
            recommendations = doctor_recommendation_service.analyze_and_recommend(metrics)
            
            # Step 2: Determine criticality and required actions
            critical_metrics = self._identify_critical_metrics(metrics)
            priority_level = self._determine_overall_priority(critical_metrics, recommendations)
            
            # Step 3: Enhanced AI analysis if OpenRouter is available
            enhanced_reasoning = None
            if self.openrouter_api_key:
                enhanced_reasoning = self._get_enhanced_ai_analysis(metrics, recommendations, lang)
            
            # Step 4: Decide on actions and auto-booking
            actions_taken = []
            appointment_booked = None
            action_taken = AgentAction.NONE
            
            if auto_book_critical and priority_level == PriorityLevel.HIGH and critical_metrics:
                appointment_booked, booking_message = self._attempt_auto_booking(
                    patient, health_analysis_id, critical_metrics, recommendations, preferred_datetime, lang
                )
                
                if appointment_booked:
                    action_taken = AgentAction.APPOINTMENT_BOOKED
                    actions_taken.append(localization_service.get_text(
                        "auto_booked_appointment", lang, appointment_id=appointment_booked.id
                    ))
                else:
                    action_taken = AgentAction.BOOKING_ATTEMPTED
                    actions_taken.append(localization_service.get_text(
                        "booking_attempted", lang, message=booking_message
                    ))
            
            # Step 5: Send notifications
            notifications_sent = self._send_notifications(
                patient, critical_metrics, recommendations, actions_taken, appointment_booked, lang
            )
            
            # Step 6: Save agent recommendation to database
            agent_recommendation = self._save_agent_recommendation(
                patient_id, health_analysis_id, recommendations, critical_metrics,
                priority_level, action_taken, appointment_booked, enhanced_reasoning, lang
            )
            
            # Step 7: Create response
            return IntelligentAgentResponse(
                analysis_summary={
                    "total_metrics": len(metrics),
                    "abnormal_metrics": recommendations.get('abnormal_metrics_count', 0),
                    "critical_metrics": len(critical_metrics),
                    "priority_level": priority_level.value,
                    "health_analysis_id": health_analysis_id
                },
                recommendations=self._create_agent_recommendation_response(agent_recommendation, lang),
                actions_taken=actions_taken,
                notifications_sent=notifications_sent,
                appointment_booked=self._create_appointment_response(appointment_booked) if appointment_booked else None
            )
            
        except Exception as e:
            logger.error(f"Error in intelligent health agent analysis: {e}")
            raise
    
    def _identify_critical_metrics(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify metrics that are at critical levels requiring urgent attention."""
        critical_metrics = []
        
        for metric in metrics:
            name = metric.get('name', '').lower()
            value = metric.get('value', 0)
            status = metric.get('status', '').lower()
            
            # Check for critical thresholds
            is_critical = False
            
            # Glucose checks
            if 'glucose' in name and status == 'high':
                if value >= self.critical_thresholds['glucose']['very_high']:
                    is_critical = True
                elif value >= self.critical_thresholds['glucose']['high']:
                    is_critical = True
            
            # Liver enzyme checks
            elif 'alt' in name and status == 'high':
                if value >= self.critical_thresholds['alt']['high']:
                    is_critical = True
            elif 'ast' in name and status == 'high':
                if value >= self.critical_thresholds['ast']['high']:
                    is_critical = True
            
            # Kidney function checks
            elif 'creatinine' in name and status == 'high':
                if value >= self.critical_thresholds['creatinine']['high']:
                    is_critical = True
            
            # Blood count checks
            elif 'hemoglobin' in name and status == 'low':
                if value <= self.critical_thresholds['hemoglobin']['low']:
                    is_critical = True
            elif 'platelets' in name and status == 'low':
                if value <= self.critical_thresholds['platelets']['low']:
                    is_critical = True
            
            # Infectious disease markers
            elif any(marker in name for marker in ['hepatitis', 'hiv', 'syphilis']) and status in ['positive', 'detected']:
                is_critical = True
            
            if is_critical:
                critical_metrics.append(metric)
                logger.warning(f"Critical metric detected: {name} = {value} ({status})")
        
        return critical_metrics
    
    def _determine_overall_priority(self, critical_metrics: List[Dict], recommendations: Dict) -> PriorityLevel:
        """Determine the overall priority level based on critical metrics and recommendations."""
        if critical_metrics:
            # Check for very critical values
            very_critical = any(
                (metric.get('name', '').lower() == 'glucose' and metric.get('value', 0) >= 15.0) or
                (metric.get('name', '').lower() == 'creatinine' and metric.get('value', 0) >= 300) or
                ('hepatitis' in metric.get('name', '').lower() and metric.get('status') == 'positive')
                for metric in critical_metrics
            )
            
            if very_critical or len(critical_metrics) >= 3:
                return PriorityLevel.HIGH
        
        # Check recommendation priority
        rec_priority = recommendations.get('priority_level', 'low')
        if rec_priority == 'high':
            return PriorityLevel.HIGH
        elif rec_priority == 'medium' or critical_metrics:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW
    
    def _get_enhanced_ai_analysis(self, metrics: List[Dict], recommendations: Dict, lang: Language) -> Optional[str]:
        """Get enhanced AI analysis using OpenRouter API."""
        if not self.openrouter_api_key:
            return None
        
        try:
            # Prepare data for AI analysis with localized prompt
            if lang == Language.RUSSIAN:
                analysis_prompt = f"""
                Проанализируйте следующие показатели здоровья и дайте углубленные медицинские рекомендации:
                
                Показатели: {json.dumps(metrics, indent=2, ensure_ascii=False)}
                Первичные рекомендации: {json.dumps(recommendations, indent=2, ensure_ascii=False)}
                
                Предоставьте краткий, но всесторонний анализ, сосредоточившись на:
                1. Клиническое значение аномальных значений
                2. Потенциальные взаимосвязи между аномальными показателями
                3. Уровень срочности медицинской консультации
                4. Любые паттерны, которые указывают на конкретные состояния
                
                Держите ответ кратким и медицински значимым. Отвечайте на русском языке.
                """
                
                system_message = "Вы медицинский ИИ-помощник, предоставляющий анализ лабораторных результатов. Предоставляйте краткие, клинически значимые рекомендации."
            else:
                analysis_prompt = f"""
                Analyze the following health metrics and provide enhanced medical insights:
                
                Metrics: {json.dumps(metrics, indent=2)}
                Initial Recommendations: {json.dumps(recommendations, indent=2)}
                
                Provide a brief but comprehensive analysis focusing on:
                1. Clinical significance of the abnormal values
                2. Potential interconnections between abnormal metrics
                3. Urgency level for medical consultation
                4. Any patterns that suggest specific conditions
                
                Keep the response concise and medically relevant.
                """
                
                system_message = "You are a medical AI assistant providing analysis of laboratory results. Provide concise, clinically relevant insights."
            
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                "max_tokens": 500
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_analysis = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                logger.info("Enhanced AI analysis completed successfully")
                return ai_analysis
            else:
                logger.error(f"OpenRouter API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting enhanced AI analysis: {e}")
            return None
    
    def _attempt_auto_booking(self, patient: User, health_analysis_id: int,
                             critical_metrics: List[Dict], recommendations: Dict,
                             preferred_datetime: Optional[datetime], lang: Language) -> Tuple[Optional[Appointment], str]:
        """Attempt to automatically book an appointment for critical values."""
        try:
            # Determine the most appropriate specialist based on critical metrics
            specialist_type = self._determine_priority_specialist(critical_metrics, recommendations)
            
            if not specialist_type:
                return None, localization_service.get_text("no_appropriate_specialist", lang)
            
            # Determine reason for appointment
            critical_metric_names = [m.get('name', 'Unknown') for m in critical_metrics]
            reason = localization_service.get_text(
                "urgent_consultation_required", lang, metrics=", ".join(critical_metric_names)
            )
            
            # Attempt auto-booking
            appointment, message = self.appointment_service.auto_book_appointment(
                patient_id=patient.id,
                specialist_type=specialist_type,
                priority_level=PriorityLevel.HIGH,
                reason=reason,
                health_analysis_id=health_analysis_id,
                preferred_datetime=preferred_datetime
            )
            
            if appointment:
                logger.info(f"Successfully auto-booked appointment {appointment.id} for patient {patient.id}")
                
                # Send booking confirmation notifications
                doctor = self.db.query(User).filter(User.id == appointment.doctor_id).first()
                if doctor:
                    notification_service.notify_appointment_booked(patient, doctor, appointment)
                
                return appointment, localization_service.get_text(
                    "successfully_booked", lang, 
                    doctor_name=doctor.full_name if doctor else "Unknown",
                    datetime=appointment.appointment_datetime.strftime('%Y-%m-%d %H:%M')
                )
            
            return appointment, message
            
        except Exception as e:
            logger.error(f"Error in auto-booking attempt: {e}")
            return None, localization_service.get_text("auto_booking_failed", lang, error=str(e))
    
    def _determine_priority_specialist(self, critical_metrics: List[Dict], recommendations: Dict) -> Optional[str]:
        """Determine the highest priority specialist based on critical metrics."""
        specialist_scores = {}
        
        # Score specialists based on critical metrics
        for metric in critical_metrics:
            metric_name = metric.get('name', '').lower()
            
            for specialist, metric_list in self.specialist_mapping.items():
                if any(m in metric_name for m in metric_list):
                    specialist_scores[specialist] = specialist_scores.get(specialist, 0) + 1
        
        # Also consider recommendation priorities
        recommended_specialists = recommendations.get('recommended_specialists', [])
        for spec_rec in recommended_specialists:
            if spec_rec.get('priority') == 'high':
                specialist_type = spec_rec.get('type')
                specialist_scores[specialist_type] = specialist_scores.get(specialist_type, 0) + 2
        
        # Return the specialist with the highest score
        if specialist_scores:
            return max(specialist_scores, key=specialist_scores.get)
        
        # Fallback to first recommended specialist
        if recommended_specialists:
            return recommended_specialists[0].get('type')
        
        return None
    
    def _send_notifications(self, patient: User, critical_metrics: List[Dict],
                           recommendations: Dict, actions_taken: List[str],
                           appointment_booked: Optional[Appointment], lang: Language) -> List[str]:
        """Send appropriate notifications based on analysis results."""
        notifications_sent = []
        
        # Send critical alert if critical metrics found
        if critical_metrics:
            critical_notifications = notification_service.notify_critical_health_metrics(
                patient, critical_metrics, recommendations.get('recommended_specialists', [])
            )
            notifications_sent.extend(critical_notifications)
        
        # Send general recommendation notification
        recommendation_notifications = notification_service.notify_agent_recommendation(
            patient, recommendations, actions_taken
        )
        notifications_sent.extend(recommendation_notifications)
        
        return notifications_sent
    
    def _save_agent_recommendation(self, patient_id: int, health_analysis_id: int,
                                  recommendations: Dict, critical_metrics: List[Dict],
                                  priority_level: PriorityLevel, action_taken: AgentAction,
                                  appointment_booked: Optional[Appointment],
                                  enhanced_reasoning: Optional[str], lang: Language) -> AgentRecommendation:
        """Save the agent recommendation to the database."""
        try:
            agent_rec = AgentRecommendation(
                patient_id=patient_id,
                health_analysis_id=health_analysis_id,
                recommended_specialists=recommendations.get('recommended_specialists', []),
                critical_metrics=critical_metrics,
                priority_level=priority_level.value,
                action_taken=action_taken.value,
                appointment_id=appointment_booked.id if appointment_booked else None,
                agent_reasoning=enhanced_reasoning or localization_service.get_text(
                    "automated_analysis_detected", lang, metrics=len(critical_metrics), priority=priority_level.value
                ),
                next_steps=recommendations.get('next_steps', [])
            )
            
            self.db.add(agent_rec)
            self.db.commit()
            self.db.refresh(agent_rec)
            
            logger.info(f"Saved agent recommendation {agent_rec.id} for patient {patient_id}")
            return agent_rec
            
        except Exception as e:
            logger.error(f"Error saving agent recommendation: {e}")
            self.db.rollback()
            raise
    
    def _create_no_metrics_response(self, health_analysis: HealthAnalysis, lang: Language) -> IntelligentAgentResponse:
        """Create response when no metrics are found."""
        # Get patient data
        patient = self.db.query(User).filter(User.id == health_analysis.user_id).first()
        patient_data = None
        if patient:
            patient_data = {
                "id": patient.id,
                "full_name": patient.full_name,
                "email": patient.email,
                "role": patient.role,
                "created_at": patient.created_at
            }
        
        return IntelligentAgentResponse(
            analysis_summary={
                "total_metrics": 0,
                "abnormal_metrics": 0,
                "critical_metrics": 0,
                "priority_level": "low",
                "health_analysis_id": health_analysis.id
            },
            recommendations={
                "id": 0,
                "patient_id": health_analysis.user_id,
                "health_analysis_id": health_analysis.id,
                "recommended_specialists": [],
                "critical_metrics": [],
                "priority_level": "low",
                "action_taken": "none",
                "appointment_id": None,
                "agent_reasoning": localization_service.get_text("no_health_metrics_found", lang),
                "next_steps": [localization_service.get_text("upload_medical_report", lang)],
                "processed_at": datetime.now(),
                "patient": patient_data,
                "appointment": None
            },
            actions_taken=[localization_service.get_text("no_actions_taken", lang)],
            notifications_sent=[],
            appointment_booked=None
        )
    
    def _create_agent_recommendation_response(self, agent_rec: AgentRecommendation, lang: Language) -> Dict[str, Any]:
        """Create agent recommendation response from database object."""
        # Get patient data
        patient = self.db.query(User).filter(User.id == agent_rec.patient_id).first()
        patient_data = None
        if patient:
            patient_data = {
                "id": patient.id,
                "full_name": patient.full_name,
                "email": patient.email,
                "role": patient.role,
                "created_at": patient.created_at
            }
        
        # Get appointment data if exists
        appointment_data = None
        if agent_rec.appointment_id:
            appointment = self.db.query(Appointment).filter(Appointment.id == agent_rec.appointment_id).first()
            if appointment:
                appointment_data = self._create_appointment_response(appointment)
        
        # Localize specialist recommendations
        localized_specialists = []
        for specialist in agent_rec.recommended_specialists:
            specialist_type = specialist.get("type", "")
            specialist_info = localization_service.get_specialist_info(specialist_type, lang)
            
            localized_specialist = {
                "type": specialist_info["type"],
                "reason": specialist.get("reason", ""),  # Keep original reason for now
                "priority": specialist.get("priority", "medium"),
                "metrics_involved": specialist.get("metrics_involved", []),
                "description": specialist_info["description"],
                "when_to_consult": specialist_info["when_to_consult"]
            }
            localized_specialists.append(localized_specialist)
        
        # Localize next steps
        localized_next_steps = []
        for step in agent_rec.next_steps:
            # Try to map common next steps to localized versions
            if "urgent consultation" in step.lower():
                localized_next_steps.append(localization_service.get_text("schedule_urgent_consultation", lang))
            elif "liver function" in step.lower():
                localized_next_steps.append(localization_service.get_text("consider_liver_function", lang))
            elif "glucose" in step.lower() or "hba1c" in step.lower():
                localized_next_steps.append(localization_service.get_text("monitor_glucose", lang))
            elif "primary care" in step.lower():
                localized_next_steps.append(localization_service.get_text("follow_up_primary", lang))
            elif "lab results" in step.lower():
                localized_next_steps.append(localization_service.get_text("bring_previous_results", lang))
            elif "normal" in step.lower() and "range" in step.lower():
                localized_next_steps.append(localization_service.get_text("continue_monitoring", lang))
            else:
                localized_next_steps.append(step)  # Keep original if no mapping found
        
        return {
            "id": agent_rec.id,
            "patient_id": agent_rec.patient_id,
            "health_analysis_id": agent_rec.health_analysis_id,
            "recommended_specialists": localized_specialists,
            "critical_metrics": agent_rec.critical_metrics,
            "priority_level": agent_rec.priority_level,
            "action_taken": agent_rec.action_taken,
            "appointment_id": agent_rec.appointment_id,
            "agent_reasoning": agent_rec.agent_reasoning,
            "next_steps": localized_next_steps,
            "processed_at": agent_rec.processed_at,
            "patient": patient_data,
            "appointment": appointment_data
        }
    
    def _create_appointment_response(self, appointment: Appointment) -> Optional[Dict[str, Any]]:
        """Create appointment response from database object."""
        if not appointment:
            return None
        
        # Get patient data
        patient = self.db.query(User).filter(User.id == appointment.patient_id).first()
        patient_data = None
        if patient:
            patient_data = {
                "id": patient.id,
                "full_name": patient.full_name,
                "email": patient.email,
                "role": patient.role,
                "created_at": patient.created_at
            }
        
        # Get doctor data
        doctor = self.db.query(User).filter(User.id == appointment.doctor_id).first()
        doctor_data = None
        if doctor:
            doctor_data = {
                "id": doctor.id,
                "full_name": doctor.full_name,
                "email": doctor.email,
                "role": doctor.role,
                "created_at": doctor.created_at
            }
        
        return {
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "doctor_id": appointment.doctor_id,
            "health_analysis_id": appointment.health_analysis_id,
            "appointment_datetime": appointment.appointment_datetime,
            "duration_minutes": appointment.duration_minutes,
            "appointment_type": appointment.appointment_type,
            "reason": appointment.reason,
            "specialist_type": appointment.specialist_type,
            "priority_level": appointment.priority_level,
            "notes": appointment.notes,
            "status": appointment.status,
            "booking_method": appointment.booking_method,
            "created_at": appointment.created_at,
            "updated_at": appointment.updated_at,
            "patient": patient_data,
            "doctor": doctor_data
        } 
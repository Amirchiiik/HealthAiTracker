"""
Notification Service

Handles sending notifications via email and system messages for appointments,
health alerts, and agent recommendations.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
import logging

from ..models import User, Appointment, HealthAnalysis

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending various types of notifications."""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        
        # Check if email is configured
        self.email_enabled = all([self.smtp_username, self.smtp_password, self.from_email])
        
        if not self.email_enabled:
            logger.warning("Email notifications not configured. Set SMTP_USERNAME, SMTP_PASSWORD, and FROM_EMAIL environment variables.")
    
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send an email notification."""
        if not self.email_enabled:
            logger.warning(f"Email not configured. Would have sent: {subject} to {to_email}")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                text = msg.as_string()
                server.sendmail(self.from_email, to_email, text)
            
            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def notify_appointment_booked(self, patient: User, doctor: User, appointment: Appointment) -> List[str]:
        """Send notifications when an appointment is booked."""
        notifications_sent = []
        
        # Patient notification
        patient_subject = "Appointment Confirmation - AI Health Tracker"
        patient_body = f"""
        Dear {patient.full_name},

        Your appointment has been successfully booked with {doctor.full_name}.

        Appointment Details:
        - Doctor: {doctor.full_name} ({appointment.specialist_type or 'General'})
        - Date & Time: {appointment.appointment_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}
        - Type: {appointment.appointment_type.title()}
        - Duration: {appointment.duration_minutes} minutes
        - Reason: {appointment.reason or 'Health consultation'}
        
        {f"Priority: {appointment.priority_level.upper()}" if appointment.priority_level != 'low' else ""}
        
        {f"This appointment was automatically scheduled by our intelligent health agent based on your recent health analysis." if appointment.booking_method == 'auto_agent' else ""}
        
        Please arrive 15 minutes early for your appointment.
        
        If you need to reschedule or cancel, please contact us as soon as possible.
        
        Best regards,
        AI Health Tracker Team
        """
        
        if self.send_email(patient.email, patient_subject, patient_body):
            notifications_sent.append(f"Patient notification sent to {patient.email}")
        
        # Doctor notification
        doctor_subject = f"New Appointment Assigned - {patient.full_name}"
        doctor_body = f"""
        Dear Dr. {doctor.full_name},

        A new appointment has been scheduled with you.

        Patient Details:
        - Name: {patient.full_name}
        - Email: {patient.email}
        
        Appointment Details:
        - Date & Time: {appointment.appointment_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}
        - Type: {appointment.appointment_type.title()}
        - Duration: {appointment.duration_minutes} minutes
        - Priority: {appointment.priority_level.upper()}
        - Reason: {appointment.reason or 'Health consultation'}
        
        {f"⚠️ This is an URGENT appointment automatically scheduled by our intelligent health agent due to critical health metrics detected in the patient's recent analysis." if appointment.priority_level == 'high' and appointment.booking_method == 'auto_agent' else ""}
        
        {f"Notes: {appointment.notes}" if appointment.notes else ""}
        
        Please review the patient's health analysis before the appointment if available.
        
        Best regards,
        AI Health Tracker System
        """
        
        if self.send_email(doctor.email, doctor_subject, doctor_body):
            notifications_sent.append(f"Doctor notification sent to {doctor.email}")
        
        return notifications_sent
    
    def notify_critical_health_metrics(self, patient: User, critical_metrics: List[dict], 
                                      recommendations: List[dict]) -> List[str]:
        """Send notification when critical health metrics are detected."""
        notifications_sent = []
        
        subject = "⚠️ Important Health Alert - Critical Values Detected"
        
        # Format critical metrics
        metrics_text = ""
        for metric in critical_metrics:
            metrics_text += f"- {metric.get('name', 'Unknown')}: {metric.get('value', 'N/A')} {metric.get('unit', '')} (Status: {metric.get('status', 'abnormal').upper()})\n"
        
        # Format recommendations
        recommendations_text = ""
        for rec in recommendations:
            recommendations_text += f"- {rec.get('type', 'Specialist')}: {rec.get('reason', 'Consultation recommended')}\n"
        
        body = f"""
        Dear {patient.full_name},

        ⚠️ IMPORTANT HEALTH ALERT ⚠️

        Our intelligent health analysis system has detected critical values in your recent medical report that require immediate attention.

        Critical Metrics Detected:
        {metrics_text}

        Recommended Medical Specialists:
        {recommendations_text}

        NEXT STEPS:
        1. We are attempting to schedule you with an appropriate specialist automatically
        2. Please contact your primary care physician immediately
        3. If you experience any severe symptoms, seek emergency medical care
        4. Keep all previous lab results and medical records ready for your specialist visit

        ⚠️ IMPORTANT DISCLAIMER ⚠️
        This is an automated analysis and does not replace professional medical diagnosis. 
        Please consult with licensed healthcare professionals for proper medical evaluation and treatment.

        EMERGENCY: If you experience severe symptoms, chest pain, difficulty breathing, 
        or feel unwell, please seek immediate emergency medical attention.

        Best regards,
        AI Health Tracker Team

        ---
        This notification was generated by our Intelligent Health Agent based on your recent health analysis.
        """
        
        if self.send_email(patient.email, subject, body):
            notifications_sent.append(f"Critical health alert sent to {patient.email}")
        
        return notifications_sent
    
    def notify_agent_recommendation(self, patient: User, recommendations: dict, 
                                   actions_taken: List[str]) -> List[str]:
        """Send notification about agent recommendations and actions taken."""
        notifications_sent = []
        
        subject = f"Health Analysis Complete - {len(recommendations.get('recommended_specialists', []))} Recommendations"
        
        # Format specialist recommendations
        specialists_text = ""
        for specialist in recommendations.get('recommended_specialists', []):
            specialists_text += f"""
        • {specialist.get('type', 'Specialist')} (Priority: {specialist.get('priority', 'Medium')})
          Reason: {specialist.get('reason', 'Consultation recommended')}
          When to consult: {specialist.get('when_to_consult', 'As soon as possible')}
        """
        
        # Format next steps
        next_steps_text = ""
        for step in recommendations.get('next_steps', []):
            next_steps_text += f"• {step}\n"
        
        # Format actions taken
        actions_text = ""
        for action in actions_taken:
            actions_text += f"• {action}\n"
        
        body = f"""
        Dear {patient.full_name},

        Your health analysis has been completed by our Intelligent Health Agent.

        ANALYSIS SUMMARY:
        - {recommendations.get('abnormal_metrics_count', 0)} abnormal metrics detected
        - Overall priority level: {recommendations.get('priority_level', 'Unknown').upper()}
        - {len(recommendations.get('recommended_specialists', []))} specialist consultations recommended

        RECOMMENDED SPECIALISTS:
        {specialists_text}

        RECOMMENDED NEXT STEPS:
        {next_steps_text}

        ACTIONS TAKEN BY OUR SYSTEM:
        {actions_text}

        IMPORTANT NOTES:
        {recommendations.get('disclaimer', 'This analysis is for informational purposes only.')}

        {recommendations.get('emergency_note', 'If you feel unwell, seek immediate medical attention.')}

        You can view your complete health analysis and history by logging into your AI Health Tracker account.

        Best regards,
        AI Health Tracker Team
        """
        
        if self.send_email(patient.email, subject, body):
            notifications_sent.append(f"Agent recommendation report sent to {patient.email}")
        
        return notifications_sent
    
    def notify_booking_failed(self, patient: User, specialist_type: str, reason: str) -> List[str]:
        """Send notification when automatic booking fails."""
        notifications_sent = []
        
        subject = f"Appointment Booking Update - {specialist_type} Consultation"
        
        body = f"""
        Dear {patient.full_name},

        Our Intelligent Health Agent attempted to automatically schedule an appointment with a {specialist_type} 
        based on your recent health analysis, but was unable to complete the booking automatically.

        Reason: {reason}

        NEXT STEPS:
        1. Please log into your AI Health Tracker account to view available doctors
        2. Contact our support team to assist with manual booking
        3. You can also contact your primary care physician for a referral
        
        We recommend scheduling this appointment as soon as possible based on your health analysis results.

        For immediate assistance, please contact:
        - Support Email: support@aihealthtracker.com
        - Phone: [Your support phone number]

        Best regards,
        AI Health Tracker Team
        """
        
        if self.send_email(patient.email, subject, body):
            notifications_sent.append(f"Booking failed notification sent to {patient.email}")
        
        return notifications_sent
    
    def send_appointment_reminder(self, patient: User, doctor: User, appointment: Appointment) -> bool:
        """Send appointment reminder notification."""
        subject = f"Appointment Reminder - Tomorrow at {appointment.appointment_datetime.strftime('%I:%M %p')}"
        
        body = f"""
        Dear {patient.full_name},

        This is a reminder of your upcoming appointment:

        Doctor: {doctor.full_name}
        Date: {appointment.appointment_datetime.strftime('%A, %B %d, %Y')}
        Time: {appointment.appointment_datetime.strftime('%I:%M %p')}
        Location: [Clinic address would go here]

        Please arrive 15 minutes early and bring:
        - A valid ID
        - Insurance card (if applicable)
        - List of current medications
        - Previous lab results or medical records

        If you need to reschedule or cancel, please contact us at least 24 hours in advance.

        Best regards,
        AI Health Tracker Team
        """
        
        return self.send_email(patient.email, subject, body)

# Global notification service instance
notification_service = NotificationService() 
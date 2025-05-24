"""
Appointment Service

Handles appointment booking, doctor availability, scheduling, and appointment management.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging
import pytz

from ..models import Appointment, User, DoctorAvailability, HealthAnalysis
from ..schemas import (
    AppointmentCreate, AppointmentType, AppointmentStatus, PriorityLevel, 
    BookingMethod, UserRole
)

logger = logging.getLogger(__name__)

class AppointmentService:
    """Service for managing appointments and doctor scheduling."""
    
    def __init__(self, db: Session):
        self.db = db
        # Use UTC timezone for consistent datetime handling
        self.timezone = pytz.UTC
    
    def _ensure_timezone_aware(self, dt: datetime) -> datetime:
        """Ensure datetime object is timezone-aware."""
        if dt.tzinfo is None:
            return self.timezone.localize(dt)
        return dt.astimezone(self.timezone)
    
    def _get_current_time_aware(self) -> datetime:
        """Get current time as timezone-aware datetime."""
        return datetime.now(self.timezone)
    
    def find_available_doctors_by_specialty(self, specialty: str, limit: int = 10) -> List[User]:
        """Find available doctors by medical specialty."""
        try:
            doctors = self.db.query(User).filter(
                and_(
                    User.role == UserRole.DOCTOR,
                    User.medical_specialty == specialty,
                    User.is_available_for_booking == True
                )
            ).limit(limit).all()
            
            logger.info(f"Found {len(doctors)} available doctors for specialty: {specialty}")
            return doctors
            
        except Exception as e:
            logger.error(f"Error finding doctors by specialty {specialty}: {e}")
            return []
    
    def find_next_available_slot(self, doctor_id: int, 
                                preferred_datetime: Optional[datetime] = None,
                                appointment_duration: int = 60) -> Optional[datetime]:
        """Find the next available appointment slot for a doctor."""
        try:
            # Start from preferred time or current time + 1 hour
            start_time = preferred_datetime or (self._get_current_time_aware() + timedelta(hours=1))
            # Ensure start_time is timezone-aware
            start_time = self._ensure_timezone_aware(start_time)
            
            # Get doctor's availability
            availability = self.db.query(DoctorAvailability).filter(
                and_(
                    DoctorAvailability.doctor_id == doctor_id,
                    DoctorAvailability.is_active == True
                )
            ).all()
            
            if not availability:
                logger.warning(f"No availability set for doctor {doctor_id}")
                return None
            
            # Get existing appointments for the doctor
            existing_appointments = self.db.query(Appointment).filter(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.status.in_(['scheduled', 'confirmed']),
                    Appointment.appointment_datetime >= start_time
                )
            ).all()
            
            # Check availability for the next 30 days
            for days_ahead in range(30):
                check_date = start_time + timedelta(days=days_ahead)
                day_of_week = check_date.weekday()  # 0=Monday, 6=Sunday
                
                # Find availability for this day of week
                day_availability = [av for av in availability if av.day_of_week == day_of_week]
                
                for av in day_availability:
                    # Parse start and end times
                    start_hour, start_minute = map(int, av.start_time.split(':'))
                    end_hour, end_minute = map(int, av.end_time.split(':'))
                    
                    # Create timezone-aware datetime objects
                    day_start = check_date.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                    day_end = check_date.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
                    
                    # Check slots every 30 minutes
                    current_slot = day_start
                    while current_slot + timedelta(minutes=appointment_duration) <= day_end:
                        slot_end = current_slot + timedelta(minutes=appointment_duration)
                        
                        # Check if this slot conflicts with existing appointments
                        # Ensure both datetimes are timezone-aware for comparison
                        conflict = any(
                            (current_slot < self._ensure_timezone_aware(apt.appointment_datetime) + timedelta(minutes=apt.duration_minutes) and
                             slot_end > self._ensure_timezone_aware(apt.appointment_datetime))
                            for apt in existing_appointments
                        )
                        
                        if not conflict and current_slot >= start_time:
                            logger.info(f"Found available slot for doctor {doctor_id}: {current_slot}")
                            return current_slot
                        
                        current_slot += timedelta(minutes=30)
            
            logger.warning(f"No available slots found for doctor {doctor_id} in next 30 days")
            return None
            
        except Exception as e:
            logger.error(f"Error finding available slot for doctor {doctor_id}: {e}")
            return None
    
    def book_appointment(self, patient_id: int, appointment_data: AppointmentCreate,
                        booking_method: BookingMethod = BookingMethod.MANUAL) -> Optional[Appointment]:
        """Book an appointment with a doctor."""
        try:
            # Validate doctor exists and is available
            doctor = self.db.query(User).filter(
                and_(
                    User.id == appointment_data.doctor_id,
                    User.role == UserRole.DOCTOR,
                    User.is_available_for_booking == True
                )
            ).first()
            
            if not doctor:
                logger.error(f"Doctor {appointment_data.doctor_id} not found or not available")
                return None
            
            # Ensure appointment datetime is timezone-aware
            appointment_datetime = self._ensure_timezone_aware(appointment_data.appointment_datetime)
            appointment_end = appointment_datetime + timedelta(minutes=appointment_data.duration_minutes)
            
            # Check if the requested time slot is available by getting all existing appointments
            # and checking for conflicts in Python (simpler than complex SQL with timedelta)
            existing_appointments = self.db.query(Appointment).filter(
                and_(
                    Appointment.doctor_id == appointment_data.doctor_id,
                    Appointment.status.in_(['scheduled', 'confirmed'])
                )
            ).all()
            
            # Check for time conflicts
            for existing in existing_appointments:
                existing_start = self._ensure_timezone_aware(existing.appointment_datetime)
                existing_end = existing_start + timedelta(minutes=existing.duration_minutes)
                
                # Check if there's any overlap
                if (appointment_datetime < existing_end and appointment_end > existing_start):
                    logger.error(f"Time slot conflict for doctor {appointment_data.doctor_id} at {appointment_datetime}")
                    return None
            
            # Create the appointment
            appointment = Appointment(
                patient_id=patient_id,
                doctor_id=appointment_data.doctor_id,
                health_analysis_id=appointment_data.health_analysis_id,
                appointment_datetime=appointment_datetime,
                duration_minutes=appointment_data.duration_minutes,
                appointment_type=appointment_data.appointment_type,
                reason=appointment_data.reason,
                specialist_type=appointment_data.specialist_type,
                priority_level=appointment_data.priority_level,
                notes=appointment_data.notes,
                booking_method=booking_method,
                status=AppointmentStatus.SCHEDULED
            )
            
            self.db.add(appointment)
            self.db.commit()
            self.db.refresh(appointment)
            
            logger.info(f"Successfully booked appointment {appointment.id} for patient {patient_id} with doctor {appointment_data.doctor_id}")
            return appointment
            
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            self.db.rollback()
            return None
    
    def auto_book_appointment(self, patient_id: int, specialist_type: str, 
                             priority_level: PriorityLevel, reason: str,
                             health_analysis_id: int,
                             preferred_datetime: Optional[datetime] = None) -> Tuple[Optional[Appointment], str]:
        """Automatically book appointment with the best available doctor."""
        try:
            # Find available doctors for the specialist type
            doctors = self.find_available_doctors_by_specialty(specialist_type)
            
            if not doctors:
                return None, f"No available {specialist_type} doctors found"
            
            # Determine appointment type based on priority
            if priority_level == PriorityLevel.HIGH:
                appointment_type = AppointmentType.URGENT
                max_days_ahead = 2  # Try to book within 2 days for high priority
            elif priority_level == PriorityLevel.MEDIUM:
                appointment_type = AppointmentType.ROUTINE
                max_days_ahead = 7  # Try to book within 1 week for medium priority
            else:
                appointment_type = AppointmentType.ROUTINE
                max_days_ahead = 14  # Try to book within 2 weeks for low priority
            
            # Try to find an available slot with each doctor
            best_appointment = None
            earliest_time = None
            
            for doctor in doctors:
                available_slot = self.find_next_available_slot(
                    doctor.id, 
                    preferred_datetime,
                    60 if priority_level != PriorityLevel.HIGH else 30  # Shorter slots for urgent appointments
                )
                
                if available_slot:
                    # Check if it's within the acceptable timeframe
                    if available_slot <= self._get_current_time_aware() + timedelta(days=max_days_ahead):
                        # This is acceptable, try to book
                        appointment_data = AppointmentCreate(
                            doctor_id=doctor.id,
                            health_analysis_id=health_analysis_id,
                            appointment_datetime=available_slot,
                            duration_minutes=60 if priority_level != PriorityLevel.HIGH else 30,
                            appointment_type=appointment_type,
                            reason=reason,
                            specialist_type=specialist_type,
                            priority_level=priority_level,
                            notes=f"Automatically booked by intelligent health agent due to {priority_level.value} priority health metrics"
                        )
                        
                        appointment = self.book_appointment(patient_id, appointment_data, BookingMethod.AUTO_AGENT)
                        
                        if appointment:
                            logger.info(f"Successfully auto-booked appointment {appointment.id} with {doctor.full_name}")
                            return appointment, f"Successfully booked appointment with {doctor.full_name} on {available_slot.strftime('%Y-%m-%d at %H:%M')}"
                    
                    # Keep track of the earliest available slot even if it's outside preferred timeframe
                    if earliest_time is None or available_slot < earliest_time:
                        earliest_time = available_slot
                        best_doctor = doctor
            
            # If we couldn't book within the preferred timeframe, return the earliest available
            if earliest_time:
                return None, f"Earliest available appointment with {best_doctor.full_name} is on {earliest_time.strftime('%Y-%m-%d at %H:%M')}. Please book manually if acceptable."
            else:
                return None, f"No available appointment slots found with {specialist_type} doctors in the next 30 days"
            
        except Exception as e:
            logger.error(f"Error in auto-booking appointment: {e}")
            return None, f"Error occurred while booking appointment: {str(e)}"
    
    def get_user_appointments(self, user_id: int, role: str, 
                             status_filter: Optional[str] = None,
                             limit: int = 50, offset: int = 0) -> List[Appointment]:
        """Get appointments for a user (patient or doctor)."""
        try:
            query = self.db.query(Appointment)
            
            if role == UserRole.PATIENT:
                query = query.filter(Appointment.patient_id == user_id)
            elif role == UserRole.DOCTOR:
                query = query.filter(Appointment.doctor_id == user_id)
            
            if status_filter:
                query = query.filter(Appointment.status == status_filter)
            
            appointments = query.order_by(Appointment.appointment_datetime.desc()).offset(offset).limit(limit).all()
            
            logger.info(f"Retrieved {len(appointments)} appointments for user {user_id}")
            return appointments
            
        except Exception as e:
            logger.error(f"Error getting appointments for user {user_id}: {e}")
            return []
    
    def update_appointment_status(self, appointment_id: int, new_status: AppointmentStatus,
                                 user_id: int, user_role: str) -> Optional[Appointment]:
        """Update appointment status (with permission checking)."""
        try:
            appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
            
            if not appointment:
                logger.error(f"Appointment {appointment_id} not found")
                return None
            
            # Check permissions
            if user_role == UserRole.PATIENT and appointment.patient_id != user_id:
                logger.error(f"Patient {user_id} not authorized to modify appointment {appointment_id}")
                return None
            elif user_role == UserRole.DOCTOR and appointment.doctor_id != user_id:
                logger.error(f"Doctor {user_id} not authorized to modify appointment {appointment_id}")
                return None
            
            appointment.status = new_status
            self.db.commit()
            self.db.refresh(appointment)
            
            logger.info(f"Updated appointment {appointment_id} status to {new_status}")
            return appointment
            
        except Exception as e:
            logger.error(f"Error updating appointment {appointment_id}: {e}")
            self.db.rollback()
            return None
    
    def create_doctor_availability(self, doctor_id: int, day_of_week: int,
                                  start_time: str, end_time: str) -> Optional[DoctorAvailability]:
        """Create availability schedule for a doctor."""
        try:
            # Check if doctor exists
            doctor = self.db.query(User).filter(
                and_(User.id == doctor_id, User.role == UserRole.DOCTOR)
            ).first()
            
            if not doctor:
                logger.error(f"Doctor {doctor_id} not found")
                return None
            
            # Check if availability already exists for this day
            existing = self.db.query(DoctorAvailability).filter(
                and_(
                    DoctorAvailability.doctor_id == doctor_id,
                    DoctorAvailability.day_of_week == day_of_week,
                    DoctorAvailability.is_active == True
                )
            ).first()
            
            if existing:
                # Update existing availability
                existing.start_time = start_time
                existing.end_time = end_time
                self.db.commit()
                self.db.refresh(existing)
                logger.info(f"Updated availability for doctor {doctor_id} on day {day_of_week}")
                return existing
            else:
                # Create new availability
                availability = DoctorAvailability(
                    doctor_id=doctor_id,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                    is_active=True
                )
                
                self.db.add(availability)
                self.db.commit()
                self.db.refresh(availability)
                
                logger.info(f"Created availability for doctor {doctor_id} on day {day_of_week}")
                return availability
            
        except Exception as e:
            logger.error(f"Error creating doctor availability: {e}")
            self.db.rollback()
            return None 
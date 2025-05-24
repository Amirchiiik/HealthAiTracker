"""
Appointments Router

Provides API endpoints for appointment booking, scheduling, and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from ..database import get_db
from ..auth import get_current_user, get_current_doctor, get_current_patient
from ..models import User, Appointment
from ..schemas import (
    AppointmentCreate, AppointmentResponse, AppointmentUpdate,
    DoctorAvailabilityCreate, DoctorAvailabilityResponse,
    AvailableDoctorsResponse, AutoBookingRequest, AutoBookingResponse,
    AppointmentStatus, UserRole
)
from ..services.appointment_service import AppointmentService
from ..services.notification_service import notification_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/book", response_model=AppointmentResponse)
async def book_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_patient),  # Only patients can book
    db: Session = Depends(get_db)
):
    """
    Book a new appointment with a doctor.
    
    Only patients can book appointments. The appointment will be created with 'scheduled' status.
    """
    try:
        appointment_service = AppointmentService(db)
        
        appointment = appointment_service.book_appointment(
            patient_id=current_user.id,
            appointment_data=appointment_data
        )
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to book appointment. Doctor may not be available at the requested time."
            )
        
        # Send notification to both patient and doctor
        doctor = db.query(User).filter(User.id == appointment.doctor_id).first()
        if doctor:
            notification_service.notify_appointment_booked(current_user, doctor, appointment)
        
        # Return appointment with related data
        appointment_response = AppointmentResponse.from_orm(appointment)
        
        logger.info(f"Appointment {appointment.id} booked successfully for patient {current_user.id}")
        return appointment_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error booking appointment for patient {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to book appointment. Please try again later."
        )

@router.post("/auto-book", response_model=AutoBookingResponse)
async def auto_book_appointment(
    booking_request: AutoBookingRequest,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """
    Automatically book an appointment with the best available doctor for a specific specialty.
    
    This endpoint attempts to find and book the earliest available appointment
    with a doctor of the requested specialty.
    """
    try:
        appointment_service = AppointmentService(db)
        
        appointment, message = appointment_service.auto_book_appointment(
            patient_id=current_user.id,
            specialist_type=booking_request.specialist_type,
            priority_level=booking_request.priority_level,
            reason=booking_request.reason,
            health_analysis_id=booking_request.health_analysis_id,
            preferred_datetime=booking_request.preferred_datetime
        )
        
        if appointment:
            # Send notifications
            doctor = db.query(User).filter(User.id == appointment.doctor_id).first()
            if doctor:
                notification_service.notify_appointment_booked(current_user, doctor, appointment)
            
            appointment_response = AppointmentResponse.from_orm(appointment)
            
            return AutoBookingResponse(
                success=True,
                appointment=appointment_response,
                message=message,
                available_doctors=[],
                next_available_slot=None
            )
        else:
            # Get available doctors for manual booking
            available_doctors = appointment_service.find_available_doctors_by_specialty(
                booking_request.specialist_type
            )
            
            # Find next available slot from any doctor
            next_slot = None
            for doctor in available_doctors:
                slot = appointment_service.find_next_available_slot(doctor.id, booking_request.preferred_datetime)
                if slot and (next_slot is None or slot < next_slot):
                    next_slot = slot
            
            return AutoBookingResponse(
                success=False,
                appointment=None,
                message=message,
                available_doctors=[],  # Would populate with DoctorProfileResponse if needed
                next_available_slot=next_slot
            )
        
    except Exception as e:
        logger.error(f"Error in auto-booking for patient {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to auto-book appointment. Please try manual booking."
        )

@router.get("/my-appointments", response_model=List[AppointmentResponse])
async def get_my_appointments(
    status_filter: Optional[str] = Query(None, description="Filter by appointment status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's appointments (for both patients and doctors).
    
    - Patients see their booked appointments
    - Doctors see appointments scheduled with them
    """
    try:
        appointment_service = AppointmentService(db)
        
        appointments = appointment_service.get_user_appointments(
            user_id=current_user.id,
            role=current_user.role,
            status_filter=status_filter,
            limit=limit,
            offset=offset
        )
        
        return [AppointmentResponse.from_orm(apt) for apt in appointments]
        
    except Exception as e:
        logger.error(f"Error getting appointments for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve appointments."
        )

@router.put("/{appointment_id}/status", response_model=AppointmentResponse)
async def update_appointment_status(
    appointment_id: int,
    status_update: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update appointment status or details.
    
    - Patients can cancel their appointments
    - Doctors can confirm, complete, or cancel appointments assigned to them
    """
    try:
        appointment_service = AppointmentService(db)
        
        if not status_update.status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status is required for update"
            )
        
        appointment = appointment_service.update_appointment_status(
            appointment_id=appointment_id,
            new_status=status_update.status,
            user_id=current_user.id,
            user_role=current_user.role
        )
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found or unauthorized"
            )
        
        # Update other fields if provided
        if status_update.notes is not None:
            appointment.notes = status_update.notes
        if status_update.appointment_datetime is not None:
            appointment.appointment_datetime = status_update.appointment_datetime
        
        db.commit()
        db.refresh(appointment)
        
        logger.info(f"Appointment {appointment_id} updated by user {current_user.id}")
        return AppointmentResponse.from_orm(appointment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment {appointment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update appointment."
        )

@router.get("/available-doctors", response_model=AvailableDoctorsResponse)
async def get_available_doctors(
    specialty: Optional[str] = Query(None, description="Filter by medical specialty"),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """
    Get list of available doctors for booking appointments.
    
    Only patients can access this endpoint to find doctors for booking.
    """
    try:
        appointment_service = AppointmentService(db)
        
        if specialty:
            doctors = appointment_service.find_available_doctors_by_specialty(specialty, limit)
        else:
            # Get all available doctors
            doctors = db.query(User).filter(
                User.role == UserRole.DOCTOR,
                User.is_available_for_booking == True
            ).limit(limit).all()
        
        return AvailableDoctorsResponse(
            doctors=[],  # Would populate with DoctorProfileResponse if needed
            specialty=specialty,
            total_count=len(doctors)
        )
        
    except Exception as e:
        logger.error(f"Error getting available doctors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve available doctors."
        )

@router.post("/availability", response_model=DoctorAvailabilityResponse)
async def set_doctor_availability(
    availability_data: DoctorAvailabilityCreate,
    current_user: User = Depends(get_current_doctor),  # Only doctors can set availability
    db: Session = Depends(get_db)
):
    """
    Set or update doctor's availability schedule.
    
    Only doctors can set their own availability for appointment booking.
    """
    try:
        appointment_service = AppointmentService(db)
        
        availability = appointment_service.create_doctor_availability(
            doctor_id=current_user.id,
            day_of_week=availability_data.day_of_week,
            start_time=availability_data.start_time,
            end_time=availability_data.end_time
        )
        
        if not availability:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to set availability. Please check the time format."
            )
        
        logger.info(f"Availability set for doctor {current_user.id}")
        return DoctorAvailabilityResponse.from_orm(availability)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting availability for doctor {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to set availability."
        )

@router.get("/availability", response_model=List[DoctorAvailabilityResponse])
async def get_doctor_availability(
    doctor_id: Optional[int] = Query(None, description="Get availability for specific doctor"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get doctor availability schedule.
    
    - If doctor_id is provided, get that doctor's availability (patients can see any doctor's availability)
    - If doctor_id is not provided and user is a doctor, get their own availability
    """
    try:
        if doctor_id:
            # Get specific doctor's availability
            target_doctor_id = doctor_id
        elif current_user.role == UserRole.DOCTOR:
            # Doctor getting their own availability
            target_doctor_id = current_user.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor ID is required for patients"
            )
        
        from ..models import DoctorAvailability
        availability = db.query(DoctorAvailability).filter(
            DoctorAvailability.doctor_id == target_doctor_id,
            DoctorAvailability.is_active == True
        ).all()
        
        return [DoctorAvailabilityResponse.from_orm(av) for av in availability]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting doctor availability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve availability."
        )

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific appointment details.
    
    Users can only access appointments they are involved in (as patient or doctor).
    """
    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Check authorization
        if (current_user.role == UserRole.PATIENT and appointment.patient_id != current_user.id) or \
           (current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this appointment"
            )
        
        return AppointmentResponse.from_orm(appointment)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting appointment {appointment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve appointment."
        ) 
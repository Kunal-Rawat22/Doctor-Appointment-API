from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, create_access_token, verify_password
from app.models.Availability import Availability
from app.models.Appointment import Appointment
from ..schemas import appointmentSchema
from ..repository import appointment_repository, user_repository, availability_repository
from ..models.enums import UserRole
from datetime import datetime

async def create_appointment(request: appointmentSchema.AppointmentRequestCO, db: AsyncSession):
    doctor_id = request.doctor_id
    patient_id = request.patient_id
    start_time = request.start_time
    end_time = request.end_time
    availability_id = request.availability_id

    await verify_doctor_and_patient(db, doctor_id, patient_id)
    await verify_duplicate_booking(db, doctor_id, patient_id, availability_id)

    availability =  await verify_consistent_booking_with_availability(db, end_time, start_time, availability_id)
    availability.booked_appointments+=1
    await availability_repository.update_availability(db, availability)

    new_appointment = Appointment(doctor_id = doctor_id, 
                                  patient_id=patient_id, 
                                  start_time=start_time, 
                                  end_time=end_time, 
                                  availability_id = availability_id)
    return await appointment_repository.save_appointment(db, new_appointment)

# validate the doctors and patients
async def verify_doctor_and_patient(db: AsyncSession, doctor_id: int, patient_id: int):
    doctor = await user_repository.get_user_by_id_and_role(db, doctor_id, UserRole.DOCTOR)
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Doctor not found with id: {doctor_id}")
    
    patient = await user_repository.get_user_by_id_and_role(db, patient_id, UserRole.PATIENT)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient not found with id: {patient_id}")
    
# Validate to avoid duplicate booking
async def verify_duplicate_booking(db: AsyncSession, doctor_id: int, patient_id: int, availability_id: int):
    existing_appointment = await appointment_repository.fetch_by_doctor_id_and_patient_id_and_availability_id(doctor_id, patient_id, availability_id, db)

    if existing_appointment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Already booked appointment with id: {existing_appointment.id}")
    
# Validate appointment with availabilty for consistent booking
async def verify_consistent_booking_with_availability(db: AsyncSession, end_time: datetime , start_time: datetime, availability_id: int):
    start_time = start_time.replace(tzinfo=None)
    end_time = end_time.replace(tzinfo=None)
    availability = await availability_repository.get_availability_by_id(db, availability_id)
    if not availability_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Availibility not found with id: {availability_id}")
    
    if start_time < availability.start_time and end_time > availability.end_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Appointment timing not within the time range of given availability")
    
    if availability.booked_appointments >= availability.max_appointments:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No. of booked appointments has exceeded max appointments")
    
    return availability
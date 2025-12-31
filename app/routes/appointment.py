from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from ..schemas import appointmentSchema
from ..service import appointment_service
from app.models.enums import UserRole
from app.dependencies import auth, roles

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("",status_code=status.HTTP_201_CREATED, response_model=appointmentSchema.AppointmentResponseDTO)
async def create_appointment(request: appointmentSchema.AppointmentRequestCO, db: AsyncSession = Depends(get_db), current_user=Depends(roles.require_role(UserRole.PATIENT))):
    return await appointment_service.create_appointment(request, db)

@router.delete("/cancel/{appointment_id}", status_code=status.HTTP_200_OK)
async def cancel_appointment(appointment_id, patient_id, db: AsyncSession = Depends(get_db), current_user=Depends(roles.require_role(UserRole.PATIENT))):
    return await appointment_service.cancel_apppointment(appointment_id, patient_id, db)

@router.get("/doctor/{doctor_id}", status_code=status.HTTP_200_OK, response_model=list[appointmentSchema.AppointmentResponseDTO])
async def doctor_upcoming_appointments(doctor_id, limit: int = 10, page: int = 0, db: AsyncSession = Depends(get_db), current_user=Depends(roles.require_role(UserRole.DOCTOR))):
    return await appointment_service.fetch_all_doctor_upcoming_appointments(doctor_id, limit, page*limit, db)

@router.get("/patient/{patient_id}", status_code=status.HTTP_200_OK, response_model=list[appointmentSchema.AppointmentResponseDTO])
async def patient_upcoming_appointments(patient_id, limit: int = 10, page: int = 0, db: AsyncSession = Depends(get_db), current_user=Depends(roles.require_role(UserRole.PATIENT))):
    return await appointment_service.fetch_all_patient_upcoming_appointments(patient_id, limit, page*limit, db)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post()
async def create_appointment():
    pass

@router.put("/cancel/{id}")
async def cancel_appointment():
    pass

@router.get("/doctor/{doctor_id}")
async def doctor_upcoming_appointments():
    pass

@router.get("/patient/{patient_id}")
async def patient_upcoming_appointments():
    pass
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..schemas import userSchema, availbilitySchema
from ..service import doctor_service
from app.models.enums import UserRole
from app.dependencies import auth, roles

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.get("", status_code=status.HTTP_200_OK, response_model=list[userSchema.UserResponseDTO])
async def fetch_all_doctors(limit: int = 10, page: int = 0, db: AsyncSession = Depends(get_db), current_user=Depends(auth.get_current_user)):
    return await doctor_service.fetch_all_doctors(limit, page, db)

@router.get("/{doctor_id}/availability", status_code=status.HTTP_200_OK, response_model=list[availbilitySchema.AvailabilityResponseDTO])
async def fetch_availability_of_doctor(doctor_id, limit: int = 10, page: int = 0, db: AsyncSession = Depends(get_db), current_user=Depends(auth.get_current_user)):
    return await doctor_service.fetch_availabilty_of_doctor(doctor_id, limit, page, db)

@router.post("/availability", status_code=status.HTTP_201_CREATED, response_model=availbilitySchema.AvailabilityResponseDTO)
async def set_availability(request: availbilitySchema.AvailabilitySetRequestCO, db: AsyncSession = Depends(get_db), current_user=Depends(roles.require_role(UserRole.DOCTOR))):
    return await doctor_service.set_availability(request, db)

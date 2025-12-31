from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..schemas import userSchema, availbilitySchema
from ..service import doctor_service

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.get("", status_code=status.HTTP_200_OK, response_model=list[userSchema.UserResponseDTO])
async def fetch_all_doctors(limit: int = 10, page: int = 0, db: AsyncSession = Depends(get_db)):
    return await doctor_service.fetch_all_doctors(limit, page, db)

@router.get("/{id}/availabilty")
async def fetch_availabilty_of_doctor():
    pass

@router.post("/availabilty", status_code=status.HTTP_201_CREATED)
async def set_availabilty(request: availbilitySchema.AvailabilitySetRequestCO, db: AsyncSession = Depends(get_db)):
    return await doctor_service.set_availability(request, db)

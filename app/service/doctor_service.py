from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, create_access_token, verify_password
from app.models.Availability import Availability
from ..schemas import userSchema, availbilitySchema
from ..repository import availability_repository, user_repository

async def fetch_all_doctors(limit:int, page:int, db: AsyncSession):
    return await user_repository.fetch_all_doctors(limit, page*limit, db)

async def set_availability(request: availbilitySchema.AvailabilitySetRequestCO, db: AsyncSession):
    # Check if the user exists and is doctor
    # Most probably this apit will be role based
    doctor_id = request.doctor_id
    start_time = request.start_time
    end_time = request.end_time

    existing_user = await user_repository.get_user_by_id(db, doctor_id)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Doctor not found with id: {doctor_id}")
    
    if start_time>end_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start Time can't be after end Time" )
    
    new_availability = Availability(doctor_id = doctor_id, start_time = start_time, end_time = end_time)
    return await availability_repository.save_availability(db, new_availability)
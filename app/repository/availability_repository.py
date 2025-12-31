from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, create_access_token
from app.models.Availability import Availability
from ..schemas import userSchema
from sqlalchemy import select, and_
from ..models.enums import UserRole
from datetime import datetime

async def save_availability(db: AsyncSession, availability: Availability):
    db.add(availability)
    await db.commit()
    await db.refresh(availability)
    return availability

async def fetch_all_availability_of_doctor_by_id(doctor_id: int, limit: int, offset: int, db: AsyncSession):
    query = (
            select(Availability)
            .where(
                and_(
                    Availability.doctor_id == doctor_id,
                    Availability.end_time > datetime.now(),
                    Availability.max_appointments > Availability.booked_appointments
                )
            )
            .order_by(Availability.id)
            .offset(offset)
            .limit(limit)
        )

    result = await db.execute(query)
    return result.scalars().all()

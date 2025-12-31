from sqlalchemy.ext.asyncio import AsyncSession
from app.models.Availability import Availability
from sqlalchemy import select, and_
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

async def get_availability_by_id(db: AsyncSession, id: str):
    result = await db.execute(select(Availability).where(Availability.id == id))
    return result.scalars().first()

async def update_availability(db: AsyncSession, availability: Availability):
    await db.commit()
    await db.refresh(availability)
    return availability

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, create_access_token
from app.models.Availability import Availability
from ..schemas import userSchema
from sqlalchemy import select
from ..models.enums import UserRole

async def save_availability(db: AsyncSession, availability: Availability):
    db.add(availability)
    await db.commit()
    await db.refresh(availability)
    return availability
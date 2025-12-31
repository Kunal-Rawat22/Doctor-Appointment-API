from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, create_access_token
from app.models.user import User
from ..schemas import userSchema
from sqlalchemy import select, and_
from ..models.enums import UserRole

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def save_user(db: AsyncSession, user: User):
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user(db: AsyncSession, user: User):
    await db.commit()
    await db.refresh(user)
    return user

async def fetch_all_doctors(limit: int, offset:int, db:AsyncSession):
    result = await db.execute(select(User).where(User.role==UserRole.DOCTOR).order_by(User.id).offset(offset).limit(limit))
    return result.scalars().all()

async def get_user_by_id(db: AsyncSession, id: str):
    result = await db.execute(select(User).where(User.id == id))
    return result.scalars().first()

async def get_user_by_id_and_role(db: AsyncSession, id: str, role: UserRole):
    result = await db.execute(
        select(User).where(
            and_(
                User.id == id,
                User.role == role
            )
        )
    )
    return result.scalars().first()
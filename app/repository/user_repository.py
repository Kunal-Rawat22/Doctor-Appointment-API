from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, create_access_token
from app.models.user import User
from ..schemas import userSchema
from sqlalchemy import select

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

def save_user(db: AsyncSession, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

async def update_user(db: AsyncSession, user: User):
    await db.commit()
    await db.refresh(user)
    return user
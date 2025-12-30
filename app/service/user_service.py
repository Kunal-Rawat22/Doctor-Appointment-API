from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, create_access_token
from app.models.user import User
from ..schemas import userSchema
from ..repository import user_repository

async def create_user(db: AsyncSession, user: userSchema.UserRequestCO):
    # Check if user exists
    if 'doctor' != user.role or 'patient' != user.role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Role")
 
    existing_user = await user_repository.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(email: str, password: str, db: AsyncSession = Depends(get_db)):
    user = User(
        email=email,
        hashed_password=hash_password(password)
    )
    db.add(user)
    await db.commit()
    return {"msg": "User created"}

@router.post("/login")
async def login():
    pass

@router.put("/forget-password")
async def forget_password():
    pass

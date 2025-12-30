from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from app.core.security import hash_password, create_access_token
from ..schemas import userSchema
from ..service import user_service
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=userSchema.UserResponseDTO)
async def register(request: userSchema.UserRequestCO, db: AsyncSession = Depends(get_db)):
    return await user_service.create_user(db, request)

@router.post("/login")
async def login():
    pass

@router.put("/forget-password")
async def forget_password():
    pass

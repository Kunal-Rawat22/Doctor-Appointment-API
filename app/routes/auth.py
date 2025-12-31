from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..schemas import userSchema
from ..service import user_service
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=userSchema.UserResponseDTO)
async def register(request: userSchema.UserRequestCO, db: AsyncSession = Depends(get_db)):
    return await user_service.create_user(db, request)

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(request: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    return await user_service.login_user(db, request)

@router.put("/forgot-password", status_code=status.HTTP_200_OK)
async def forget_password(request: userSchema.UserForgetPasswordCO, db: AsyncSession = Depends(get_db)):
    return await user_service.forget_password(db, request)

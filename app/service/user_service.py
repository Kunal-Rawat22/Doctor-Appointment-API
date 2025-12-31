from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, create_access_token, verify_password
from app.models.user import User
from ..schemas import userSchema
from ..repository import user_repository

async def create_user(db: AsyncSession, user: userSchema.UserRequestCO):
    print(user)
    if 'DOCTOR' != user.role and 'PATIENT' != user.role:
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
    return await user_repository.save_user(db, db_user)

async def login_user(db: AsyncSession, request: userSchema.UserLoginRequestCO):
    existing_user = await user_repository.get_user_by_email(db, request.email)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    if not verify_password(request.password, existing_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    access_token = create_access_token(data={'sub': existing_user.email})
    return {'access_token': access_token, "token_type": "bearer"}

async def forget_password(db: AsyncSession, request: userSchema.UserForgetPasswordCO):
    existing_user = await user_repository.get_user_by_email(db, request.email)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if request.otp != '123456':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP")
    existing_user.hashed_password = hash_password(request.new_password)
    await user_repository.update_user(db, existing_user)
    return {"message":"Password Updated Successfully"}
    
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.get()
async def fetch_all_doctors():
    pass

@router.get("/{id}/availabilty")
async def fetch_availabilty_of_doctor():
    pass

@router.post("/availabilty")
async def set_availabilty():
    pass

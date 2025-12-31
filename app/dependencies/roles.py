from fastapi import Depends, HTTPException, status
from app.models.enums import UserRole
from .auth import get_current_user

def require_role(*roles: UserRole):
    async def role_checker(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        return user
    return role_checker

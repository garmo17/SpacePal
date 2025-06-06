from fastapi import Depends, HTTPException, status
from backend.api.services.auth_service import get_current_user
from backend.api.models.users import UserDB

async def is_admin(current_user: UserDB = Depends(get_current_user)) -> UserDB:
    if current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido solo para el usuario admin"
        )
    return current_user

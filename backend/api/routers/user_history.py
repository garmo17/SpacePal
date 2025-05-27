from fastapi import APIRouter, status, HTTPException, Depends
from backend.api.dependencies.auth import get_current_user
from backend.api.schemas.user_history import UserHistoryCreate, UserHistoryRead
from backend.api.services import user_history as user_history_service
from typing import List
from backend.api.models.users import UserDB

router = APIRouter(prefix="/user_history", tags=["user_history"])

@router.post("/", response_model=UserHistoryRead, status_code=status.HTTP_201_CREATED)
async def create_user_history(
    history_data: UserHistoryCreate,
    current_user: UserDB = Depends(get_current_user)
):
    history_entry = await user_history_service.create_user_history(history_data, str(current_user._id))
    if not history_entry:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user history entry")
    return history_entry

@router.get("/", response_model=List[UserHistoryRead], status_code=status.HTTP_200_OK)
async def get_user_history(current_user: UserDB = Depends(get_current_user), skip: int = 0, limit: int = 10):
    history = await user_history_service.get_user_history(str(current_user._id), skip, limit)
    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user history found")
    return history

@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_user_history(current_user: UserDB = Depends(get_current_user)):
    success = await user_history_service.delete_user_history(str(current_user._id))
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user history")
    return {"message": "User history deleted successfully"}

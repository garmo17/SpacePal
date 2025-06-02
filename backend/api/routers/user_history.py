from fastapi import APIRouter, status, HTTPException, Depends, Response, Request
import json
from backend.api.dependencies.auth import get_current_user
from backend.api.schemas.user_history import UserHistoryCreate, UserHistoryRead
from backend.api.services import user_history as user_history_service
from typing import List
from backend.api.models.users import UserDB
from fastapi import Response

router = APIRouter(prefix="/user_history", tags=["user_history"])

@router.get("/", response_model=List[UserHistoryRead], status_code=status.HTTP_200_OK)
async def get_user_histories(request: Request, response: Response, current_user: UserDB = Depends(get_current_user)):
    range_param = request.query_params.get('range')
    if range_param:
        range_values = json.loads(range_param)
        skip = range_values[0]
        limit = range_values[1] - range_values[0] + 1
    else:
        skip = 0
        limit = 10

    if current_user.username == "admin":
        history, total = await user_history_service.get_all_user_histories(skip, limit)
        response.headers["Content-Range"] = f"0-{skip + len(history) - 1}/{total}"
        return history
    else:
        history = await user_history_service.get_user_history(str(current_user._id), skip, limit)
        response.headers["Content-Range"] = f"0-{skip + len(history) - 1}/{len(history)}"
        return history


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

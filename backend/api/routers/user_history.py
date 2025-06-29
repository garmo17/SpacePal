from fastapi import APIRouter, status, HTTPException, Depends, Response, Request
import json
from backend.api.dependencies.auth import get_current_user
from backend.api.dependencies.auth import is_admin
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
        if not history:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user history found")
        response.headers["Content-Range"] = f"0-{skip + len(history) - 1}/{total}"
        return history
    else:
        history = await user_history_service.get_user_history(str(current_user._id), skip, limit)
        if not history:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user history found")
        response.headers["Content-Range"] = f"0-{skip + len(history) - 1}/{len(history)}"
        return history


@router.post("/", response_model=UserHistoryRead, status_code=status.HTTP_201_CREATED)
async def create_user_history(user_history: UserHistoryCreate, current_user: UserDB = Depends(get_current_user)):
    created_history = await user_history_service.create_user_history(user_history, str(current_user._id))
    if not created_history:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user history")
    return created_history

@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_history_by_id(history_id: str, current_user: UserDB = Depends(is_admin)):
    if not history_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="History ID is required")
    
    result = await user_history_service.delete_user_history_by_id(history_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User history not found")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_user_history(current_user: UserDB = Depends(is_admin)):
    success = await user_history_service.delete_user_history()
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user history")
    return {"message": "User history deleted successfully"}

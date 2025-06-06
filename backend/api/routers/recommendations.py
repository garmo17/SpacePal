from fastapi import APIRouter, status, Depends, Query
from typing import Optional, List

from backend.api.services.auth_service import get_optional_user
from backend.api.services.recommendation_service import get_personalized
from backend.api.models.users import UserDB
from backend.api.schemas.products import ProductRead

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/user", response_model=List[ProductRead], status_code=status.HTTP_200_OK)
async def personalized_recommendations(
    space: str,
    style: str,
    limit: int = 10,
    offset: int = 0,
    categories: Optional[List[str]] = Query(default=None),
    current_user: Optional[UserDB] = Depends(get_optional_user)
):
    return await get_personalized(space, style, current_user, limit, offset, categories)


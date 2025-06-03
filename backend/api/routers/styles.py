from fastapi import APIRouter, status, HTTPException, Depends, Response, Request
import json
from backend.api.dependencies.auth import is_admin
from backend.api.services import styles as styles_service
from backend.api.schemas.styles import *
from typing import List


router = APIRouter(prefix="/styles", tags=["styles"])

@router.get("/", response_model=List[StyleRead], status_code=status.HTTP_200_OK)
async def get_styles(request: Request, response: Response):
    range_param = request.query_params.get('range')
    if range_param:
        range_values = json.loads(range_param)
        skip = range_values[0]
        limit = range_values[1] - range_values[0] + 1
    else:
        skip = 0
        limit = 10

    styles, total = await styles_service.list_styles(skip, limit)
    if not styles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No styles found")
    response.headers["Content-Range"] = f"0-{skip + len(styles) - 1}/{total}"
    return styles

@router.get("/{id}", response_model=StyleRead, status_code=status.HTTP_200_OK)
async def get_style(id: str):
    style = await styles_service.get_style(id)  
    if not style:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Style not found")
    return style

@router.post("/", response_model=StyleRead, status_code=status.HTTP_201_CREATED)
async def create_style(style_data: StyleCreate, current_user: str = Depends(is_admin)):
    created_style = await styles_service.create_style(style_data)  
    if not created_style:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Style already exists")
    return created_style

@router.post("/bulk", response_model=StylesBulkResponse, status_code=status.HTTP_201_CREATED)
async def create_styles(styles_data: List[StyleCreate], current_user: str = Depends(is_admin)):
    results = await styles_service.create_styles(styles_data)  
    if not results.get("created"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="All styles already exist")
    return results

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_style(id: str, current_user: str = Depends(is_admin)):
    success = await styles_service.delete_style(id)  
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Style not found")
    return {"message": "Style deleted successfully"}

@router.put("/{id}", response_model=StyleRead, status_code=status.HTTP_200_OK)
async def update_style(id: str, style_data: StyleUpdate, current_user: str = Depends(is_admin)):
    updated_style = await styles_service.update_style(id, style_data)  
    if not updated_style:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Style not found")
    return updated_style
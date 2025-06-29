from fastapi import APIRouter, status, HTTPException, Depends, Response, Request
from backend.api.dependencies.auth import is_admin
from backend.api.services import spaces as spaces_service
from backend.api.schemas.spaces import *
from typing import List
import json


router = APIRouter(prefix="/spaces", tags=["spaces"])

@router.get("/", response_model=List[SpaceRead], status_code=status.HTTP_200_OK)
async def get_spaces(request: Request, response: Response):
    range_param = request.query_params.get('range')
    if range_param:
        range_values = json.loads(range_param)
        skip = range_values[0]
        limit = range_values[1] - range_values[0] + 1
    else:
        skip = 0
        limit = 10

    spaces, total = await spaces_service.list_spaces(skip, limit)
    if not spaces:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No spaces found")
    response.headers["Content-Range"] = f"0-{skip + len(spaces) - 1}/{total}"
    return spaces

@router.get("/{id}", response_model=SpaceRead, status_code=status.HTTP_200_OK)
async def get_space(id: str):
    space = await spaces_service.get_space(id)  
    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")
    return space

@router.post("/", response_model=SpaceRead, status_code=status.HTTP_201_CREATED)
async def create_space(space_data: SpaceCreate, current_user: str = Depends(is_admin)):
    created_space = await spaces_service.create_space(space_data)  
    if not created_space:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Space already exists")
    return created_space

@router.post("/bulk", response_model=SpacesBulkResponse, status_code=status.HTTP_201_CREATED)
async def create_spaces(spaces_data: List[SpaceCreate], current_user: str = Depends(is_admin)):
    results = await spaces_service.create_spaces(spaces_data)  
    if not results.get("created"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="All spaces already exist")
    return results

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_space(id: str, current_user: str = Depends(is_admin)):
    success = await spaces_service.delete_space(id)  
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")
    return {"message": "Space deleted successfully"}

@router.put("/{id}", response_model=SpaceRead, status_code=status.HTTP_200_OK)
async def update_space(id: str, space_data: SpaceUpdate, current_user: str = Depends(is_admin)):
    updated_space = await spaces_service.update_space(id, space_data)  
    if not updated_space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")
    return updated_space
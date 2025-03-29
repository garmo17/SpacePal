from fastapi import APIRouter, status, HTTPException, Depends
from backend.api.dependencies.auth import is_admin
from backend.api.services import spaces as spaces_service
from backend.api.schemas.spaces import SpaceRead, SpaceCreate, SpaceUpdate

router = APIRouter(prefix="/spaces", tags=["spaces"])

@router.get("/", response_model=list[SpaceRead], status_code=status.HTTP_200_OK)
async def get_spaces(skip: int = 0, limit: int = 10):
    spaces = await spaces_service.list_spaces(skip, limit)  
    if not spaces:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No spaces found")
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
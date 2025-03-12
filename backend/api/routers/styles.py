from fastapi import APIRouter, status, HTTPException
from services import styles as styles_service
from schemas.styles import Style

router = APIRouter(prefix="/styles", tags=["styles"])

@router.get("/", response_model=list[Style], status_code=status.HTTP_200_OK)
async def get_styles(skip: int = 0, limit: int = 10):
    styles = await styles_service.list_styles(skip, limit)  
    if not styles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No styles found")
    return styles

@router.get("/{id}", response_model=Style, status_code=status.HTTP_200_OK)
async def get_style(id: int):
    style = await styles_service.get_style(id)  
    if not style:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Style not found")
    return style

@router.post("/", response_model=Style, status_code=status.HTTP_201_CREATED)
async def create_style(style_data: Style):
    created_style = await styles_service.create_style(style_data)  
    if not created_style:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Style already exists")
    return created_style

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_style(id: int):
    success = await styles_service.delete_style(id)  
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Style not found")
    return {"message": "Style deleted successfully"}

@router.put("/{id}", response_model=Style, status_code=status.HTTP_200_OK)
async def update_style(id: int, style_data: Style):
    updated_style = await styles_service.update_style(id, style_data)  
    if not updated_style:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Style not found")
    return updated_style
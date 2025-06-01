from fastapi import APIRouter, status, HTTPException
from backend.api.services import users as users_service
from backend.api.schemas.users import *
from backend.api.models.users import *
from backend.api.services.auth_service import get_current_user
from fastapi import Depends
from backend.api.dependencies.auth import is_admin
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserRead], status_code=status.HTTP_200_OK)
async def get_users(skip: int = 0, limit: int = 10, current_user: UserDB = Depends(is_admin)):
    users = await users_service.list_users(skip, limit)  
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    return users


@router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def read_users_me(current_user: UserDB = Depends(get_current_user)):
    print(f"Current user: {current_user.username}, {current_user.email}, {current_user._id}")
    return UserRead(username=current_user.username, email=current_user.email, id=str(current_user._id))

@router.get("/{id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user(id: str, current_user: UserDB = Depends(is_admin)):
    user = await users_service.get_user(id)  
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    created_user = await users_service.create_user(user_data)  
    if not created_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    return created_user

@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_all_users(current_user: UserDB = Depends(is_admin)):
    deleted_count = await users_service.delete_all_users()  
    if deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found to delete")
    return {"message": f"Deleted {deleted_count} users"}

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_user(id: str, current_user: UserDB = Depends(is_admin)):
    success = await users_service.delete_user(id)  
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User deleted successfully"}

@router.put("/{id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user(id: str, user_data: UserUpdate, current_user: UserDB = Depends(get_current_user)):
    if str(current_user._id) != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own user")
    updated_user = await users_service.update_user(id, user_data)  
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user

@router.get("/me/likes", response_model=List[ProductIdPayload], status_code=status.HTTP_200_OK)
async def get_liked_products(current_user: UserDB = Depends(get_current_user)):
    liked_products = await users_service.get_liked_products(str(current_user._id))
    if liked_products is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return [{"product_id": p} for p in liked_products]

@router.post("/me/likes", status_code=status.HTTP_200_OK)
async def add_liked_product(payload: ProductIdPayload, current_user: UserDB = Depends(get_current_user)):
    product_id = payload.product_id
    if not product_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product ID is required")
    result = await users_service.add_liked_product(str(current_user._id), product_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not result:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El producto ya está en favoritos")
    return {"message": "Producto añadido a favoritos"}

@router.delete("/me/likes/{product_id}", status_code=status.HTTP_200_OK)
async def remove_liked_product(product_id: str, current_user: UserDB = Depends(get_current_user)):
    if not product_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product ID is required")
    result = await users_service.remove_liked_product(str(current_user._id), product_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El producto no está en favoritos")
    return {"message": "Producto eliminado de favoritos"}

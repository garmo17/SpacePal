from fastapi import APIRouter, status, HTTPException, Response, Depends, Request
import json
from backend.api.services import users as users_service
from backend.api.schemas.users import *
from backend.api.models.users import  UserDB
from backend.api.schemas.users import CartItem, CartItemPayload
from backend.api.services.auth_service import get_current_user
from backend.api.dependencies.auth import is_admin
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserRead], status_code=status.HTTP_200_OK)
async def get_users(request: Request, response: Response, current_user: UserDB = Depends(is_admin)):
    range_param = request.query_params.get('range')
    if range_param:
        range_values = json.loads(range_param)
        skip = range_values[0]
        limit = range_values[1] - range_values[0] + 1
    else:
        skip = 0
        limit = 10

    users, total = await users_service.list_users(skip=skip, limit=limit)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    response.headers["Content-Range"] = f"0-{skip + len(users) - 1}/{total}"
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
    if str(current_user._id) != id and current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own user"
        )
    updated_user = await users_service.update_user(id, user_data)  
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user

@router.get("/me/cart", response_model=List[CartItem], status_code=status.HTTP_200_OK)
async def get_cart_products(current_user: UserDB = Depends(get_current_user)):
    cart_products = await users_service.get_cart_products(str(current_user._id))
    if cart_products is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return cart_products

@router.post("/me/cart", status_code=status.HTTP_200_OK)
async def add_cart_product(payload: CartItemPayload, current_user: UserDB = Depends(get_current_user)):
    if not payload.product_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product ID is required")
    
    result = await users_service.add_cart_product(
        str(current_user._id),
        payload.product_id,
        payload.quantity
    )
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if result is False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return {"message": "Producto añadido al carrito"}

@router.patch("/me/cart/{product_id}", status_code=status.HTTP_200_OK)
async def update_cart_product_quantity(
    product_id: str,
    payload: QuantityPayload,
    current_user: UserDB = Depends(get_current_user)
):
    if not product_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product ID is required")
    
    result = await users_service.update_product_quantity(
        str(current_user._id),
        product_id,
        payload.quantity
    )
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no está en el carrito")
    return {"message": "Cantidad actualizada correctamente"}

@router.delete("/me/cart/clear", status_code=status.HTTP_200_OK)
async def clear_cart(current_user: UserDB = Depends(get_current_user)):
    result = await users_service.clear_cart(str(current_user._id))
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "Carrito vaciado correctamente"}


@router.delete("/me/cart/{product_id}", status_code=status.HTTP_200_OK)
async def remove_cart_product(product_id: str, current_user: UserDB = Depends(get_current_user)):
    if not product_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product ID is required")
    result = await users_service.remove_cart_product(str(current_user._id), product_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El producto no está en el carrito")
    return {"message": "Producto eliminado del carrito"}
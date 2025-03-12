from fastapi import APIRouter, status, HTTPException
from services import users as users_service
from schemas.users import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[User], status_code=status.HTTP_200_OK)
async def get_users(skip: int = 0, limit: int = 10):
    users = await users_service.list_users(skip, limit)  
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")
    return users

@router.get("/{id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user(id: int):
    user = await users_service.get_user(id)  
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: User):
    created_user = await users_service.create_user(user_data)  
    if not created_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    return created_user

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_user(id: int):
    success = await users_service.delete_user(id)  
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User deleted successfully"}

@router.put("/{id}", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(id: int, user_data: User):
    updated_user = await users_service.update_user(id, user_data)  
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


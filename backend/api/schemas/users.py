from pydantic import BaseModel, EmailStr
from typing import Optional, List, Type, TypeVar

class CartItem(BaseModel):
    product_id: str
    quantity: int

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: str
    cart_products: Optional[List[CartItem]] = []

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    cart_products: Optional[List[CartItem]] = None

class ProductIdPayload(BaseModel):
    product_id: str

class CartItemPayload(BaseModel):
    product_id: str
    quantity: int

class QuantityPayload(BaseModel):
    quantity: int

T = TypeVar("T", bound=BaseModel)
    
def from_mongo(document: dict, model: Type[T]) -> T:
    if not document:
        return None 
    if "_id" in document:
        document["id"] = str(document["_id"]) 
        del document["_id"]  
    return model(**document)

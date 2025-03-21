from pydantic import BaseModel, EmailStr
from typing import Optional, Type, TypeVar

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str



class UserRead(UserBase):
    id: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None



T = TypeVar("T", bound=BaseModel)
    
def from_mongo(document: dict, model: Type[T]) -> T:
    if not document:
        return None 
    if "_id" in document:
        document["id"] = str(document["_id"]) 
        del document["_id"]  
    return model(**document)  
    
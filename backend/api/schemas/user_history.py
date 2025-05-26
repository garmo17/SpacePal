from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime
from typing import Type, TypeVar

class UserHistoryBase(BaseModel):
    product_id: str
    action: Literal["click", "like"] = "click"

class UserHistoryCreate(UserHistoryBase):
    pass

class UserHistoryRead(UserHistoryBase):
    id: str
    user_id: str
    timestamp: datetime
    
T = TypeVar("T", bound=BaseModel)

def from_mongo(document: dict, model: Type[T]) -> T:
    if not document:
        return None
    if "_id" in document:
        document["id"] = str(document["_id"])
        del document["_id"]
    return model(**document)

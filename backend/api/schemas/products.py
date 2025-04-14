from pydantic import BaseModel, HttpUrl
from typing import Optional, Type, TypeVar


class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    purchase_link: HttpUrl
    image_url: HttpUrl
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass
    

class ProductRead(ProductBase):
    id: str

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    purchase_link: Optional[HttpUrl] = None
    image_url: Optional[HttpUrl] = None
    category: Optional[str] = None

T = TypeVar("T", bound=BaseModel)

def from_mongo(document: dict, model: Type[T]) -> T:
    if not document:
        return None
    if "_id" in document:
        document["id"] = str(document["_id"])
        del document["_id"]
    return model(**document)
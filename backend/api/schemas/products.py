from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional, Type, TypeVar, List
from uuid import uuid4


class ProductReview(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    username: str
    rating: float
    comment: Optional[str] = None
    timestamp: Optional[datetime] = None

class ProductReviewCreate(BaseModel):
    rating: float
    comment: Optional[str] = None

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    purchase_link: HttpUrl
    image_url: HttpUrl
    category: Optional[str] = None
    spaces: Optional[List[str]] = []
    styles: Optional[List[str]] = []
    rating: Optional[float] = 0.0
    review_count: Optional[int] = 0
    reviews: Optional[List[ProductReview]] = []

class ProductCreate(ProductBase):
    pass
    

class ProductRead(ProductBase):
    id: str

class ProductsBulkResponse(BaseModel):
    created: List[ProductRead]
    existing: List[ProductRead]

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    purchase_link: Optional[HttpUrl] = None
    image_url: Optional[HttpUrl] = None
    category: Optional[str] = None
    spaces: Optional[List[str]] = None
    styles: Optional[List[str]] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    reviews: Optional[List[ProductReview]] = None


T = TypeVar("T", bound=BaseModel)

def from_mongo(document: dict, model: Type[T]) -> T:
    if not document:
        return None
    if "_id" in document:
        document["id"] = str(document["_id"])
        del document["_id"]
    return model(**document)
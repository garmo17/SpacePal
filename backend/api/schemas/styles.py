from pydantic import BaseModel, HttpUrl
from typing import Optional, Type, TypeVar

class StyleBase(BaseModel):
    name: str
    description: str
    image: HttpUrl

class StyleCreate(StyleBase):
    pass

class StyleRead(StyleBase):
    id: str

class StyleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[HttpUrl] = None

T = TypeVar("T", bound=BaseModel)

def from_mongo(document: dict, model: Type[T]) -> T:
    if not document:
        return None
    if "_id" in document:
        document["id"] = str(document["_id"])
        del document["_id"]
    return model(**document)



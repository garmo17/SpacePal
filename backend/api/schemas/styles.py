from pydantic import BaseModel

class Style(BaseModel):
    id: int
    name: str
    description: str
    image: str



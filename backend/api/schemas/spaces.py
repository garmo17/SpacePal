from pydantic import BaseModel

class Space(BaseModel):
    id: int
    name: str
    description: str
    image: str

from bson import ObjectId
from pydantic import EmailStr
from typing import List
from typing import Optional

class UserDB:
    def __init__(
        self,
        username: str,
        email: EmailStr,
        password: str,
        liked_products: Optional[List[str]] = None,
        _id: ObjectId = None
    ):
        self._id = _id or ObjectId()
        self.username = username
        self.email = str(email)
        self.password = password
        self.liked_products = liked_products or []

    def to_dict(self):
        return {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'liked_products': self.liked_products
        }

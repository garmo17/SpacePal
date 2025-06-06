from bson import ObjectId
from pydantic import EmailStr
from typing import List, Optional

class CartItem:
    def __init__(self, product_id: str, quantity: int = 1):
        self.product_id = product_id
        self.quantity = quantity

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "quantity": self.quantity
        }

class UserDB:
    def __init__(
        self,
        username: str,
        email: EmailStr,
        password: str,
        cart_products: Optional[List[CartItem]] = None,
        _id: ObjectId = None
    ):
        self._id = _id or ObjectId()
        self.username = username
        self.email = str(email)
        self.password = password
        self.cart_products = cart_products or []

    def to_dict(self):
        return {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'cart_products': [item.to_dict() for item in self.cart_products]
        }

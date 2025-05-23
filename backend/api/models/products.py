from bson import ObjectId
from pydantic.networks import HttpUrl
from typing import List

class ProductDB:
    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        purchase_link: HttpUrl,
        image_url: HttpUrl,
        category: str,
        _id: ObjectId = None,
        spaces: List[str] = None,
        styles: List[str] = None,
        reviews: List[dict] = None,
        rating: float = 0.0,
        review_count: int = 0
    ):
        self._id = _id or ObjectId()
        self.name = name
        self.description = description
        self.price = price
        self.purchase_link = str(purchase_link)
        self.image_url = str(image_url)
        self.category = category
        self.spaces = spaces or []
        self.styles = styles or []
        self.reviews = reviews or []
        self.rating = rating
        self.review_count = review_count

    def to_dict(self):
        return {
            "_id": self._id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "purchase_link": self.purchase_link,
            "image_url": self.image_url,
            "category": self.category,
            "spaces": self.spaces,
            "styles": self.styles,
            "reviews": self.reviews,
            "rating": self.rating,
            "review_count": self.review_count
        }

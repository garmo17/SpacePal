from bson import ObjectId

class ProductDB:
    def __init__(self, name: str, description: str, price: float, purchase_link: str, image_url: str, category: str, _id: ObjectId = None):
        self._id = _id or ObjectId()  
        self.name = name
        self.description = description
        self.price = price
        self.purchase_link = purchase_link
        self.image_url = image_url
        self.category = category
        
    def to_dict(self):
        
        return {
            '_id': self._id,  
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'purchase_link': self.purchase_link,
            'image_url': self.image_url,
            'category': self.category
        }
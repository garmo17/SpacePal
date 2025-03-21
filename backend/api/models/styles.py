from bson import ObjectId
from pydantic.networks import HttpUrl

class StyleDB:
    def __init__(self, name: str, description: str, image: HttpUrl, _id: ObjectId = None):
        self._id = _id or ObjectId()  
        self.name = name
        self.description = description
        self.image = str(image)
        
    def to_dict(self):
        
        return {
            '_id': self._id,  
            'name': self.name,
            'description': self.description,
            'image': self.image
        }
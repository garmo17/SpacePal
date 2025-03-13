from bson import ObjectId

class SpaceDB:
    def __init__(self, name: str, description: str, image: str, _id: ObjectId = None):
        self._id = _id or ObjectId()  
        self.name = name
        self.description = description
        self.image = image
        
    def to_dict(self):
        
        return {
            '_id': self._id,  
            'name': self.name,
            'description': self.description,
            'image': self.image
        }
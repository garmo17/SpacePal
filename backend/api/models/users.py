from bson import ObjectId

class UserDB:
    def __init__(self, name: str, surname: str, email: str, _id: ObjectId = None):
        self._id = _id or ObjectId()  
        self.name = name
        self.surname = surname
        self.email = email
        
    def to_dict(self):
        
        return {
            '_id': self._id,  
            'name': self.name,
            'surname': self.surname,
            'email': self.email
        }

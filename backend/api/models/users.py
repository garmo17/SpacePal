from bson import ObjectId
from pydantic import EmailStr

class UserDB:
    def __init__(self, username: str, email: EmailStr, password: str, _id: ObjectId = None):
        self._id = _id or ObjectId()
        self.username = username
        self.email = str(email)
        self.password = password  

    def to_dict(self):
        return {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'password': self.password  
        }


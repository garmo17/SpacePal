from bson import ObjectId
from datetime import datetime, timezone

class UserHistoryDB:
    def __init__(
        self,
        user_id: str,
        product_id: str,
        action: str = "click",
        timestamp: datetime = None,
        _id: ObjectId = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.product_id = product_id
        self.action = action
        self.timestamp = timestamp or datetime.now(timezone.utc)
        
    def to_dict(self):
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "action": self.action,
            "timestamp": self.timestamp
        }

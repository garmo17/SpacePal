from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URI, DB_NAME

client = AsyncIOMotorClient(MONGO_URI)

database = client[DB_NAME]

users_collection = database.get_collection("users")
products_collection = database.get_collection("products")
spaces_collection = database.get_collection("spaces")
styles_collection = database.get_collection("styles")



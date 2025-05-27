from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client.registeruser
session_collection = db["session_id"]
session_title_collection = db["session_chat"]
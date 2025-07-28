from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client["matri"]
users = db["users"]
profiles = db["profiles"]
pre_profiles = db["pre_profiles"]  # For pre-registration profiles
masters = db["masters"]            # ⬅️ Add this line for Master Data

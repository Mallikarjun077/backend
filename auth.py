from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from database import users, profiles
from schemas import UserRegister, UserLogin, TokenResponse, PreProfile
from config import settings
from bson import ObjectId
from database import db  # ✅ Import this


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_token(user_id: str):
    expire = datetime.utcnow() + timedelta(hours=6)
    to_encode = {"sub": user_id, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

@router.post("/pre-profile/")
async def create_pre_profile(data: PreProfile):
    pre_data = data.dict()

    # Optional: rename `image_base64` to `image_path` for consistency
    if pre_data.get("image_base64"):
        print("✅ Received base64 image")
        pre_data["image_path"] = pre_data.pop("image_base64")

    pre_data["created_at"] = datetime.utcnow()

    result = await db["pre_profiles"].insert_one(pre_data)
    print("📦 Saved pre-profile:", pre_data)

    return {"pre_profile_id": str(result.inserted_id)}



# ✅ 2. Register user and link profile
@router.post("/register/")
async def register(data: UserRegister, pre_profile_id: str = None):
    if await users.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = pwd_context.hash(data.password)
    user = {"username": data.username, "email": data.email, "password": hashed}
    result = await users.insert_one(user)
    user_id = str(result.inserted_id)

    # ✅ Link pre-profile to user
    if pre_profile_id:
        await profiles.update_one(
            {"_id": ObjectId(pre_profile_id)},
            {"$set": {"user_id": user_id}}
        )

    return {"message": "User created", "user_id": user_id}

# ✅ 3. Login and return token
@router.post("/login/", response_model=TokenResponse)
async def login(data: UserLogin):
    user = await users.find_one({"email": data.email})
    if not user or not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(str(user["_id"]))
    return {"access": token}

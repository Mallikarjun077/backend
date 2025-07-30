from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from database import db, users
from schemas import UserRegister, UserLogin, TokenResponse, PreProfile, RegisterWithProfile
from config import settings
from bson import ObjectId
from fastapi.encoders import jsonable_encoder

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login/")

def create_token(user_id: str):
    expire = datetime.utcnow() + timedelta(hours=6)
    to_encode = {"sub": user_id, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ✅ Combined Register + Profile + Token
@router.post("/register_with_profile/", response_model=TokenResponse)
async def register_with_profile(data: RegisterWithProfile):
    # Check email
    if await users.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed = pwd_context.hash(data.password)
    user_doc = {
        "username": data.username,
        "email": data.email,
        "password": hashed
    }
    user_result = await users.insert_one(user_doc)
    user_id = str(user_result.inserted_id)

    # Create profile
    profile_data = data.pre_profile.dict()
    profile_data["user_id"] = user_id
    profile_data["created_at"] = datetime.utcnow()
    await db["pre_profiles"].insert_one(profile_data)

    token = create_token(user_id)
    return {"access": token}

# 🔐 Login
@router.post("/login/", response_model=TokenResponse)
async def login(data: UserLogin):
    user = await users.find_one({"email": data.email})
    if not user or not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(str(user["_id"]))
    return {"access": token}

# 🔎 Get Profile for Logged-in User
@router.get("/pre-profile/me")
async def get_my_pre_profile(user=Depends(get_current_user)):
    profile = await db["pre_profiles"].find_one({"user_id": str(user["_id"])})
    if not profile:
        raise HTTPException(status_code=404, detail="Pre-profile not found")
    profile["_id"] = str(profile["_id"])
    return profile

# --- Get All Pre-Profiles (excluding current user) ---

@router.get("/pre-profiles/all")
async def get_all_pre_profiles(user=Depends(get_current_user)):
    current_user_id = str(user["_id"])

    # Fetch all pre-profiles except the current user's
    cursor = db["pre_profiles"].find({"user_id": {"$ne": current_user_id}})
    pre_profiles = []

    async for profile in cursor:
        profile["_id"] = str(profile["_id"])
        pre_profiles.append(jsonable_encoder(profile))

    return pre_profiles


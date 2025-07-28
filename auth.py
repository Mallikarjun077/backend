from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from database import db, users
from schemas import UserRegister, UserLogin, TokenResponse, PreProfile
from config import settings
from bson import ObjectId

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login/")  # Important: Must match route

def create_token(user_id: str):
    expire = datetime.utcnow() + timedelta(hours=6)
    to_encode = {"sub": user_id, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/pre-profile/")
async def create_pre_profile(data: PreProfile, token: str = Depends(oauth2_scheme)):
    pre_data = data.dict()
    pre_data["created_at"] = datetime.utcnow()

    # Optional: attach user_id if token is present
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id:
            pre_data["user_id"] = user_id
    except JWTError:
        pass  # Token not required to create pre-profile

    result = await db["pre_profiles"].insert_one(pre_data)
    return {"pre_profile_id": str(result.inserted_id)}



@router.post("/register/")
async def register(data: UserRegister, pre_profile_id: str = None):
    if await users.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(data.password)
    user = {"username": data.username, "email": data.email, "password": hashed}
    result = await users.insert_one(user)
    user_id = str(result.inserted_id)

    if pre_profile_id:
        await db["pre_profiles"].update_one(
            {"_id": ObjectId(pre_profile_id)},
            {"$set": {"user_id": user_id}}
        )

    return {"message": "User created", "user_id": user_id}

@router.post("/login/", response_model=TokenResponse)
async def login(data: UserLogin):
    user = await users.find_one({"email": data.email})
    if not user or not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(str(user["_id"]))
    return {"access": token}

@router.get("/pre-profile/me")
async def get_my_pre_profile(user=Depends(get_current_user)):
    pre_profile = await db["pre_profiles"].find_one({"user_id": str(user["_id"])})
    if not pre_profile:
        raise HTTPException(status_code=404, detail="Pre-profile not found")
    pre_profile["_id"] = str(pre_profile["_id"])
    return pre_profile

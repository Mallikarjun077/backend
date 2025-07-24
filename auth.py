from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from database import users, profiles
from schemas import UserRegister, UserLogin, TokenResponse
from config import settings
from bson import ObjectId

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def create_token(user_id: str):
    expire = datetime.utcnow() + timedelta(hours=6)
    to_encode = {"sub": user_id, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

@router.post("/register/")
async def register(data: UserRegister):
    # Check if user already exists
    existing = await users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    # Save user
    hashed_pwd = hash_password(data.password)
    user_doc = {
        "email": data.email,
        "username": data.username,
        "password": hashed_pwd
    }
    result = await users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    # Save profile
    profile_doc = {
        "user_id": user_id,
        "name": data.name,
        "surname": data.surname,
        "age": data.age,
        "gender": data.gender,
        "phone": data.phone,
        "religion": data.religion,
        "caste": data.caste,
        "education": data.education,
        "job": data.job,
        "image_path": data.image_base64 or ""
    }
    await profiles.insert_one(profile_doc)

    # Token
    access_token = create_token(user_id)
    return {"access": access_token, "msg": "Successfully registered"}

@router.post("/login/", response_model=TokenResponse)
async def login(data: UserLogin):
    user = await users.find_one({"email": data.email})
    if not user or not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(str(user["_id"]))
    return {"access": token}

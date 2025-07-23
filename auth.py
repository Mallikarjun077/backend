from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from database import users
from schemas import UserRegister, UserLogin, TokenResponse
from config import settings
from bson import ObjectId

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- JWT Creation ---
def create_token(user_id: str):
    expire = datetime.utcnow() + timedelta(hours=6)
    to_encode = {"sub": user_id, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

# --- Register with Token ---
@router.post("/register/", response_model=TokenResponse)
async def register(data: UserRegister):
    if await users.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = pwd_context.hash(data.password)
    user = {"username": data.username, "email": data.email, "password": hashed}
    result = await users.insert_one(user)

    user_id = str(result.inserted_id)
    token = create_token(user_id)

    return {"access": token}  # 🔐 Token sent on successful registration

# --- Login with Token ---
@router.post("/login/", response_model=TokenResponse)
async def login(data: UserLogin):
    user = await users.find_one({"email": data.email})
    if not user or not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(str(user["_id"]))
    return {"access": token}

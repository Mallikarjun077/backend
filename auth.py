from fastapi import APIRouter, HTTPException, status, Depends
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database import users
from schemas import UserRegister, UserLogin, TokenResponse
from config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# 🔑 Create token
def create_token(user_email: str):
    expire = datetime.utcnow() + timedelta(days=1)
    payload = {"sub": user_email, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

# ✅ Verify token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ✅ Get current user (used for protected routes)
def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    email = verify_token(token.credentials)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    return email

# 🔐 Register
@router.post("/register/", response_model=TokenResponse)
async def register(data: UserRegister):
    existing_user = await users.find_one({"email": data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(data.password)
    user_data = {
        "email": data.email,
        "username": data.username,
        "password": hashed_password,
    }
    await users.insert_one(user_data)

    token = create_token(data.email)
    return {"access": token, "email": data.email}

# 🔐 Login
@router.post("/login/", response_model=TokenResponse)
async def login(data: UserLogin):
    user = await users.find_one({"email": data.email})
    if not user or not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(data.email)
    return {"access": token, "email": data.email}

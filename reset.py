from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from email_utils import send_otp, otp_store
from database import users
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class EmailRequest(BaseModel):
    email: EmailStr

class ResetRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

@router.post("/password-reset/")
async def request_reset(data: EmailRequest):
    user = await users.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the name from the database
    name = user.get("username", "User")  

    # Send OTP with the user's name
    await send_otp(data.email, name)
    return {"message": "OTP sent to email"}


@router.post("/password-reset/confirm/")
async def reset_password(data: ResetRequest):
    stored_otp = otp_store.get(data.email)
    if not stored_otp or stored_otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    hashed_password = pwd_context.hash(data.new_password)
    await users.update_one({"email": data.email}, {"$set": {"password": hashed_password}})
    otp_store.pop(data.email, None)
    return {"message": "Password updated"}

from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    name: str
    surname: str
    age: int
    gender: str
    phone: str
    religion: str
    caste: str
    education: str
    job: str
    image_base64: Optional[str]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access: str

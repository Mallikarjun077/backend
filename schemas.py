from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access: str
    email: EmailStr

class Profile(BaseModel):
    # user_id: str
    name: Optional[str] = None
    surname: Optional[str] = None
    age: Optional[str] = None
    height: Optional[str] = None
    motherTongue:Optional[str] = None
    maritalStatus: Optional[str] = None
    eatingHabits: Optional[str] = None
    religion: Optional[str] = None
    community: Optional[str] = None
    subCaste: Optional[str] = None
    gothra: Optional[str] = None
    dosha: Optional[str] = None
    star: Optional[str] = None
    rassi: Optional[str] = None
    horoscope: Optional[str] = None
    profession: Optional[str] = None
    qualification: Optional[str] = None
    jobSector: Optional[str] = None
    income: Optional[str] = None
    familyStatus: Optional[str] = None
    familyType: Optional[str] = None
    fatherOccupation: Optional[str] = None
    motherOccupation: Optional[str] = None
    brothers: Optional[str] = None
    sisters: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    ancestralOrigin: Optional[str] = None
    mobile: Optional[str] = None
    socialMedia: Optional[str] = None
    about: Optional[str] = None
    image_base64: Optional[str] = None


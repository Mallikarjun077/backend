from pydantic import BaseModel, EmailStr
from typing import Optional,List



class PreProfile(BaseModel):
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
    liked_profiles: Optional[List[str]] = []  # user_ids this user liked
    liked_by: Optional[List[str]] = [] 
       # user_ids who liked this user




class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access: str

class LikeRequest(BaseModel):
    liked_user_id: str    

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
         # user_ids who liked this user


class MasterData(BaseModel):
    type: str                  
    values: List[str] 

class RegisterWithProfile(BaseModel):
    username: str
    email: EmailStr
    password: str
    pre_profile: PreProfile    
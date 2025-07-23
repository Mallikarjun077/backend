from fastapi import APIRouter, Depends, HTTPException, status
from schemas import Profile
from database import profiles
from config import settings
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

# --- JWT Decode & Extract Email ---
def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            token.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=403, detail="Token missing subject (email)")
        return email
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

@router.post("/profile/")
async def save_profile(data: Profile, user_email: str = Depends(get_current_user)):
    try:
        data_dict = data.dict()
        print("Received data:", data_dict)
        print("User email from token:", user_email)

        data_dict["email"] = user_email
        data_dict["user_id"] = user_email

        if data_dict.get("image_base64"):
            data_dict["image_path"] = data_dict.pop("image_base64")

        result = await profiles.update_one(
            {"email": user_email},
            {"$set": data_dict},
            upsert=True
        )

        print("MongoDB update result:", result)

        return {"message": "Profile saved successfully"}

    except Exception as e:
        print("Profile save error:", e)
        raise HTTPException(status_code=500, detail=f"Error saving profile: {str(e)}")


# --- Get Own Profile ---
@router.get("/profile/")
async def get_profile(user_email: str = Depends(get_current_user)):
    profile = await profiles.find_one({"user_id": user_email})
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found")

    profile["_id"] = str(profile["_id"])
    profile["image"] = profile.get("image_path", "")
    return profile

# --- Get All Other Users' Profiles ---
@router.get("/all-profiles/")
async def get_all_profiles(user_email: str = Depends(get_current_user)):
    cursor = profiles.find({"user_id": {"$ne": user_email}})
    all_profiles = []

    async for profile in cursor:
        profile["_id"] = str(profile["_id"])
        profile["image"] = profile.get("image_path", "")
        all_profiles.append(profile)

    return all_profiles

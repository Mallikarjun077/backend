from fastapi import APIRouter, Depends, HTTPException
from schemas import Profile
from database import profiles
from config import settings
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

# --- JWT Decode & Extract user_id ---
def get_current_user_id(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            token.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")  # sub should be user_id
        if not user_id:
            raise HTTPException(status_code=403, detail="Token missing subject (user_id)")
        return user_id
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

# --- Save or Update Profile ---
@router.post("/profile/")
async def save_profile(data: Profile, user_id: str = Depends(get_current_user_id)):
    try:
        data_dict = data.dict()
        print("Received data:", data_dict)
        print("User ID from token:", user_id)

        data_dict["user_id"] = user_id

        # Handle image field
        if data_dict.get("image_base64"):
            data_dict["image_path"] = data_dict.pop("image_base64")

        # Update or insert profile
        result = await profiles.update_one(
            {"user_id": user_id},
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
async def get_profile(user_id: str = Depends(get_current_user_id)):
    profile = await profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found")

    profile["_id"] = str(profile["_id"])
    profile["image"] = profile.get("image_path", "")
    return profile

# --- Get All Other Users' Profiles ---
@router.get("/all-profiles/")
async def get_all_profiles(user_id: str = Depends(get_current_user_id)):
    cursor = profiles.find({"user_id": {"$ne": user_id}})
    all_profiles = []

    async for profile in cursor:
        profile["_id"] = str(profile["_id"])
        profile["image"] = profile.get("image_path", "")
        all_profiles.append(profile)

    return all_profiles

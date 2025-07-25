from fastapi import APIRouter, Depends, HTTPException
from schemas import Profile
from database import profiles
from auth import settings
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schemas import LikeRequest
from email_utils import send_profile_liked_email

router = APIRouter()
security = HTTPBearer()

# --- Decode JWT ---
def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload  
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

# --- Save Profile (POST) ---
@router.post("/profile/")
async def save_profile(data: Profile, user=Depends(get_current_user)):
    try:
        user_id = str(user["sub"])
        data_dict = data.dict()
        data_dict["user_id"] = user_id

        if data_dict.get("image_base64"):
            print("✅ Received base64 image")
            data_dict["image_path"] = data_dict["image_base64"]
            data_dict.pop("image_base64", None)

        print("📦 Final data saving to DB:", data_dict)
        await profiles.update_one({"user_id": user_id}, {"$set": data_dict}, upsert=True)

        return {"message": "Profile saved successfully"}

    except Exception as e:
        print("❌ Error saving profile:", e)
        raise HTTPException(status_code=500, detail=str(e))


# --- Get Own Profile (GET) ---
@router.get("/profile/")
async def get_profile(user=Depends(get_current_user)):
    user_id = str(user["sub"])
    profile = await profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found")

    profile["_id"] = str(profile["_id"])
    profile["image"] = profile.get("image_path", "")  

    return profile


# --- Get All Other Profiles (GET) ---
@router.get("/all-profiles/")
async def get_all_profiles(user=Depends(get_current_user)):
    current_user_id = str(user["sub"])
    profiles_cursor = profiles.find({"user_id": {"$ne": current_user_id}})
    all_profiles = []

    async for profile in profiles_cursor:
        profile["_id"] = str(profile["_id"])
        profile["image"] = profile.get("image_path", "")  
        all_profiles.append(profile)

    return all_profiles

# --- Like a profile ---
@router.post("/like/")
async def like_profile(data: LikeRequest, user=Depends(get_current_user)):
    current_user_id = str(user["sub"])
    liker_profile = await profiles.find_one({"user_id": current_user_id})
    liked_profile = await profiles.find_one({"user_id": data.liked_user_id})

    if not liker_profile or not liked_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if data.liked_user_id == current_user_id:
        raise HTTPException(status_code=400, detail="You cannot like your own profile")

    # Check if already liked
    if data.liked_user_id in liker_profile.get("liked_profiles", []):
        raise HTTPException(status_code=400, detail="Already liked")

    # Update liker: add to liked_profiles
    await profiles.update_one(
        {"user_id": current_user_id},
        {"$addToSet": {"liked_profiles": data.liked_user_id}}
    )

    # Update liked user: add to liked_by
    await profiles.update_one(
        {"user_id": data.liked_user_id},
        {"$addToSet": {"liked_by": current_user_id}}
    )

    # Send notification email
    liked_user_email = liked_profile.get("email")
    liker_name = liker_profile.get("name", "Someone")

    if liked_user_email:
        await send_profile_liked_email(liked_user_email, liker_name)

    return {"message": f"You liked {liked_profile.get('name', 'this user')}"}

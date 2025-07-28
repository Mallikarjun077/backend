from fastapi import APIRouter, Depends, HTTPException
from schemas import Profile, PreProfile, LikeRequest,MasterData
from database import profiles, users, db
from auth import settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from email_utils import send_profile_liked_email

router = APIRouter()
security = HTTPBearer()

# --- Decode JWT Token ---
def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")


# --- Get Your Pre-Profile ---
@router.get("/pre-profile/me")
async def get_my_pre_profile(user=Depends(get_current_user)):
    user_id = str(user["sub"])
    profile = await db["pre_profiles"].find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Pre-profile not found")
    
    profile["_id"] = str(profile["_id"])
    return jsonable_encoder(profile)





# # --- Save Full Profile ---
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


# # --- Get Own Profile ---
@router.get("/profile/")
async def get_profile(user=Depends(get_current_user)):
    user_id = str(user["sub"])
    profile = await profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found")

    profile["_id"] = str(profile["_id"])
    profile["image"] = profile.get("image_path", "")
    return profile


# --- Get All Other Profiles ---
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


# --- Like a Profile ---
@router.post("/like/")
async def like_profile(data: LikeRequest, user=Depends(get_current_user)):
    current_user_id = str(user["sub"])

    # Get both profiles
    liker_profile = await profiles.find_one({"user_id": current_user_id})
    liked_profile = await profiles.find_one({"user_id": data.liked_user_id})

    if not liker_profile or not liked_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if data.liked_user_id == current_user_id:
        raise HTTPException(status_code=400, detail="You cannot like your own profile")

    if data.liked_user_id in liker_profile.get("liked_profiles", []):
        raise HTTPException(status_code=400, detail="Already liked")

    # Save like
    await profiles.update_one(
        {"user_id": current_user_id},
        {"$addToSet": {"liked_profiles": data.liked_user_id}}
    )
    await profiles.update_one(
        {"user_id": data.liked_user_id},
        {"$addToSet": {"liked_by": current_user_id}}
    )

    # Fetch liked user's email
    try:
        liked_user_id = liked_profile["user_id"]
        liked_user_doc = await users.find_one({"_id": ObjectId(liked_user_id)})
        liked_user_email = liked_user_doc.get("email") if liked_user_doc else None
    except Exception as e:
        print("❌ Failed to fetch liked user's email:", e)
        liked_user_email = None

    print("📨 Liked user email:", liked_user_email)

    liker_name = liker_profile.get("name", "Someone")

    if liked_user_email:
        await send_profile_liked_email(liked_user_email, liker_name)
    else:
        print("⚠️ Email not found for liked user")

    return {"message": f"You liked {liked_profile.get('name', 'this user')}"}

@router.post("/masters/", tags=["Masters"])
async def create_master(data: MasterData):
    existing = await db["masters"].find_one({"type": data.type})
    if existing:
        raise HTTPException(status_code=400, detail="Master type already exists")
    await db["masters"].insert_one(data.dict())
    return {"message": "Master created"}

@router.get("/masters/{type}", tags=["Masters"])
async def get_master(type: str):
    data = await db["masters"].find_one({"type": type})
    if not data:
        raise HTTPException(status_code=404, detail="Master not found")
    return data["values"]

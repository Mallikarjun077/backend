from fastapi import APIRouter, Depends, HTTPException
from database import profiles
from auth import settings
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
@router.get("/profile/")
async def get_profile(user=Depends(get_current_user)):
    user_id = str(user.get("sub"))
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user ID from token")

    profile = await profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found")

    # Convert ObjectId to string for frontend
    profile["_id"] = str(profile.get("_id", ""))
    profile["image"] = profile.get("image_path", "")
    
    return profile

@router.get("/all-profiles/")
async def get_all_profiles(user=Depends(get_current_user)):
    current_user_id = str(user["sub"])
    cursor = profiles.find({"user_id": {"$ne": current_user_id}})
    result = []

    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["image"] = doc.get("image_path", "")
        result.append(doc)

    return result

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from profile_routes import router as profile_router
from reset import router as reset_router
from fastapi.openapi.utils import get_openapi
from database import masters
import asyncio

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI backend"}

# Allow requests from frontend (adjust origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(reset_router, prefix="/api")



@app.on_event("startup")
async def insert_master_data():
    async def safe_insert(type_, values):
        if await masters.count_documents({"type": type_}) == 0:
            await masters.insert_one({"type": type_, "values": values})

    await safe_insert("religion", ["Hindu", "Muslim", "Christian", "Sikh", "Jain", "Other"])
    await safe_insert("caste", ["Brahmin", "Kshatriya", "Vaishya", "Shudra", "Other"])
    await safe_insert("job_sector", ["Government", "Private", "Business", "Defence", "Other"])
    await safe_insert("qualification", ["B.Tech", "M.Tech", "MBA", "MBBS", "CA", "Diploma", "Other"])
    await safe_insert("eating_habits", ["Vegetarian", "Non-Vegetarian", "Eggetarian", "Vegan"])
    await safe_insert("annual_income", ["Below ₹2 Lakh", "₹2 - ₹5 Lakh", "₹5 - ₹10 Lakh", "₹10 - ₹25 Lakh", "₹25 - ₹50 Lakh", "Above ₹50 Lakh"])
    await safe_insert("country", ["India", "USA", "UK", "Canada", "Australia", "Other"])
    await safe_insert("state", ["Karnataka", "Maharashtra", "Tamil Nadu", "Telangana", "Delhi", "Other"])
    await safe_insert("city", ["Bangalore", "Mumbai", "Chennai", "Hyderabad", "Delhi", "Other"])
    await safe_insert("gender", ["Male", "Female", "Other"])
    await safe_insert("language", ["Kannada", "Hindi", "Telugu", "Tamil", "Marathi", "Malayalam", "English", "Urdu", "Other"])
    await safe_insert("mother_tongue", ["Hindi", "English", "Kannada", "Telugu", "Tamil", "Malayalam", "Marathi", "Gujarati", "Punjabi", "Bengali", "Urdu", "Odia", "Assamese", "Rajasthani", "Sindhi", "Konkani", "Tulu", "Other"])
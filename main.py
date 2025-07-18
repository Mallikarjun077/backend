from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from profile_routes import router as profile_router
from reset import router as reset_router

app = FastAPI()

# ✅ Allow requests from frontend (adjust origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://192.168.236.102:8081"],  # You can restrict to ["http://localhost:3000"] or your mobile IP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(reset_router, prefix="/api")


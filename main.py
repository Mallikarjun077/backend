from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from profile_routes import router as profile_router
from reset import router as reset_router

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


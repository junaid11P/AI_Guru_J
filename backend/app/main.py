from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from app.database import mongodb_ops
from app.api.tutor_router import router as tutor_router

app = FastAPI(
    title="AI Guru J Backend",
    description="Backend API for AI Guru J deployed on Render."
)

# --- CORS SETUP (UPDATED FOR DEPLOYMENT) ---
# We allow localhost for testing AND the specific Render URL for production.
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    # This environment variable will be set in Render dashboard later
    os.getenv("FRONTEND_URL", ""), 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Allows only specific origins from the list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Ensure DB is connected on startup
    mongodb_ops.initialize_db()

@app.get("/")
async def root():
    return {"message": "AI Guru J Backend is Live!"}

app.include_router(tutor_router, prefix="/api/tutor", tags=["Tutor Interaction"])
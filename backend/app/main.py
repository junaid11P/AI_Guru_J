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

# CORS setup
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "https://aiguruj-s8fa.onrender.com",
]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    import shutil
    mongodb_ops.initialize_db()
    rhubarb_path = os.getenv("RHUBARB_BINARY", "rhubarb")
    if not shutil.which(rhubarb_path):
        logging.warning(f"⚠️ Rhubarb binary not found in path: {rhubarb_path}")

@app.get("/")
async def root():
    return {"message": "AI Guru J Backend is Live!"}

app.include_router(tutor_router, prefix="/api/tutor", tags=["Tutor Interaction"])
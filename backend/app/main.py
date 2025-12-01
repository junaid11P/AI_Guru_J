from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from typing import Any, Dict
import dns.resolver

# Import DB logic
from app.database import mongodb_ops

from app.api.tutor_router import router as tutor_router
import os
print("DEBUG CHECK KEY:", os.getenv("GEMINI_API_KEY"))

app = FastAPI(
    title="AI Guru J Backend",
    description="Backend API for AI Guru J: handles Whisper audio intake, FLAN‑T5 processing, gTTS responses, and tutor interaction endpoints."
)

# --- CORS SETUP ---
origins = [
    "http://localhost:5173",    # Standard Vite React port
    "http://127.0.0.1:5173",    # Alternate local address
    "http://localhost:3000",    # Common alternative
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    mongodb_ops.initialize_db()

@app.get("/")
async def root():
    return {"message": "Welcome to AI Guru J Backend."}

# --- REGISTER ROUTER ---
app.include_router(tutor_router, prefix="/api/tutor", tags=["Tutor Interaction"])
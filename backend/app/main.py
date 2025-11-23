from dotenv import load_dotenv
import os

# Load .env into os.environ before other app modules import environment variables
load_dotenv()

from fastapi import FastAPI
from .api import tutor_router
from .database.mongodb_ops import check_db_connection
import logging

logging.basicConfig(level=logging.INFO)

# Run database check on startup for verification
check_db_connection()

app = FastAPI(
    title="AI Guru J Backend",
    description="Backend API for AI Guru J: handles Whisper audio intake, FLAN‑T5 processing, gTTS responses, and tutor interaction endpoints."
)

# Include the router for all tutor-related endpoints
app.include_router(tutor_router.router, prefix="/api/tutor", tags=["Tutor Interaction"])

@app.get("/")
async def root():
    """Simple health check endpoint."""
    return {"message": "Welcome to AI Guru J Backend. Visit /docs for API documentation."}

# To run the app: uvicorn app.main:app --reload
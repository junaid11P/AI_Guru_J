from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import logging
import shutil
import os
import random  # <--- Needed for random mouth shapes
import whisper
from urllib.parse import quote_plus
from typing import Optional

# Core imports
from ..core.speech_synth import generate_speech
from ..core.nlp_engine import get_ai_explanation
from ..database.mongodb_ops import log_interaction

router = APIRouter()
logger = logging.getLogger(__name__)

# --- LOAD WHISPER ---
try:
    whisper_model = whisper.load_model("base")
except Exception as e:
    logger.error(f"Failed to load Whisper: {e}")

# --- UTILS ---
def remove_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logger.error(f"Error removing temp file {path}: {e}")

def mock_rhubarb_lipsync(text: str):
    """
    Generates fake lip-sync data since we don't have the real Rhubarb tool running.
    """
    if not text:
        return {"metadata": {"duration": 0}, "mouthCues": []}

    # Estimate audio duration based on text length (approx 0.08s per char)
    duration = len(text) * 0.10
    cues = []
    current_time = 0.0
    
    # Rhubarb shapes: A, B, C, D, E, F, G, H, X
    shapes = ["A", "B", "C", "D", "E", "F", "G", "H"] 

    # Generate a random mouth shape every ~0.15 seconds
    while current_time < duration:
        shape = random.choice(shapes)
        # Random duration for this shape (between 0.1s and 0.25s)
        step = random.uniform(0.1, 0.25)
        
        end_time = min(current_time + step, duration)
        
        cues.append({
            "start": round(current_time, 2),
            "end": round(end_time, 2),
            "value": shape
        })
        
        current_time = end_time

    # Ensure mouth closes at the end
    cues.append({"start": round(current_time, 2), "end": round(current_time + 0.1, 2), "value": "X"})

    return {"metadata": {"duration": duration}, "mouthCues": cues}

# --- ROUTES ---
@router.post("/query/")
async def handle_query(
    audio_file: Optional[UploadFile] = File(None),
    text_query: Optional[str] = Form(None),
    teacher_gender: str = Form("female")
):
    temp_filename = None
    user_query = ""

    try:
        # 1. Process Input
        if audio_file:
            temp_filename = f"temp_{audio_file.filename}"
            with open(temp_filename, "wb") as buffer:
                shutil.copyfileobj(audio_file.file, buffer)
            result = whisper_model.transcribe(temp_filename, fp16=False)
            user_query = result["text"].strip()
        elif text_query:
            user_query = text_query.strip()
        else:
            raise HTTPException(status_code=400, detail="No input provided.")

        # 2. AI Processing
        explanation_text, code_block = get_ai_explanation(user_query)

        # 3. Audio URL
        if explanation_text:
            safe_text = quote_plus(explanation_text)
            audio_url = f"http://127.0.0.1:8000/api/tutor/audio_stream/?text={safe_text}&gender={teacher_gender}"
        else:
            audio_url = None
            explanation_text = "I couldn't generate an answer."

        # 4. GENERATE LIP SYNC DATA (The Fix!)
        # We now call the function instead of returning an empty list
        lip_sync_data = mock_rhubarb_lipsync(explanation_text)

        # 5. Log
        log_interaction(user_query, explanation_text, code_block, lip_sync_data, audio_url)

        return {
            "user_query": user_query,
            "explanation": explanation_text,
            "code": code_block,
            "lip_sync": lip_sync_data, # Frontend receives this now!
            "audio_url": audio_url
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_filename and os.path.exists(temp_filename):
            os.remove(temp_filename)

@router.get("/audio_stream/")
async def stream_audio(
    text: str, 
    gender: str = "female", 
    background_tasks: BackgroundTasks = None
):
    try:
        file_path = await generate_speech(text, gender)
        if background_tasks:
            background_tasks.add_task(remove_file, file_path)
        return FileResponse(file_path, media_type="audio/mpeg", filename="speech.mp3")
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
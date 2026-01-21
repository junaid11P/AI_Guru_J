from fastapi import APIRouter, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import logging
import os
import random
from urllib.parse import quote_plus
from typing import Optional

# Core imports
from ..core.speech_synth import generate_speech
from ..core.nlp_engine import get_ai_explanation
from ..database.mongodb_ops import log_interaction

router = APIRouter()
logger = logging.getLogger(__name__)

# --- UTILS ---
def remove_file(path: str):
    """Deletes a temporary file after use."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logger.error(f"Error removing temp file {path}: {e}")

def mock_rhubarb_lipsync(text: str):
    """
    Generates fake lip-sync data (randomized but realistic-looking)
    for the 3D Avatar.
    """
    if not text:
        return {"metadata": {"duration": 0}, "mouthCues": []}

    # Estimate duration: approx 0.10s per character
    duration = len(text) * 0.10
    cues = []
    current_time = 0.0
    
    # Standard Rhubarb shapes
    shapes = ["A", "B", "C", "D", "E", "F", "G", "H"] 

    while current_time < duration:
        shape = random.choice(shapes)
        step = random.uniform(0.1, 0.25) # Random duration for realism
        
        end_time = min(current_time + step, duration)
        
        cues.append({
            "start": round(current_time, 2),
            "end": round(end_time, 2),
            "value": shape
        })
        current_time = end_time

    # Always close mouth at the end
    cues.append({"start": round(current_time, 2), "end": round(current_time + 0.1, 2), "value": "X"})

    return {"metadata": {"duration": duration}, "mouthCues": cues}

# --- ROUTES ---
@router.post("/query/")
async def handle_query(
    background_tasks: BackgroundTasks,  # <--- Added for non-blocking logging
    text_query: Optional[str] = Form(None),
    teacher_gender: str = Form("female")
):
    user_query_for_log = ""

    try:
        explanation_text = ""
        code_block = ""

        # 1. PROCESS INPUT (Text Only now, as Frontend handles STT)
        if text_query:
            user_query_for_log = text_query.strip()
            # Standard Text Query (or Transcribed Text)
            explanation_text, code_block = get_ai_explanation(user_query_for_log)
            
        else:
            raise HTTPException(status_code=400, detail="No input provided.")

        # 2. GENERATE AUDIO URL (TTS)
        if explanation_text:
            safe_text = quote_plus(explanation_text)
            # Use environment variable for URL if available, else standard relative path
            base_url = os.getenv("RENDER_EXTERNAL_URL", "http://127.0.0.1:8000")
            audio_url = f"{base_url}/api/tutor/audio_stream/?text={safe_text}&gender={teacher_gender}"
        else:
            audio_url = None
            explanation_text = "I'm sorry, I couldn't process that request."

        # 3. GENERATE LIP SYNC
        lip_sync_data = mock_rhubarb_lipsync(explanation_text)

        # 4. LOG INTERACTION (BACKGROUND TASK)
        # This runs AFTER the response is sent, speeding up the UI significantly.
        background_tasks.add_task(
            log_interaction, 
            user_query_for_log, 
            explanation_text, 
            code_block, 
            lip_sync_data, 
            audio_url
        )

        return {
            "user_query": user_query_for_log,
            "explanation": explanation_text,
            "code": code_block,
            "lip_sync": lip_sync_data,
            "audio_url": audio_url
        }

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio_stream/")
async def stream_audio(
    text: str, 
    gender: str = "female", 
    background_tasks: BackgroundTasks = None
):
    try:
        # Generate the MP3 file using Edge TTS (or backup)
        file_path = await generate_speech(text, gender)
        
        # Schedule file deletion after the response is sent
        if background_tasks:
            background_tasks.add_task(remove_file, file_path)
            
        return FileResponse(file_path, media_type="audio/mpeg", filename="speech.mp3")
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
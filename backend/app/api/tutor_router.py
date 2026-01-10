from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import logging
import os
import io

from app.core.speech_synth import generate_speech
from app.core.nlp_engine import get_ai_explanation
from app.utils.rhubarb_generator import generate_lip_sync_json
from app.database.mongodb_ops import log_interaction
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

def remove_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        logger.error(f"Error removing temp file {path}: {e}")

@router.post("/query/")
async def handle_query(
    background_tasks: BackgroundTasks,
    text_query: str = Form(...),
    teacher_gender: str = Form("female")
):
    try:
        explanation_text, code_block = get_ai_explanation(text_query)
        if not explanation_text:
            explanation_text = "I'm sorry, I couldn't process that request."

        # Generate TTS audio (WAV for Rhubarb)
        audio_path = await generate_speech(explanation_text, gender=teacher_gender, wav_output=True)

        # Read WAV into BytesIO
        with open(audio_path, "rb") as f:
            audio_bytes = io.BytesIO(f.read())

        # Generate real lip-sync JSON
        lip_sync_data = generate_lip_sync_json(audio_bytes)

        # Generate MP3 URL for frontend streaming
        mp3_path = await generate_speech(explanation_text, gender=teacher_gender)
        audio_url = f"{settings.BASE_URL}/api/tutor/audio_stream/?file_path={mp3_path}"

        # Cleanup (Only WAV, MP3 is cleaned after streaming)
        background_tasks.add_task(remove_file, audio_path)

        # Log interaction
        background_tasks.add_task(
            log_interaction,
            text_query,
            explanation_text,
            code_block,
            lip_sync_data,
            audio_url
        )

        return {
            "user_query": text_query,
            "explanation": explanation_text,
            "code": code_block,
            "lip_sync": lip_sync_data,
            "audio_url": audio_url
        }

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio_stream/")
async def stream_audio(background_tasks: BackgroundTasks, file_path: str):
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Add cleanup to run after the file is served
        background_tasks.add_task(remove_file, file_path)
        
        return FileResponse(file_path, media_type="audio/mpeg", filename="speech.mp3")
    except Exception as e:
        logger.error(f"TTS Streaming Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
import subprocess
import tempfile
import json
import os
import io
import logging
import gc
from app.config import settings

logger = logging.getLogger(__name__)

def generate_lip_sync_json(mp3_path: str) -> dict:
    temp_wav = None
    temp_json = None
    try:
        # 1. Convert MP3 → WAV (Downsample to 16kHz Mono for memory efficiency)
        fd, temp_wav = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        
        logger.info(f"🎞️ Converting {os.path.basename(mp3_path)} to 8kHz WAV...")
        gc.collect() # Free memory before subprocess
        ffmpeg_cmd = [settings.FFMPEG_PATH, "-y", "-i", mp3_path, "-ar", "8000", "-ac", "1", temp_wav]
        ffmpeg_proc = subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if ffmpeg_proc.returncode != 0:
            logger.error("FFmpeg failed")
            return {"error": "FFmpeg failed"}

        # 2. Run Rhubarb
        fd, temp_json = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        
        logger.info("👄 Generating lip-sync data with Rhubarb...")
        gc.collect() # Free memory before subprocess
        rhubarb_cmd = [settings.RHUBARB_BINARY, temp_wav, "-o", temp_json, "-f", settings.RHUBARB_FORMAT]
        rhubarb_proc = subprocess.run(rhubarb_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if rhubarb_proc.returncode != 0:
            logger.error("Rhubarb failed")
            return {"error": "Rhubarb failed"}

        # 3. Load & Return JSON
        with open(temp_json, "r") as f:
            data = json.load(f)
        
        logger.info("✨ Lip-sync generation complete.")
        return data

    except Exception as e:
        return {"error": str(e)}
    finally:
        # Cleanup
        if temp_wav and os.path.exists(temp_wav):
            os.remove(temp_wav)
        if temp_json and os.path.exists(temp_json):
            os.remove(temp_json)
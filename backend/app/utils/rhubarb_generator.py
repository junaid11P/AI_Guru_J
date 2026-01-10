import subprocess
import tempfile
import json
import os
import io
from app.config import settings

def generate_lip_sync_json(mp3_path: str) -> dict:
    temp_wav = None
    temp_json = None
    try:
        # 1. Convert MP3 → WAV (Rhubarb needs WAV)
        fd, temp_wav = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        
        ffmpeg_cmd = [settings.FFMPEG_PATH, "-y", "-i", mp3_path, temp_wav]
        ffmpeg_proc = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if ffmpeg_proc.returncode != 0:
            return {"error": "FFmpeg failed", "details": ffmpeg_proc.stderr}

        # 2. Run Rhubarb
        fd, temp_json = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        
        rhubarb_cmd = [settings.RHUBARB_BINARY, temp_wav, "-o", temp_json, "-f", settings.RHUBARB_FORMAT]
        rhubarb_proc = subprocess.run(rhubarb_cmd, capture_output=True, text=True)
        if rhubarb_proc.returncode != 0:
            return {"error": "Rhubarb failed", "details": rhubarb_proc.stderr}

        # 3. Load & Return JSON
        with open(temp_json, "r") as f:
            data = json.load(f)

        return data

    except Exception as e:
        return {"error": str(e)}
    finally:
        # Cleanup
        if temp_wav and os.path.exists(temp_wav):
            os.remove(temp_wav)
        if temp_json and os.path.exists(temp_json):
            os.remove(temp_json)
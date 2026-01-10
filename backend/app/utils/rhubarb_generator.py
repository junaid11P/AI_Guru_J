import subprocess
import tempfile
import json
import os
import io
from app.config import settings

def generate_lip_sync_json(audio_stream: io.BytesIO) -> dict:
    try:
        # Save BytesIO to MP3
        temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_mp3.write(audio_stream.read())
        temp_mp3.close()

        # Convert MP3 → WAV
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_wav.close()
        ffmpeg_cmd = [settings.FFMPEG_PATH, "-y", "-i", temp_mp3.name, temp_wav.name]
        ffmpeg_proc = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if ffmpeg_proc.returncode != 0:
            return {"error": "FFmpeg failed", "details": ffmpeg_proc.stderr}

        # Rhubarb
        temp_json = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        temp_json.close()
        rhubarb_cmd = [settings.RHUBARB_BINARY, temp_wav.name, "-o", temp_json.name, "-f", settings.RHUBARB_FORMAT]
        rhubarb_proc = subprocess.run(rhubarb_cmd, capture_output=True, text=True)
        if rhubarb_proc.returncode != 0:
            return {"error": "Rhubarb failed", "details": rhubarb_proc.stderr}

        # Load JSON
        with open(temp_json.name, "r") as f:
            data = json.load(f)

        # Cleanup
        os.remove(temp_mp3.name)
        os.remove(temp_wav.name)
        os.remove(temp_json.name)

        return data

    except Exception as e:
        return {"error": str(e)}
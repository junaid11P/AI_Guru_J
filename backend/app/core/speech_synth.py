import logging
import tempfile
import os
import re
import requests
import base64
import subprocess
from gtts import gTTS
from app.config import settings

logger = logging.getLogger(__name__)

TIKTOK_VOICES = {
    "male": "en_us_006",
    "female": "en_us_001"
}

def clean_text_for_speech(text: str) -> str:
    if not text: return ""
    text = re.sub(r"[*`_#\"']", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def generate_tiktok_audio(text: str, voice: str) -> str:
    try:
        url = "https://tiktok-tts.weilnet.workers.dev/api/generation"
        payload = {"text": text, "voice": voice}
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                audio_bytes = base64.b64decode(data["data"])
                fd, path = tempfile.mkstemp(suffix=".mp3")
                os.close(fd)
                with open(path, 'wb') as f:
                    f.write(audio_bytes)
                return path
            else:
                logger.error(f"TikTok API Error: {data.get('error')}")
        else:
            logger.error(f"TikTok HTTP Error: {response.status_code}")
    except Exception as e:
        logger.error(f"TikTok TTS Failed: {e}")
    return None

async def generate_speech(text_to_speak: str, gender: str = "female", wav_output: bool = False) -> str:
    if not text_to_speak:
        raise ValueError("Empty text provided")
    
    clean_text = clean_text_for_speech(text_to_speak)
    logger.info(f"🎤 Synthesizing ({gender}): '{clean_text[:30]}...'")

    tiktok_voice = TIKTOK_VOICES.get(gender, "en_us_001")
    path = generate_tiktok_audio(clean_text, tiktok_voice)

    # Fallback Google TTS
    if not path:
        logger.warning("⚠️ TikTok failed. Using Google TTS Backup.")
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(path)

    # Convert to WAV if needed
    if wav_output:
        fd, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        ffmpeg_cmd = [settings.FFMPEG_PATH, "-y", "-i", path, wav_path]
        proc = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            logger.error(f"FFmpeg conversion failed: {proc.stderr}")
            raise RuntimeError("FFmpeg conversion failed")
        os.remove(path)
        path = wav_path

    return path
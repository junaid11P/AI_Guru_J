import logging
import tempfile
import os
import re
import requests
import base64
from gtts import gTTS

logger = logging.getLogger(__name__)

# --- VOICE CONFIGURATION ---
# TikTok Voice IDs
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
    """
    Connects to TikTok's TTS API directly.
    Using a public reverse-engineered endpoint.
    """
    try:
        # Public instance of TikTok TTS wrapper
        url = "https://tiktok-tts.weilnet.workers.dev/api/generation"
        
        payload = {
            "text": text,
            "voice": voice
        }
        
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                # Decode base64 audio
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

async def generate_speech(text_to_speak: str, gender: str = "female") -> str:
    """
    Generates TikTok Audio.
    Fallback to Google TTS if TikTok fails.
    """
    try:
        if not text_to_speak:
            raise ValueError("Empty text provided")
            
        clean_text = clean_text_for_speech(text_to_speak)
        logger.info(f"🎤 Synthesizing ({gender}): '{clean_text[:30]}...'")

        # --- TikTok TTS ---
        tiktok_voice = TIKTOK_VOICES.get(gender, "en_us_001")
        logger.info(f"� Trying TikTok TTS ({tiktok_voice})...")
        
        path = generate_tiktok_audio(clean_text, tiktok_voice)
        if path:
            logger.info("✅ TikTok TTS Success")
            return path
        
        # --- Fallback: Google TTS ---
        logger.warning("⚠️ TikTok failed. Using Google TTS Backup.")
        
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(path)
        return path

    except Exception as e:
        logger.critical(f"💀 CRITICAL TTS ERROR: {e}")
        raise e
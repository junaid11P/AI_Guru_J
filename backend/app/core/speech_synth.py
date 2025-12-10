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
# Male: en_us_006 (Male 1 - Very popular voice)
# Female: en_us_001 (Female 1)
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
    """
    try:
        # TikTok API Endpoint (Publicly accessible via some wrappers, simplified here)
        # Note: Direct TikTok API calls often require a session id or valid headers.
        # If this fails, we will fall back to Google immediately.
        
        # Using a reliable public proxy for TikTok TTS to avoid complex auth
        # This is a common workaround for "free" access
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
    Strategy:
    1. Try TikTok TTS (High Quality Male/Female).
    2. Fallback to Google TTS (Reliable Female).
    """
    try:
        if not text_to_speak:
            raise ValueError("Empty text provided")
            
        clean_text = clean_text_for_speech(text_to_speak)
        logger.info(f"🎤 Synthesizing ({gender}): '{clean_text[:30]}...'")

        # --- OPTION 1: TikTok TTS (Male & Female) ---
        tiktok_voice = TIKTOK_VOICES.get(gender, "en_us_001")
        logger.info(f"🎵 Trying TikTok TTS ({tiktok_voice})...")
        
        path = generate_tiktok_audio(clean_text, tiktok_voice)
        if path:
            logger.info("✅ TikTok TTS Success")
            return path
        
        # --- OPTION 2: Google TTS Fallback ---
        logger.warning("⚠️ TikTok failed. Using Google TTS Backup.")
        
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(path)
        return path

    except Exception as e:
        logger.critical(f"💀 CRITICAL TTS ERROR: {e}")
        raise e
import logging
import tempfile
import os
import re
import requests
from gtts import gTTS

logger = logging.getLogger(__name__)

# --- VOICE CONFIGURATION ---
# "Brian" is the famous British male voice.
MALE_VOICE_ID = "Brian"

def clean_text_for_speech(text: str) -> str:
    """
    Cleans text to prevent URL/API errors.
    """
    if not text: 
        return ""
    # Remove Markdown and Quotes
    text = re.sub(r"[*`_#\"']", "", text)
    # Clean whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def generate_streamelements_audio(text: str, voice: str) -> str:
    """
    Uses StreamElements with FAKE BROWSER HEADERS to bypass 401 errors.
    """
    try:
        url = f"https://api.streamelements.com/kappa/v2/speech?voice={voice}&text={text}"
        
        # 1. THE FIX: Add a User-Agent header so we look like a real Chrome browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Referer": "https://streamelements.com/",
            "Origin": "https://streamelements.com"
        }
        
        # 2. Send request with headers
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        
        if response.status_code == 200:
            fd, path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            
            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return path
        else:
            logger.error(f"StreamElements API Error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"StreamElements Connection Failed: {e}")
        return None

async def generate_speech(text_to_speak: str, gender: str = "female") -> str:
    """
    Logic:
    - FEMALE: Use Google TTS (gTTS).
    - MALE: Use StreamElements (Brian) with headers.
    """
    try:
        if not text_to_speak:
            raise ValueError("Empty text provided")
            
        clean_text = clean_text_for_speech(text_to_speak)
        logger.info(f"🎤 Synthesizing ({gender}): '{clean_text[:30]}...'")

        # --- OPTION 1: MALE (StreamElements) ---
        if gender == "male":
            logger.info(f"🔵 Using StreamElements ({MALE_VOICE_ID})...")
            path = generate_streamelements_audio(clean_text, MALE_VOICE_ID)
            if path:
                return path
            else:
                logger.warning("⚠️ StreamElements failed. Falling back to Google (Female).")

        # --- OPTION 2: FEMALE (Google) ---
        # Also serves as fallback if Male API fails
        logger.info("🟢 Using Google TTS (Female)")
        
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(path)
        return path

    except Exception as e:
        logger.critical(f"💀 CRITICAL TTS ERROR: {e}")
        raise e
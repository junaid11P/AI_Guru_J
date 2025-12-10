import edge_tts
import logging
import tempfile
import os
import re
from gtts import gTTS

logger = logging.getLogger(__name__)

# --- EXPANDED VOICE LIST (The Fix) ---
# It will try these one by one. If Prabhat fails, it tries Christopher, then Ryan, etc.
VOICES = {
    "male": [
        "en-IN-PrabhatNeural",      # 1. Indian Male (Best for Guru J)
        "en-US-ChristopherNeural",  # 2. US Male (Robust)
        "en-GB-RyanNeural",         # 3. UK Male (Very Reliable)
        "en-AU-WilliamNeural",      # 4. Australian Male
        "en-CA-LiamNeural"          # 5. Canadian Male
    ],
    "female": [
        "en-IN-NeerjaNeural",       # 1. Indian Female
        "en-US-AriaNeural",         # 2. US Female
        "en-GB-SoniaNeural",        # 3. UK Female
        "en-AU-NatashaNeural"       # 4. Australian Female
    ]
}

def clean_text_for_speech(text: str) -> str:
    """
    Cleans text to prevent crashes (removes quotes, stars, etc.)
    """
    if not text: 
        return ""
    
    # Remove Markdown (*bold*, `code`, # headers)
    text = re.sub(r"[*`_#]", "", text)
    
    # Remove Quotes (Single and Double) - Common crash cause!
    text = text.replace('"', '').replace("'", "")
    
    # Clean whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

async def generate_speech(text_to_speak: str, gender: str = "female") -> str:
    """
    Multi-Voice Retry Strategy:
    Tries 5 different Edge voices before giving up and using Google.
    """
    try:
        if not text_to_speak:
            raise ValueError("Empty text provided")
            
        clean_text = clean_text_for_speech(text_to_speak)
        logger.info(f"🎤 Synthesizing ({gender}): '{clean_text[:30]}...'")

        # Create Temp File
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

        # Get candidate voices
        candidate_voices = VOICES.get(gender, VOICES["female"])

        # --- ATTEMPT: Try Edge TTS Voices in Order ---
        for voice in candidate_voices:
            try:
                # logger.info(f"👉 Trying Voice: {voice}") # Optional debug log
                communicate = edge_tts.Communicate(clean_text, voice)
                await communicate.save(path)

                if os.path.getsize(path) > 0:
                    logger.info(f"✅ Success with {voice}")
                    return path # RETURN IMMEDIATELY ON SUCCESS
                
            except Exception as e:
                logger.warning(f"⚠️ Voice {voice} failed. Trying next...")
                # Continue loop to next voice

        # --- FALLBACK: GOOGLE TTS (Last Resort - Female Only) ---
        logger.error(f"❌ All {len(candidate_voices)} Edge voices failed. Using Google Backup.")
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(path)
        return path

    except Exception as e:
        logger.critical(f"💀 CRITICAL TTS ERROR: {e}")
        raise e
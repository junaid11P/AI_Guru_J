import edge_tts
import logging
import tempfile
import os
import re
from gtts import gTTS

logger = logging.getLogger(__name__)

# SWITCH TO ROBUST BRITISH VOICES (Often more reliable on Render)
VOICES = {
    "male": [
        "en-IE-ConnorNeural",       # 1. Irish Male (Very Reliable)
        "en-ZA-LukeNeural",         # 2. South African Male (Reliable)
        "en-PH-JamesNeural",        # 3. Filipino Male
        "en-GB-RyanNeural",         # 4. British Male
        "en-US-ChristopherNeural",  # 5. US Male
        "en-IN-PrabhatNeural"       # 6. Indian Male
    ], 
    "female": "en-GB-SoniaNeural"
}

def clean_text_for_speech(text: str) -> str:
    """
    Aggressively cleans text to prevent TTS crashes.
    Removes Markdown, quotes, special chars, and newlines.
    """
    if not text: 
        return ""
    
    # 1. Remove Markdown (bold, code blocks, etc.)
    text = re.sub(r"[*`_#]", "", text)
    
    # 2. Remove Quotes (Single and Double) - Common crash cause!
    text = text.replace('"', '').replace("'", "")
    
    # 3. Replace newlines with spaces to keep flow
    text = text.replace('\n', ' ')
    
    # 4. Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

async def generate_speech(text_to_speak: str, gender: str = "female") -> str:
    """
    Generates speech, favoring Edge TTS (Male/Female support).
    Falls back to Google TTS (Female only) if Edge fails.
    """
    try:
        # 1. Safety Check & Cleaning
        if not text_to_speak:
            raise ValueError("Empty text provided")
            
        clean_text = clean_text_for_speech(text_to_speak)
        
        # Log what we are sending (first 50 chars)
        logger.info(f"🎤 Synthesizing ({gender}): '{clean_text[:50]}...'")

        # 2. Create Temp File
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

        # --- PRIMARY: EDGE TTS (Supports Male) ---
        try:
            voice = VOICES.get(gender, VOICES["female"])
            communicate = edge_tts.Communicate(clean_text, voice)
            await communicate.save(path)

            if os.path.getsize(path) > 0:
                return path
            else:
                logger.warning("⚠️ Edge TTS file was empty.")

        except Exception as e:
            logger.error(f"⚠️ Edge TTS Failed: {e}")

        # --- FALLBACK: GOOGLE TTS (Female Only) ---
        # We only reach here if Edge TTS failed.
        logger.info("🔄 Switching to Backup Google TTS (Female Only)...")
        
        # Note: gTTS does not support male voices.
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(path)
        return path

    except Exception as e:
        logger.critical(f"❌ ALL TTS ENGINES FAILED: {e}")
        raise e
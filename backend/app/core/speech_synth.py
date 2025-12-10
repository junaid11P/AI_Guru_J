import edge_tts
import logging
import tempfile
import os
import re
from gtts import gTTS  # The backup engine

logger = logging.getLogger(__name__)

# Primary Voices (High Quality)
VOICES = {
    "male": "en-US-ChristopherNeural",
    "female": "en-US-AriaNeural"
}

def clean_text_for_speech(text: str) -> str:
    """
    Removes Markdown symbols that might break TTS or sound weird.
    Example: `variable` -> variable, **bold** -> bold
    """
    # Remove backticks, asterisks, underscores, and excessive whitespace
    text = re.sub(r"[`*_]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

async def generate_speech(text_to_speak: str, gender: str = "female") -> str:
    """
    Tries Edge TTS (High Quality). If it fails, falls back to Google TTS (Reliable).
    """
    if not text_to_speak:
        raise ValueError("No text provided for TTS")

    # 1. Clean the text
    clean_text = clean_text_for_speech(text_to_speak)
    logger.info(f"🎤 Synthesizing: '{clean_text[:30]}...'")

    # 2. Create Temp File
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)

    try:
        # --- ATTEMPT 1: Microsoft Edge TTS (Best Quality) ---
        voice = VOICES.get(gender, VOICES["female"])
        communicate = edge_tts.Communicate(clean_text, voice)
        await communicate.save(path)

        # Check if file is valid
        if os.path.getsize(path) > 0:
            return path
        else:
            logger.warning("⚠️ Edge TTS produced empty file. Switching to backup...")

    except Exception as e:
        logger.error(f"⚠️ Edge TTS Failed: {e}")

    # --- ATTEMPT 2: Google TTS (Backup / Fail-Safe) ---
    try:
        logger.info("🔄 Using Backup Google TTS...")
        # gTTS is synchronous, but fast enough for a backup
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(path)
        return path
        
    except Exception as e:
        logger.critical(f"❌ ALL TTS ENGINES FAILED: {e}")
        if os.path.exists(path):
            os.remove(path)
        raise e
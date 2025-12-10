import edge_tts
import logging
import tempfile
import os
import re
from gtts import gTTS

logger = logging.getLogger(__name__)

# --- VOICE CONFIGURATION ---
# We now have a LIST of voices for each gender.
# Priority: 1. Indian (Theme accurate) -> 2. US (Reliable)
VOICES = {
    "male": ["en-IN-PrabhatNeural", "en-US-ChristopherNeural"], 
    "female": ["en-IN-NeerjaNeural", "en-US-AriaNeural"]
}

def clean_text_for_speech(text: str) -> str:
    """
    Aggressively cleans text to prevent TTS crashes.
    """
    if not text: 
        return ""
    
    # 1. Remove Markdown (*bold*, `code`, # headers)
    text = re.sub(r"[*`_#]", "", text)
    
    # 2. Remove Quotes (Single and Double) - Common crash cause!
    text = text.replace('"', '').replace("'", "")
    
    # 3. Clean whitespace (newlines become spaces)
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

async def generate_speech(text_to_speak: str, gender: str = "female") -> str:
    """
    Tries multiple Edge TTS voices. If ALL fail, falls back to Google TTS.
    """
    try:
        if not text_to_speak:
            raise ValueError("Empty text provided")
            
        clean_text = clean_text_for_speech(text_to_speak)
        logger.info(f"🎤 Synthesizing ({gender}): '{clean_text[:30]}...'")

        # Create Temp File
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)

        # Get the list of voices for the requested gender
        # Default to female list if gender key is missing
        candidate_voices = VOICES.get(gender, VOICES["female"])

        # --- ATTEMPT 1 & 2: Try Edge TTS Voices in order ---
        for voice in candidate_voices:
            try:
                logger.info(f"👉 Trying Voice: {voice}")
                communicate = edge_tts.Communicate(clean_text, voice)
                await communicate.save(path)

                if os.path.getsize(path) > 0:
                    logger.info(f"✅ Success with {voice}")
                    return path # Exit function with success
                
                logger.warning(f"⚠️ Voice {voice} produced empty file.")

            except Exception as e:
                logger.warning(f"⚠️ Voice {voice} failed: {e}")
                # Loop continues to the next voice...

        # --- ATTEMPT 3: GOOGLE TTS (Last Resort) ---
        # If we reach here, ALL Edge voices failed.
        logger.error("❌ All Edge Voices failed. Switching to Google TTS (Female).")
        
        # gTTS only supports one voice per language (usually Female)
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(path)
        return path

    except Exception as e:
        logger.critical(f"💀 CRITICAL TTS ERROR: {e}")
        raise e
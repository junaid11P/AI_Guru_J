from gtts import gTTS
import io

def generate_speech(text_to_speak: str) -> io.BytesIO:
    """Converts text to speech and returns the audio as an in-memory MP3 file stream."""
    try:
        tts = gTTS(text=text_to_speak, lang='en')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0) # Reset pointer for streaming
        return mp3_fp
    except Exception as e:
        print(f"Error generating speech: {e}")
        # Return an empty buffer or handle error appropriately
        return io.BytesIO()
import logging
import re
import os
import google.generativeai as genai
from .config import settings

logging.basicConfig(level=logging.INFO)

# Configure Gemini 2.5 Flash
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    # Gemini 2.5 Flash supports native audio!
    model = genai.GenerativeModel(settings.NLP_MODEL_ID) 
    logging.info(f"Connected to {settings.NLP_MODEL_ID} with Native Audio.")
except Exception as e:
    logging.error(f"Error connecting to Gemini: {e}")
    model = None

def get_ai_explanation(user_input, is_audio=False):
    """
    Accepts either Text (str) or a File Path (audio) and generates a response.
    """
    if not model:
        return "Error: Gemini API key is missing.", "# Check logs."

    prompt_text = (
        "You are an expert Python Tutor. "
        "The user will ask a question (in text or audio). "
        "Task: Write valid Python code to solve it. "
        "Rules:\n"
        "1. Provide code inside a Markdown block: ```python ... ```\n"
        "2. Follow it with a concise explanation.\n"
        "3. Do not include 'Here is the code' filler."
    )

    try:
        content_payload = [prompt_text]

        if is_audio and user_input:
            # Upload audio file to Gemini (File API)
            # Gemini 2.5 processes audio natively!
            audio_file = genai.upload_file(path=user_input, mime_type="audio/mp3")
            content_payload.append(audio_file)
            logging.info("Audio uploaded to Gemini 2.5 Flash.")
        else:
            # Just text
            content_payload.append(f"User Question: {user_input}")

        # Generate!
        response = model.generate_content(content_payload)
        full_output = response.text
        
        # Cleanup: Code Extraction Regex
        code_pattern = r"```(?:python)?\s*(.*?)\s*```"
        code_matches = re.findall(code_pattern, full_output, re.DOTALL)
        
        if code_matches:
            code_content = "\n\n".join(code_matches).strip()
            explanation_text = re.sub(code_pattern, "", full_output, flags=re.DOTALL).strip()
        else:
            code_content = "# No code block detected."
            explanation_text = full_output

        return explanation_text, code_content

    except Exception as e:
        logging.error(f"Gemini Generation Error: {e}")
        return "I encountered an error.", f"# Error: {str(e)}"
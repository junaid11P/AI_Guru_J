import logging
import re
import google.generativeai as genai
from .config import settings

logging.basicConfig(level=logging.INFO)

# 1. Configure the Google Gemini Client
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.NLP_MODEL_ID)
    logging.info(f"Connected to Google Gemini API ({settings.NLP_MODEL_ID}).")
except Exception as e:
    logging.error(f"Error connecting to Google Gemini: {e}")
    model = None

def get_ai_explanation(user_query: str):
    """
    Generates Python code and explanation using Google Gemini 1.5 Flash.
    """
    if not model:
        return "Error: Gemini API key is missing or invalid.", "# Check server logs."

    # 2. Strict Prompting
    prompt = (
        f"You are an expert Python Tutor. \n"
        f"Task: Write valid Python code to {user_query}. \n"
        f"Rules:\n"
        f"1. Provide the code inside a Markdown block: ```python ... ```\n"
        f"2. Follow it with a concise, helpful explanation.\n"
        f"3. Do not include 'Here is the code' filler text at the start."
    )

    try:
        # 3. Generate Content
        response = model.generate_content(prompt)
        full_output = response.text
        
        # 4. Extract Code vs Text
        code_pattern = r"```(?:python)?\s*(.*?)\s*```"
        code_matches = re.findall(code_pattern, full_output, re.DOTALL)
        
        if code_matches:
            # Join multiple code blocks if present
            code_content = "\n\n".join(code_matches).strip()
            # Remove the code from the main text to get the explanation
            explanation_text = re.sub(code_pattern, "", full_output, flags=re.DOTALL).strip()
        else:
            # Fallback if no code block found
            code_content = "# No specific code block detected.\n# See explanation."
            explanation_text = full_output

        return explanation_text, code_content

    except Exception as e:
        logging.error(f"Gemini Generation Error: {e}")
        return "I encountered an error connecting to Google AI.", f"# Error: {str(e)}"
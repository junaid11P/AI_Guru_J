from transformers import T5ForConditionalGeneration, T5Tokenizer
from .config import settings
import logging

logging.basicConfig(level=logging.INFO)

# --- Global Model Loading (Occurs on startup) ---
# NOTE: Loading models can be memory intensive.
try:
    logging.info("Loading FLAN-T5 model...")
    tokenizer = T5Tokenizer.from_pretrained(settings.NLP_MODEL_ID)
    model = T5ForConditionalGeneration.from_pretrained(settings.NLP_MODEL_ID)
    logging.info("FLAN-T5 model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading FLAN-T5: {e}")
    tokenizer = None
    model = None

def get_ai_explanation(user_query: str) -> str:
    """Generates a Python explanation using the FLAN-T5 model."""
    if model is None or tokenizer is None:
        return "Sorry, the AI model is not ready yet."

    prompt = f"Explain this Python concept or code in a friendly tutor tone: {user_query}"
    
    # Generate the response
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    outputs = model.generate(input_ids, max_length=150, num_beams=5, early_stopping=True)
    
    explanation = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return explanation
import logging
import re
import ollama
from groq import Groq
import os
from .config import settings

logging.basicConfig(level=logging.INFO)

# Configuration
OLLAMA_MODEL = "llama3.2" 
GROQ_MODEL = "llama-3.1-8b-instant" # Updated to supported model

def get_ai_explanation(user_input, is_audio=False):
    """
    Accepts Text (str).
    Routes to Ollama (Local) or Groq (Cloud) based on config.
    """
    
    prompt_text = (
    "You are a friendly Python Tutor who explains like teaching a 3rd standard student. "
    f"The user will ask a question: '{user_input}'. "
    "Task:\n"
    "1. Write valid and correct Python code to solve the problem.\n"
    "2. Put the code inside a Markdown block using ```python ... ```.\n"
    "3. After the code, explain EACH LINE of the code one by one.\n"
    "4. Use very simple words and short sentences.\n"
    "5. For every line, give a small real-world example (like toys, fruits, school, or daily life).\n"
    "6. Do NOT use technical jargon.\n"
    "7. Do NOT add filler sentences like 'Here is the code'.\n"
    "8. Make the explanation friendly and easy to remember.\n"
)


    try:
        if settings.LLM_PROVIDER == "groq":
            if not settings.GROQ_API_KEY:
                return "Config Error: GROQ_API_KEY is missing.", "# Please check .env or Render settings."
            
            logging.info(f"Sending query to Groq Cloud ({GROQ_MODEL})...")
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt_text,
                    }
                ],
                model=GROQ_MODEL,
            )
            full_output = completion.choices[0].message.content

        else:
            # Default to Ollama
            logging.info(f"Sending query to Local Ollama ({OLLAMA_MODEL})...")
            response = ollama.chat(model=OLLAMA_MODEL, messages=[
                {
                    'role': 'user',
                    'content': prompt_text,
                },
            ])
            full_output = response['message']['content']
        
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
        provider = settings.LLM_PROVIDER.upper()
        logging.error(f"{provider} Generation Error: {e}")
        error_msg = str(e)
        if "connection refused" in error_msg.lower() and provider == "OLLAMA":
             return "Error: Could not connect to Ollama.", "# Please make sure Ollama is running (`ollama run llama3.2`)."
        return f"I encountered an error with {provider}.", f"# Error: {str(e)}"
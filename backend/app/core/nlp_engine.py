import logging
import re
import ollama
from groq import Groq
import os
from .config import settings

logging.basicConfig(level=logging.INFO)

# Configuration
OLLAMA_MODEL = "llama3.2" 
GROQ_MODEL = "llama3-8b-8192" # Free, equivalent to llama3.2 roughly

def get_ai_explanation(user_input, is_audio=False):
    """
    Accepts Text (str).
    Routes to Ollama (Local) or Groq (Cloud) based on config.
    """
    
    prompt_text = (
        "You are an expert Python Tutor. "
        f"The user will ask a question: '{user_input}'. "
        "Task: Write valid Python code to solve it. "
        "Rules:\n"
        "1. Provide code inside a Markdown block: ```python ... ```\n"
        "2. Follow it with a concise explanation.\n"
        "3. Do not include 'Here is the code' filler."
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
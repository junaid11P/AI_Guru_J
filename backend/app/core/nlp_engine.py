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
    "You are a friendly Python Tutor who teaches beginners and kids. "
    f"The user will ask a question: '{user_input}'. "
    "Task:\n"
    "1. Write valid and correct Python code to solve the problem.\n"
    "2. Put the code ONLY inside a Markdown block using ```python ... ```.\n"
    "3. Explain the code LINE BY LINE in very simple words.\n\n"
    "IMPORTANT: Follow this structure EXACTLY:\n\n"
    "### The Code\n"
    "```python\n"
    "# write the full solution code here\n"
    "```\n\n"
    "### Explanation\n"
    "**Line 1**: `exact code from line 1` - Simple explanation with a daily-life example.\n"
    "**Line 2**: `exact code from line 2` - Simple explanation with a daily-life example.\n"
    "**Line 3**: `exact code from line 3` - Simple explanation with a daily-life example.\n\n"
    "Rules:\n"
    "- ALWAYS copy the exact code line inside backticks.\n"
    "- ALWAYS keep code and explanation on the SAME LINE.\n"
    "- Number explanations to match the number of code lines.\n"
    "- Use words a 3rd standard student can understand.\n"
    "- Use daily-life analogies only (toys, pizza, games, school).\n"
    "- Keep sentences short and friendly.\n"
    "- Do NOT add any intro or extra text.\n"
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
            # Remove the code block and headers
            explanation_text = re.sub(code_pattern, "", full_output, flags=re.DOTALL)
            explanation_text = explanation_text.replace("### The Code", "").replace("### Explanation", "").strip()
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
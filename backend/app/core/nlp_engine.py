import logging
import re
from groq import Groq
import os
from .config import settings

logging.basicConfig(level=logging.INFO)

# Configuration
GROQ_MODEL = "llama-3.1-8b-instant" # Updated to supported model

def get_ai_explanation(user_input, is_audio=False):
    """
    Accepts Text (str).
    Routes to Groq (Cloud).
    """
    
    prompt_text = (
        "You are a friendly Python Tutor who teaches beginners and kids. "
        f"The user will ask a question: '{user_input}'.\n\n"
        "Task:\n"
        "1. Write valid and correct Python code to solve the problem.\n"
        "2. Put the code ONLY inside a Markdown block using ```python ... ```.\n"
        "3. Explain the code line-by-line using a bullet list. Provide exactly ONE unique explanation for each distinct line of code.\n\n"
        "Rules:\n"
        "- Use a BULLET LIST for the explanation (e.g., - **Line 1**: `code` - Explanation).\n"
        "- Bold the line identifier (e.g., **Line 1**).\n"
        "- Use words a 3rd standard student can understand.\n"
        "- If the code is just one line, offer ONLY one explanation for that line. DO NOT repeat explanations or add filler lines.\n"
        "- Use simple words and daily-life analogies (toys, school, etc.) that a young child can understand.\n"
        "- Keep sentences very short and avoid any intro or outro text (e.g., 'Sure!', 'Let's begin').\n"
        "Structure:\n"
        "### The Code\n"
        "```python\n"
        "# your code\n"
        "```\n\n"
        "### Explanation\n"
        "- **Line X**: `code` - Simple explanation here.\n"
    )


    try:
        # Default Strict Mode: Only Groq
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
        provider = "GROQ"
        logging.error(f"{provider} Generation Error: {e}")
        return f"I encountered an error with {provider}.", f"# Error: {str(e)}"

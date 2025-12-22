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
        "You are a friendly Python Tutor teaching beginners and kids. "
        f"The user query is: '{user_input}'.\n\n"
        "Task:\n"
        "1. Write valid Python code for the solution.\n"
        "2. Provide a line-by-line explanation using a bullet list.\n\n"
        "Critical Rules (MANDATORY):\n"
        "- Provide exactly ONE bullet point per unique line of code.\n"
        "- NEVER repeat the same Line number (e.g., **Line 1**) in the explanation section.\n"
        "- NEVER provide multiple explanations for the same line of code.\n"
        "- Use simple words and daily-life analogies and keep sentences very short.\n"
        "- Do NOT add any intro text, 'Sure!', or extra comments outside the requested headers.\n\n"
        "Exact Format:\n"
        "### The Code\n"
        "```python\n"
        "# your code here\n"
        "```\n\n"
        "### Explanation\n"
        "- **Line 1**: `code` - Simple analogy explanation.\n"
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
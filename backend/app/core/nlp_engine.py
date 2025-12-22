import logging
import re
from groq import Groq
import os
from .config import settings

logging.basicConfig(level=logging.INFO)

# Configuration
GROQ_MODEL = "llama-3.1-8b-instant" 

def get_ai_explanation(user_input, is_audio=False):
    """
    Accepts Text (str).
    Routes to Groq (Cloud).
    Returns: cleaned explanation text and raw code block.
    """
    
    # SYSTEM PROMPT: Defines the persona and strict formatting rules
    system_instruction = (
        "You are a friendly, high-energy Python Teacher for an 8-year-old child (3rd Grade). "
        "Your goal is to explain code using EMOJIS and concrete ANALOGIES (like Lego, Pizza, or Magic)."
    )

    # USER PROMPT: The specific task
    prompt_text = (
        f"The user asks: '{user_input}'.\n\n"
        "### INSTRUCTIONS\n"
        "1. Write valid Python code to solve this.\n"
        "2. Explain it step-by-step using a SINGLE analogy theme (e.g., if you choose cooking, stick to cooking terms).\n"
        "3. Use EMOJIS at the start of every explanation line.\n"
        "4. DO NOT use technical words like 'variable' or 'function'. Instead use 'box', 'label', 'robot', or 'recipe'.\n\n"
        "### STRICT RESPONSE FORMAT\n"
        "(Output ONLY these two sections. No intro text like 'Here is the code'.)\n\n"
        "### The Code\n"
        "```python\n"
        "# code here\n"
        "```\n\n"
        "### Explanation\n"
        "- 🎨 **Line 1**: `code` - Simple explanation with analogy.\n"
        "- 🚀 **Line 2**: `code` - Simple explanation with analogy.\n"
    )

    try:
        if not settings.GROQ_API_KEY:
            return "Config Error: GROQ_API_KEY is missing.", "# Please check .env or Render settings."
        
        logging.info(f"Sending query to Groq Cloud ({GROQ_MODEL})...")
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": prompt_text,
                }
            ],
            model=GROQ_MODEL,
            temperature=0.3, # Low temp keeps the formatting strict
        )
        full_output = completion.choices[0].message.content

        # Cleanup: Code Extraction Regex
        code_pattern = r"```(?:python)?\s*(.*?)\s*```"
        code_matches = re.findall(code_pattern, full_output, re.DOTALL)
        
        if code_matches:
            code_content = "\n\n".join(code_matches).strip()
            # Remove the code block and headers to get clean explanation text
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
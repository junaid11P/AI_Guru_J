import logging
import re
from groq import Groq
from google import genai
from app.config import settings

logging.basicConfig(level=logging.INFO)

def get_ai_explanation(user_input: str, is_audio=False):
    """
    Sends user input to the configured LLM (Gemini or Groq) and returns:
    - explanation_text
    - code_block
    """
    prompt_text = f"""
You are a friendly Python Tutor who explains to beginners and kids.

The user asked:
"{user_input}"

Your task:

1. Write valid Python code to solve the user's question.
2. Put ONLY the code inside a markdown block:
```python
# code here
```

Then explain the code line-by-line as a bullet list.

Each bullet MUST follow this format:

Line X: actual code - simple explanation.

Use very simple English (3rd grade level).

Do not add any intro or outro text.

At the end, show the exact OUTPUT of the code.
"""

    provider = settings.LLM_PROVIDER.lower()
    model_id = settings.NLP_MODEL_ID

    try:
        if provider == "groq" and "gemini" in model_id.lower():
            logging.warning(f"Likely configuration error: Using Gemini model '{model_id}' with Groq provider.")
            return "Configuration Error: Gemini models are not supported on Groq.", "# Update LLM_PROVIDER to 'gemini' or NLP_MODEL_ID to a Groq model (e.g., llama-3.1-8b-instant)"

        if provider == "gemini":
            if not settings.GEMINI_API_KEY:
                return ("Config Error: GEMINI_API_KEY missing.",
                        "# Set GEMINI_API_KEY in your .env or Render Dashboard")
            
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            logging.info(f"Sending NLP request to Gemini model={model_id}")
            
            response = client.models.generate_content(model=model_id, contents=prompt_text)
            ai_output = response.text

        elif provider == "groq":
            if not settings.GROQ_API_KEY:
                return ("Config Error: GROQ_API_KEY missing.",
                        "# Set GROQ_API_KEY in your .env or Render Dashboard")

            client = Groq(api_key=settings.GROQ_API_KEY)
            logging.info(f"Sending NLP request to Groq model={model_id}")

            completion = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt_text}],
                temperature=0.3
            )
            ai_output = completion.choices[0].message.content
        
        else:
            return f"Unsupported provider: {provider}", "# Configuration Error"

        # Extract code block
        code_pattern = r"```(?:python)?\s*(.*?)\s*```"
        code_blocks = re.findall(code_pattern, ai_output, flags=re.DOTALL)
        code_block = code_blocks[0].strip() if code_blocks else "# No Python code found."

        # Remove code block from explanation
        explanation_text = re.sub(code_pattern, "", ai_output, flags=re.DOTALL).strip()

        return explanation_text, code_block

    except Exception as e:
        logging.error(f"NLP Engine Error: {e}")
        return "Error generating explanation.", f"# Error: {str(e)}"

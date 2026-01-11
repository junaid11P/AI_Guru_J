from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str | None = None
    MONGODB_URI: str = "mongodb://localhost:27017/ai_guru_j_db"

    # UPDATED: Use the model explicitly listed in your terminal
    NLP_MODEL_ID: str = "gemini-2.5-flash"

    MAX_TOKENS: int = 1024
    
    # Provider: 'groq' (Cloud/Render)
    LLM_PROVIDER: str = "groq" 
    GROQ_API_KEY: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
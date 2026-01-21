from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017/ai_guru_j_db"

    NLP_MODEL_ID: str = "llama-3.1-8b-instant"

    MAX_TOKENS: int = 1024

    LLM_PROVIDER: str = "groq" 
    GROQ_API_KEY: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
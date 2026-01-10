from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # API KEYS
    GEMINI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None

    # UPDATED: Use the model explicitly listed in your terminal
    NLP_MODEL_ID: str = "gemini-1.5-flash"
    MAX_TOKENS: int = 1024
    
    # Provider: 'groq' (Cloud/Render)
    LLM_PROVIDER: str = "groq"

    # Database
    MONGODB_URI: str = "mongodb://localhost:27017/ai_guru_j_db"

    # Audio & Lip Sync Paths
    TEMP_DIR: str = "/tmp"
    FFPROBE_PATH: str = "ffprobe"
    FFMPEG_PATH: str = "ffmpeg"

    # Rhubarb Lip Sync
    RHUBARB_BINARY: str = "rhubarb"
    RHUBARB_FORMAT: str = "json"

    # Server config
    BASE_URL: str = os.getenv("RENDER_EXTERNAL_URL", "http://127.0.0.1:8000")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys & Secrets
    OPENAI_API_KEY: str = "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"
    MONGODB_URI: str = "mongodb://localhost:27017" # Default fallback

    # AI Model Configuration
    NLP_MODEL_ID: str = "google/flan-t5-base"

    class Config:
        env_file = ".env" # Loads variables from .env file

settings = Settings()
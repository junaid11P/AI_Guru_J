from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys & Secrets
    OPENAI_API_KEY: str = "placeholder_key"
    MONGODB_URI: str = "mongodb://localhost:27017" # Default fallback

    # AI Model Configuration
    NLP_MODEL_ID: str = "google/flan-t5-base"

    class Config:
        env_file = ".env" # Loads variables from .env file

settings = Settings()
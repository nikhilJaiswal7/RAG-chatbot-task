import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    QDRANT_URL: str = ":memory:" # Use in-memory for dev as requested
    
    class Config:
        env_file = ".env"

settings = Settings()

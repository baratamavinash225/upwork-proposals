from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    # Upwork API Credentials
    UPWORK_CLIENT_ID: str
    UPWORK_CLIENT_SECRET: str
    UPWORK_REDIRECT_URI: str = "http://localhost:8080"
    
    # AI & Messaging
    GOOGLE_API_KEY: str  # For Gemini
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_WHATSAPP_NUMBER: str
    MY_WHATSAPP_NUMBER: str
    
    # Project Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    RESUME_PATH: str = str(BASE_DIR / "Avinash_SDE.pdf")
    
    # State Management
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
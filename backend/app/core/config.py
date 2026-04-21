from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = (BASE_DIR / "capitalmax.db").as_posix()

class Settings(BaseSettings):
    PROJECT_NAME: str = "ChatMax Omnichannel Backend"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{DEFAULT_SQLITE_PATH}" # Using SQLite for local dev, replace with PG URI in prod
    
    # WhatsApp API Config
    WHATSAPP_TOKEN: str = "YOUR_WHATSAPP_ACCESS_TOKEN"
    WHATSAPP_VERIFY_TOKEN: str = "YOUR_CUSTOM_VERIFY_TOKEN"
    WHATSAPP_PHONE_ID: str = "YOUR_WHATSAPP_PHONE_NUMBER_ID"

    # Language Detection & Guardrails
    # These can be comma-separated strings in .env, Pydantic will convert to list
    NE_ROM_KEYWORDS: list[str] = ["kasto", "kasari", "laagi", "chha", "ho", "bhayeko", "garnu", "pane", "ko", "ma"]
    GUARDRAIL_KEYWORDS: list[str] = ["urgent", "emergency", "human", "talk to person", "complaint", "fraud"]
    
    # Profanity Guardrails
    PROFANITY_KEYWORDS: list[str] = ["badword1", "badword2", "spam", "scam"] # Placeholder: User can fill in .env
    PROFANITY_RESPONSE: str = "Please maintain professional language. Your message has been flagged."

    # NLU Model Settings
    # Lower value (e.g., 0.6) makes the bot more "brave" but increases false positives.
    # Higher value (e.g., 0.8) makes it more "conservative" and triggers fallback more often.
    NLU_THRESHOLD: float = 0.68

    class Config:
        env_file = ".env"

settings = Settings()

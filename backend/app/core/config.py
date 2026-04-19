from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ChatMax Omnichannel Backend"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./capitalmax.db" # Using SQLite for local dev, replace with PG URI in prod
    
    # WhatsApp API Config
    WHATSAPP_TOKEN: str = "YOUR_WHATSAPP_ACCESS_TOKEN"
    WHATSAPP_VERIFY_TOKEN: str = "YOUR_CUSTOM_VERIFY_TOKEN"
    WHATSAPP_PHONE_ID: str = "YOUR_WHATSAPP_PHONE_NUMBER_ID"

    class Config:
        env_file = ".env"

settings = Settings()
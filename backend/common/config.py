import os
from dotenv import load_dotenv

load_dotenv()  # loads .env at app startup


class Settings:
    # App
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")

    # FastAPI
    FASTAPI_HOST = os.getenv("FASTAPI_HOST", "127.0.0.1")
    FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))

    # Flask
    FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))

    # Jobs
    PRICING_TIMEZONE = os.getenv("PRICING_TIMEZONE", "UTC")

    # ML
    MODEL_DIR = os.getenv("MODEL_DIR", "models/")
    ACTIVE_MODEL_VERSION = os.getenv("ACTIVE_MODEL_VERSION", "latest")


settings = Settings()

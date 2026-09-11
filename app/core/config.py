from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str
    ENV: str = "development"
    SUPABASE_URL: str = ""
    SUPABASE_PUBL_KEY: str = ""
    SUPABASE_SECRET_KEY: str = ""

    SECRET_KEY: str = "ecobite-super-secret-key-change-in-production-32-chars-min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite / React dev server
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # Next.js / Create React App
    ]

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    groq_api_key: str
    news_api_key: str | None = None

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"


settings = Settings()

import os
import urllib.parse
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "community_food_rescue"

    SECRET_KEY: str = "food_rescue_network_local_secure_secret_key_2026_jwt"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    PORT: int = 5000
    HOST: str = "127.0.0.1"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Hosted Gemma AI Configuration
    GEMMA_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMMA_MODEL: str = "gemma-4-26b-a4b-it"

    @property
    def ai_api_key(self) -> Optional[str]:
        return self.GEMMA_API_KEY or self.GEMINI_API_KEY or os.getenv("GEMMA_API_KEY") or os.getenv("GEMINI_API_KEY")

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        encoded_password = urllib.parse.quote_plus(self.DB_PASSWORD) if self.DB_PASSWORD else ""
        auth = f"{self.DB_USER}:{encoded_password}" if encoded_password else self.DB_USER
        return f"mysql+pymysql://{auth}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    @property
    def server_database_url(self) -> str:
        # URL without database name, used to create database if not exists
        encoded_password = urllib.parse.quote_plus(self.DB_PASSWORD) if self.DB_PASSWORD else ""
        auth = f"{self.DB_USER}:{encoded_password}" if encoded_password else self.DB_USER
        return f"mysql+pymysql://{auth}@{self.DB_HOST}:{self.DB_PORT}/?charset=utf8mb4"

settings = Settings()


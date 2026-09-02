from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "LexiMini AI Gateway"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super-secret-leximini-jwt-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    DATABASE_URL: str = "postgresql+asyncpg://leximini:leximini_pass@postgres:5432/leximinidb"
    REDIS_URL: str = "redis://redis:6379/0"
    RAG_SERVICE_URL: str = "http://rag_engine:8001"
    MODEL_SERVER_URL: str = "http://model_server:8002"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

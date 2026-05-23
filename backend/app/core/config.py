from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    postgres_url: str = Field(alias="POSTGRES_URL")
    redis_url: str = Field(alias="REDIS_URL")
    rabbitmq_url: str = Field(alias="RABBITMQ_URL")
    jwt_secret: str = Field(alias="JWT_SECRET")
    internal_ingest_secret: str = Field(alias="INTERNAL_INGEST_SECRET")
    jwt_expiry_hours: int = 24
    app_name: str = "TraceMind"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

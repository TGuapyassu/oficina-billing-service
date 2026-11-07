from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = Field(default="sqlite:///:memory:", validation_alias="DATABASE_URL")
    mongodb_url: str = Field(default="", validation_alias="MONGODB_URL")
    rabbitmq_url: str = Field(default="", validation_alias="RABBITMQ_URL")
    os_service_url: str = Field(default="http://localhost:8001", validation_alias="OS_SERVICE_URL")
    internal_service_key: str = Field(default="dev-internal-key", validation_alias="INTERNAL_SERVICE_KEY")
    mp_access_token: str = Field(default="", validation_alias="MP_ACCESS_TOKEN")
    mp_webhook_secret: str = Field(default="", validation_alias="MP_WEBHOOK_SECRET")
    public_base_url: str = Field(default="http://localhost:8003", validation_alias="PUBLIC_BASE_URL")


@lru_cache
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    environment: str = "development"
    database_url: str = "postgresql+psycopg://ivoirex:ivoirex@postgres:5432/ivoirex"
    jwt_secret: SecretStr = SecretStr("development-only-change-me-32-bytes")
    jwt_access_minutes: int = 15
    jwt_refresh_days: int = 14
    cors_origins: str = "http://localhost:43100"
    redis_url: str = "redis://redis:6379/0"
    trusted_proxy_ips: str = ""
    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def trusted_proxy_addresses(self) -> frozenset[str]:
        return frozenset(address.strip() for address in self.trusted_proxy_ips.split(",") if address.strip())

    @field_validator("jwt_secret")
    @classmethod
    def require_secret_in_production(cls, value, info):
        if info.data.get("environment") == "production" and len(value.get_secret_value()) < 32:
            raise ValueError("JWT_SECRET must contain at least 32 characters in production")
        return value
@lru_cache
def get_settings() -> Settings:
    return Settings()
settings = get_settings()

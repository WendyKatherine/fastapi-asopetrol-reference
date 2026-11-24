"""Application configuration.

All values are loaded from the environment (or a local .env file).
Secrets are NEVER hardcoded: `database_url` and `jwt_secret` have no
defaults, so the app refuses to boot without them.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "fastapi-asopetrol-reference"
    environment: str = Field(default="local")
    debug: bool = Field(default=False)


@lru_cache
def get_settings() -> Settings:
    """Cached singleton so config is parsed once per process."""
    return Settings()

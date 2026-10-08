"""Application configuration, loaded from environment variables (prefix ``PQ_``)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PQ_", env_file=".env", extra="ignore")

    environment: str = "local"

    # Classifier confidence below which the type is marked uncertain and the
    # request is routed for manual triage.
    min_confidence: float = 0.45


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

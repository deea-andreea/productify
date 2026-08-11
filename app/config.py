"""
App settings, loaded from the repo-root .env. Also owns the shared
image-call counter — gpt-image-1 calls are the expensive ones and there is
one shared spend cap for the whole team.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    OPENAI_API_KEY: str = ""
    MOCK: bool = True
    MAX_IMAGE_CALLS: int = 40
    OUT_DIR: str = "out/pitches"


settings = Settings()

_image_calls_used = 0


def can_call_image() -> bool:
    return _image_calls_used < settings.MAX_IMAGE_CALLS


def record_image_call() -> None:
    global _image_calls_used
    _image_calls_used += 1


def image_calls_used() -> int:
    return _image_calls_used


def image_calls_remaining() -> int:
    return max(0, settings.MAX_IMAGE_CALLS - _image_calls_used)

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Core API ---
    API_KEY: str

    # --- Database ---
    DATABASE_URL: str

    # --- Redis / Celery ---
    REDIS_URL: str
    CELERY_TASK_ALWAYS_EAGER: bool = True

    # --- Storage ---
    CHROMA_PATH: str = "./chroma_db"

    # --- Models ---
    WHISPER_MODEL: str = "medium"

    # --- LLM Keys ---
    GEMINI_API_KEY: str
    GROQ_API_KEY: str | None = None  # optional fallback

    # --- Pydantic Config ---
    model_config = SettingsConfigDict(
        env_file=".env",          # used only locally
        env_file_encoding="utf-8",
        extra="ignore"            # ignore unknown env vars
    )


# Create a single settings instance
settings = Settings()


# --- DEBUG (remove after testing) ---
print("🚀 CONFIG LOADED")
print("GEMINI_API_KEY:", settings.GEMINI_API_KEY[:10] if settings.GEMINI_API_KEY else None)
print("DATABASE_URL:", "SET" if settings.DATABASE_URL else "MISSING")
print("REDIS_URL:", "SET" if settings.REDIS_URL else "MISSING")
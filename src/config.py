from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Auth
    API_KEY: str

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/callcenter"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379"
    CELERY_TASK_ALWAYS_EAGER: bool = True   # sync mode for hackathon

    # AI Models
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""        # for Whisper API fallback
    WHISPER_MODEL: str = "medium"   # fallbacks if GPU available
    USE_WHISPER_API: bool = False   # True = use OpenAI API, False = local

    # Vector Store
    CHROMA_PATH: str = "./chroma_db"

    class Config:
        env_file = ".env"

settings = Settings()

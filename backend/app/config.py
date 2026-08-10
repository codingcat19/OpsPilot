from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://opspilot:opspilot_secret@localhost:5432/opspilot"
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    AI_PROVIDER: str = "ollama"
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    @model_validator(mode="after")
    def _validate_jwt_secret(self) -> "Settings":
        if not self.JWT_SECRET or self.JWT_SECRET == "change-me-in-production":
            raise ValueError("JWT_SECRET must be set via env to a secure random string")
        return self

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

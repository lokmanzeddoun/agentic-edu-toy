from pathlib import Path

from pydantic import BaseModel
from dotenv import load_dotenv


def load_environment() -> Path:
    """Load environment variables from the project root .env file if present."""
    env_path = Path(".env")
    load_dotenv(env_path if env_path.exists() else None)
    return env_path


class Settings(BaseModel):
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    use_llm: bool = True

    @property
    def llm_enabled(self) -> bool:
        return self.use_llm and bool(self.openai_api_key)


def get_settings() -> Settings:
    load_environment()
    from os import getenv

    return Settings(
        openai_api_key=getenv("OPENAI_API_KEY"),
        openai_model=getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        use_llm=getenv("AGENTIC_USE_LLM", "true").strip().lower() in {"1", "true", "yes", "on"},
    )

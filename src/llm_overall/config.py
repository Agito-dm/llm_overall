import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    base_url: str | None = None


def load_settings() -> Settings:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "").strip()
    base_url = os.getenv("OPENAI_BASE_URL", "").strip()

    if not api_key or api_key == "your_api_key_here":
        raise ValueError("OPENAI_API_KEY is not configured in .env")

    if not model or model == "your_model_name":
        raise ValueError("OPENAI_MODEL is not configured in .env")

    return Settings(
        api_key=api_key,
        model=model,
        base_url=base_url or None,
    )

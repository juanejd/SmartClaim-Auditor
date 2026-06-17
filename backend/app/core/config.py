import os

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_APP_DIR = Path(__file__).resolve().parent.parent

COMPLAINT_TEXT_MIN_LENGTH: int = 10
CLASSIFIER_THRESHOLD: float = 0.7

RAG_CHUNK_SIZE: int = 2048
RAG_CHUNK_OVERLAP: int = 800
RAG_TOP_K: int = 4
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

DATA_DIR: str = str(_APP_DIR / "data")
FAISS_INDEX_PATH: str = str(_APP_DIR / "data" / "index")
METADATA_PATH: str = str(_APP_DIR / "data" / "index" / "metadata.json")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    AUDIT_LLM_PROVIDER: str = "groq"
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_API_KEY: str | None = None

    AUDIT_ANALYST_TEMPERATURE: float = 0.2
    AUDIT_AUDITOR_TEMPERATURE: float = 0.0

    AUDIT_MAX_TOKENS: int = 512

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:1.5b"


settings = Settings()

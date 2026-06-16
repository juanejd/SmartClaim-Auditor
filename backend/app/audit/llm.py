from langchain_core.language_models import BaseChatModel

from app.core.config import settings

_models: dict[float, BaseChatModel] = {}


def get_audit_llm(temperature: float) -> BaseChatModel:
    if temperature not in _models:
        _models[temperature] = _build_model(temperature)
    return _models[temperature]


def _build_model(temperature: float) -> BaseChatModel:
    provider = settings.AUDIT_LLM_PROVIDER

    if provider == "groq":
        if not settings.GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is required when AUDIT_LLM_PROVIDER='groq'. "
                "Set it in the environment or in a .env file."
            )
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=temperature,
            max_tokens=settings.AUDIT_MAX_TOKENS,
            api_key=settings.GROQ_API_KEY,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=temperature,
            num_predict=settings.AUDIT_MAX_TOKENS,
        )

    raise ValueError(
        f"Unknown AUDIT_LLM_PROVIDER: {provider!r}. Supported values: 'groq', 'ollama'."
    )


def reset_audit_llm() -> None:
    _models.clear()

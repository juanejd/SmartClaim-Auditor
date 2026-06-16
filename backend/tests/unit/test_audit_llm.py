"""Unit tests for the provider-agnostic LLM factory in audit/llm.py.

All tests run without real network calls. The factory and its singletons are
exercised by monkeypatching settings fields and clearing the _models cache via
the autouse fixture — mirrors the pattern in test_classifier.py.
"""

import pytest
import app.audit.llm as llm_module
from app.audit.llm import get_audit_llm, reset_audit_llm


@pytest.fixture(autouse=True)
def reset_llm_singleton():
    """Mirror of test_classifier.py autouse fixture.

    Saves the current _models dict, clears it before each test, yields,
    then restores it. Ensures singleton state does not leak across tests.
    """
    original = llm_module._models.copy()
    llm_module._models.clear()
    yield
    llm_module._models.clear()
    llm_module._models.update(original)


def test_factory_returns_chat_groq(monkeypatch):
    """When provider='groq' and a key is set, factory returns a ChatGroq instance."""
    from langchain_groq import ChatGroq

    monkeypatch.setattr("app.audit.llm.settings.AUDIT_LLM_PROVIDER", "groq")
    monkeypatch.setattr("app.audit.llm.settings.GROQ_API_KEY", "dummy-key")
    monkeypatch.setattr("app.audit.llm.settings.GROQ_MODEL", "llama-3.1-8b-instant")
    monkeypatch.setattr("app.audit.llm.settings.AUDIT_MAX_TOKENS", 512)

    result = get_audit_llm(0.0)

    assert isinstance(result, ChatGroq)


def test_factory_returns_chat_ollama(monkeypatch):
    """When provider='ollama', factory returns a ChatOllama instance."""
    pytest.importorskip("langchain_ollama", reason="langchain-ollama not installed")
    from langchain_ollama import ChatOllama

    monkeypatch.setattr("app.audit.llm.settings.AUDIT_LLM_PROVIDER", "ollama")
    monkeypatch.setattr("app.audit.llm.settings.OLLAMA_MODEL", "qwen2.5:1.5b")
    monkeypatch.setattr("app.audit.llm.settings.OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setattr("app.audit.llm.settings.AUDIT_MAX_TOKENS", 512)

    result = get_audit_llm(0.0)

    assert isinstance(result, ChatOllama)


def test_factory_missing_groq_key_raises(monkeypatch):
    """When provider='groq' and GROQ_API_KEY is None, RuntimeError is raised immediately."""
    monkeypatch.setattr("app.audit.llm.settings.AUDIT_LLM_PROVIDER", "groq")
    monkeypatch.setattr("app.audit.llm.settings.GROQ_API_KEY", None)

    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        get_audit_llm(0.0)


def test_factory_unknown_provider_raises(monkeypatch):
    """When AUDIT_LLM_PROVIDER is an unknown string, ValueError is raised."""
    monkeypatch.setattr("app.audit.llm.settings.AUDIT_LLM_PROVIDER", "unknown_provider")

    with pytest.raises(ValueError, match="unknown_provider"):
        get_audit_llm(0.0)


def test_factory_caches_per_temperature(monkeypatch):
    """Two calls with the same temperature return the identical cached object."""
    monkeypatch.setattr("app.audit.llm.settings.AUDIT_LLM_PROVIDER", "groq")
    monkeypatch.setattr("app.audit.llm.settings.GROQ_API_KEY", "dummy-key")
    monkeypatch.setattr("app.audit.llm.settings.GROQ_MODEL", "llama-3.1-8b-instant")
    monkeypatch.setattr("app.audit.llm.settings.AUDIT_MAX_TOKENS", 512)

    first = get_audit_llm(0.0)
    second = get_audit_llm(0.0)

    assert first is second


def test_factory_different_temperatures_are_separate_instances(monkeypatch):
    """Different temperatures produce different cached objects (analyst vs auditor)."""
    monkeypatch.setattr("app.audit.llm.settings.AUDIT_LLM_PROVIDER", "groq")
    monkeypatch.setattr("app.audit.llm.settings.GROQ_API_KEY", "dummy-key")
    monkeypatch.setattr("app.audit.llm.settings.GROQ_MODEL", "llama-3.1-8b-instant")
    monkeypatch.setattr("app.audit.llm.settings.AUDIT_MAX_TOKENS", 512)

    analyst_llm = get_audit_llm(0.2)
    auditor_llm = get_audit_llm(0.0)

    assert analyst_llm is not auditor_llm


def test_reset_clears_cache(monkeypatch):
    """reset_audit_llm() clears the per-temperature cache; next call builds a new object."""
    monkeypatch.setattr("app.audit.llm.settings.AUDIT_LLM_PROVIDER", "groq")
    monkeypatch.setattr("app.audit.llm.settings.GROQ_API_KEY", "dummy-key")
    monkeypatch.setattr("app.audit.llm.settings.GROQ_MODEL", "llama-3.1-8b-instant")
    monkeypatch.setattr("app.audit.llm.settings.AUDIT_MAX_TOKENS", 512)

    first = get_audit_llm(0.0)
    reset_audit_llm()
    second = get_audit_llm(0.0)

    assert first is not second

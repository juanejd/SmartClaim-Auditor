from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from app.audit.llm import get_audit_llm
from app.audit.state import AnalystOutput, AuditState, AuditorOutput
from app.core.config import settings

logger = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

_prompt_cache: dict[str, str] = {}


def _load_prompt(name: str) -> str:
    if name not in _prompt_cache:
        path = _PROMPTS_DIR / f"{name}.yaml"
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        _prompt_cache[name] = data["template"]
    return _prompt_cache[name]


def _render(template: str, **vars: Any) -> str:
    return template.format_map(vars)


def _join(chunks: list[str]) -> str:
    if not chunks:
        return "(no evidence retrieved)"
    return "\n".join(chunks)


def node_analyst(state: AuditState) -> dict:
    """Node 1 — Analyst: produce a draft verdict grounded in the evidence.

    Temperature: AUDIT_ANALYST_TEMPERATURE (default 0.2).
    Writes: draft_verdict, draft_justification.
    Does NOT write: corrections_applied, final_verdict, final_justification, rag_citation.
    """
    llm = get_audit_llm(settings.AUDIT_ANALYST_TEMPERATURE).with_structured_output(
        AnalystOutput
    )
    prompt = _render(
        _load_prompt("analyst"),
        complaint_text=state["complaint_text"],
        contract_clauses=state["contract_clauses"] or "(no se proporcionaron cláusulas)",
        rag_chunks=_join(state["rag_chunks"]),
    )
    out: AnalystOutput = llm.invoke(prompt)
    return {
        "draft_verdict": out.draft_verdict,
        "draft_justification": out.draft_justification,
    }


def node_auditor(state: AuditState) -> dict:
    """Node 2 — Auditor: verify and ground the analyst's draft.

    Temperature: AUDIT_AUDITOR_TEMPERATURE (default 0.0 — deterministic).
    Reads: all input fields + analyst's draft fields from state.
    Writes: corrections_applied, final_verdict, final_justification, rag_citation.
    """
    llm = get_audit_llm(settings.AUDIT_AUDITOR_TEMPERATURE).with_structured_output(
        AuditorOutput
    )
    prompt = _render(
        _load_prompt("auditor"),
        complaint_text=state["complaint_text"],
        contract_clauses=state["contract_clauses"] or "(no se proporcionaron cláusulas)",
        rag_chunks=_join(state["rag_chunks"]),
        draft_verdict=state["draft_verdict"],
        draft_justification=state["draft_justification"],
    )
    out: AuditorOutput = llm.invoke(prompt)
    return {
        "corrections_applied": out.corrections_applied,
        "final_verdict": out.final_verdict,
        "final_justification": out.final_justification,
        "rag_citation": out.rag_citation,
    }

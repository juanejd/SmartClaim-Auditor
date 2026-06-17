from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.audit.nodes import node_analyst, node_auditor
from app.audit.state import AuditState

logger = logging.getLogger(__name__)

_compiled: Any = None


def _build_graph():
    g = StateGraph(AuditState)
    g.add_node("analyst", node_analyst)
    g.add_node("auditor", node_auditor)
    g.add_edge(START, "analyst")
    g.add_edge("analyst", "auditor")
    g.add_edge("auditor", END)
    return g.compile()


def _get_graph():
    global _compiled
    if _compiled is None:
        _compiled = _build_graph()
    return _compiled


def _verify_citation(citation: str, chunks: list[str]) -> bool:

    if not citation:
        return False
    return any(citation in chunk for chunk in chunks)


def run_audit(
    *,
    complaint_text: str,
    contract_clauses: str | None,
    rag_chunks: list[str],
) -> dict:
    init: AuditState = {
        "complaint_text": complaint_text,
        "contract_clauses": contract_clauses,
        "rag_chunks": rag_chunks,
        "draft_verdict": "INSPECTION_REQUIRED",
        "draft_justification": "",
        "corrections_applied": False,
        "final_verdict": "INSPECTION_REQUIRED",
        "final_justification": "",
        "rag_citation": "",
    }
    result: dict = dict(_get_graph().invoke(init))

    citation = result.get("rag_citation", "")
    sources = [*rag_chunks, contract_clauses or ""]
    if not _verify_citation(citation, sources):
        _CITATION_LOG_MAX = 40
        citation_preview = (
            citation[:_CITATION_LOG_MAX] + "..."
            if len(citation) > _CITATION_LOG_MAX
            else citation
        )
        logger.warning(
            "audit faithfulness failure: rag_citation (first %d chars: %r) "
            "is not verbatim in the evidence or contract clauses; downgrading final_verdict to INSPECTION_REQUIRED",
            _CITATION_LOG_MAX,
            citation_preview,
        )
        result["final_verdict"] = "INSPECTION_REQUIRED"

    return result

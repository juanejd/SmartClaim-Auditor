"""Unit tests for AuditState TypedDict and per-node structured-output schemas.

Tests follow RED phase: they are written before the implementation exists.
"""

import pytest
from pydantic import ValidationError

from app.audit.state import AuditState, AnalystOutput, AuditorOutput


def test_audit_state_has_all_fields():
    """AuditState TypedDict accepts all 9 defined fields without KeyError."""
    state: AuditState = {
        "complaint_text": "The product broke after 2 days.",
        "contract_clauses": "Article 5: warranty covers manufacturing defects.",
        "rag_chunks": ["chunk one", "chunk two"],
        "draft_verdict": "APPROVED",
        "draft_justification": "Defect covered by warranty.",
        "corrections_applied": False,
        "final_verdict": "APPROVED",
        "final_justification": "Evidence confirms manufacturing defect.",
        "rag_citation": "warranty covers manufacturing defects",
    }
    # Access every field to confirm no KeyError
    assert state["complaint_text"] == "The product broke after 2 days."
    assert state["contract_clauses"] == "Article 5: warranty covers manufacturing defects."
    assert state["rag_chunks"] == ["chunk one", "chunk two"]
    assert state["draft_verdict"] == "APPROVED"
    assert state["draft_justification"] == "Defect covered by warranty."
    assert state["corrections_applied"] is False
    assert state["final_verdict"] == "APPROVED"
    assert state["final_justification"] == "Evidence confirms manufacturing defect."
    assert state["rag_citation"] == "warranty covers manufacturing defects"


def test_verdict_literal_rejects_invalid():
    """AnalystOutput raises ValidationError when draft_verdict is not in the 3-value enum."""
    with pytest.raises(ValidationError):
        AnalystOutput(draft_verdict="UNKNOWN", draft_justification="some justification")


def test_analyst_output_rejects_empty_justification():
    """AnalystOutput enforces min_length=1 on draft_justification."""
    with pytest.raises(ValidationError):
        AnalystOutput(draft_verdict="APPROVED", draft_justification="")


def test_auditor_output_rejects_empty_citation():
    """AuditorOutput enforces min_length=1 on rag_citation."""
    with pytest.raises(ValidationError):
        AuditorOutput(
            corrections_applied=False,
            final_verdict="APPROVED",
            final_justification="Confirmed by evidence.",
            rag_citation="",
        )


def test_auditor_output_rejects_invalid_verdict():
    """AuditorOutput raises ValidationError when final_verdict is not in the 3-value enum."""
    with pytest.raises(ValidationError):
        AuditorOutput(
            corrections_applied=False,
            final_verdict="INVALID",  # type: ignore[arg-type]
            final_justification="Confirmed by evidence.",
            rag_citation="compressor failures covered for 12 months",
        )


def test_auditor_output_rejects_empty_justification():
    """AuditorOutput enforces min_length=1 on final_justification."""
    with pytest.raises(ValidationError):
        AuditorOutput(
            corrections_applied=False,
            final_verdict="APPROVED",
            final_justification="",
            rag_citation="compressor failures covered for 12 months",
        )

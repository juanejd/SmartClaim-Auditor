"""Unit tests for ClaimRead audit field exposure (RF-04).

Spec: Audit Fields in ClaimRead — draft AND final must be separate top-level
nullable fields; rag_chunks must NOT be exposed.
"""

from datetime import datetime, timezone

from app.models.claim import ClaimRead


_BASE = {
    "claim_id": "abc-123",
    "complaint_text": "The product broke.",
    "contract_clauses": "Clause 1: 12-month warranty.",
    "status": "AUDITED",
    "intent_label": "MECHANICAL_FAILURE",
    "confidence": 0.9,
    "received_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
}

_AUDIT_FIELDS = {
    "draft_verdict": "APPROVED",
    "draft_justification": "Draft justification text.",
    "corrections_applied": False,
    "final_verdict": "APPROVED",
    "final_justification": "Final justification text.",
    "rag_citation": "Product broke after 3 months.",
}


def test_claim_read_exposes_all_6_audit_fields():
    claim = ClaimRead(**_BASE, **_AUDIT_FIELDS)
    assert claim.draft_verdict == "APPROVED"
    assert claim.draft_justification == "Draft justification text."
    assert claim.corrections_applied is False
    assert claim.final_verdict == "APPROVED"
    assert claim.final_justification == "Final justification text."
    assert claim.rag_citation == "Product broke after 3 months."


def test_claim_read_audit_fields_nullable():
    """ClaimRead must accept None for all 6 audit fields without raising."""
    claim = ClaimRead(
        **_BASE,
        draft_verdict=None,
        draft_justification=None,
        corrections_applied=None,
        final_verdict=None,
        final_justification=None,
        rag_citation=None,
    )
    assert claim.draft_verdict is None
    assert claim.final_verdict is None
    assert claim.rag_citation is None


def test_claim_read_draft_verdict_and_final_verdict_are_distinct():
    """draft_verdict and final_verdict must be separate model fields — not aliased."""
    claim = ClaimRead(
        **_BASE,
        draft_verdict="REJECTED",
        final_verdict="INSPECTION_REQUIRED",
        draft_justification="draft reason",
        corrections_applied=True,
        final_justification="auditor corrected",
        rag_citation="some verbatim text",
    )
    # Both must be present and hold distinct values
    assert "draft_verdict" in ClaimRead.model_fields
    assert "final_verdict" in ClaimRead.model_fields
    assert claim.draft_verdict == "REJECTED"
    assert claim.final_verdict == "INSPECTION_REQUIRED"


def test_claim_read_includes_rag_chunks():
    """rag_chunks is now exposed in ClaimRead so the frontend can display evidence."""
    assert "rag_chunks" in ClaimRead.model_fields

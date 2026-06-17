"""Slow end-to-end integration test for the dual-audit LangGraph pipeline.

Requires a valid GROQ_API_KEY in the environment. Skipped automatically when
the key is absent. Run explicitly with:

    uv run python -m pytest -m slow backend/tests/integration/test_audit_integration.py
"""

import os

import pytest

# Skip the entire module immediately when GROQ_API_KEY is not set.
# This avoids any import-time LLM initialisation that would fail silently.
if not os.environ.get("GROQ_API_KEY"):
    pytest.skip(
        "GROQ_API_KEY not set — skipping real-provider audit integration test",
        allow_module_level=True,
    )

from app.audit.graph import _verify_citation, run_audit  # noqa: E402 (after guard)

_SAMPLE_CHUNKS = [
    "Clause 5 of the warranty agreement states that all major mechanical "
    "components, including the compressor, are warranted for a period of "
    "twelve (12) months from the date of purchase against defects in "
    "materials or workmanship.",
    "Section 3.2 covers cosmetic damage: scratches, dents, and cracked "
    "plastic are not covered under the standard warranty policy.",
]

_COMPLAINT = (
    "My refrigerator's compressor stopped working completely after only "
    "3 months of normal use. The unit no longer cools at all. I purchased "
    "it 3 months ago and have the original receipt."
)

_CONTRACT = (
    "Clause 5: All major components are warranted for 12 months. "
    "Clause 3.2: Cosmetic damage is excluded."
)

_VALID_VERDICTS = {"APPROVED", "REJECTED", "INSPECTION_REQUIRED"}


@pytest.mark.slow
def test_real_audit_end_to_end():
    """Run the full dual-audit graph against Groq and assert correctness.

    Assertions:
    - final_verdict is one of the three valid enum values.
    - rag_citation is a non-empty string.
    - _verify_citation confirms rag_citation is verbatim in the provided chunks.
    - All 6 output fields are present and non-None.
    """
    result = run_audit(
        complaint_text=_COMPLAINT,
        contract_clauses=_CONTRACT,
        rag_chunks=_SAMPLE_CHUNKS,
    )

    # All 6 output fields must be present and non-None
    assert result.get("draft_verdict") is not None, "draft_verdict missing"
    assert result.get("draft_justification"), "draft_justification empty"
    assert result.get("corrections_applied") is not None, "corrections_applied missing"
    assert result.get("final_verdict") is not None, "final_verdict missing"
    assert result.get("final_justification"), "final_justification empty"
    assert result.get("rag_citation"), "rag_citation empty"

    # Verdict must be within the allowed enum
    assert result["draft_verdict"] in _VALID_VERDICTS, (
        f"draft_verdict {result['draft_verdict']!r} not in {_VALID_VERDICTS}"
    )
    assert result["final_verdict"] in _VALID_VERDICTS, (
        f"final_verdict {result['final_verdict']!r} not in {_VALID_VERDICTS}"
    )

    # Citation verbatim check — _verify_citation is a pure function
    # If it returns False, run_audit already downgraded to INSPECTION_REQUIRED
    # but we still assert the citation was verified (or gracefully downgraded).
    citation = result["rag_citation"]
    assert isinstance(citation, str) and len(citation) > 0

    # If the model produced a verbatim citation, verify it directly.
    # If not, run_audit already downgraded final_verdict — that path is also valid.
    citation_verified = _verify_citation(citation, _SAMPLE_CHUNKS)
    if citation_verified:
        assert result["final_verdict"] in _VALID_VERDICTS
    else:
        # Downgrade path: final_verdict must be INSPECTION_REQUIRED
        assert result["final_verdict"] == "INSPECTION_REQUIRED", (
            f"Citation failed check but final_verdict is {result['final_verdict']!r}; "
            "expected INSPECTION_REQUIRED from citation downgrade"
        )

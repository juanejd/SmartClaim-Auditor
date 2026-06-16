"""Unit tests for node_analyst and node_auditor in audit/nodes.py.

All tests use a mocked LLM — zero real network calls. The mock is injected by
patching get_audit_llm to return a MagicMock whose chain
.with_structured_output(...).invoke(...) returns a canned schema instance.
"""

import pytest
from unittest.mock import MagicMock, patch

import app.audit.llm as llm_module
from app.audit.state import AuditState, AnalystOutput, AuditorOutput
from app.audit.nodes import node_analyst, node_auditor, _join
from app.core.config import settings

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BASE_STATE: AuditState = {
    "complaint_text": "The refrigerator compressor broke after 3 months.",
    "contract_clauses": "Article 3: compressor failures covered for 12 months.",
    "rag_chunks": ["compressor failures covered for 12 months from purchase date"],
    "draft_verdict": "APPROVED",
    "draft_justification": "Compressor failure is explicitly covered in Article 3.",
    "corrections_applied": False,
    "final_verdict": "APPROVED",
    "final_justification": "Evidence confirms coverage.",
    "rag_citation": "compressor failures covered for 12 months",
}


def _make_mock_llm(structured_output_return):
    """Build a MagicMock that mimics BaseChatModel.with_structured_output().invoke()."""
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value.invoke.return_value = structured_output_return
    return mock_llm


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_llm_singleton():
    """Clear _models cache before/after each test to prevent cross-test contamination."""
    original = llm_module._models.copy()
    llm_module._models.clear()
    yield
    llm_module._models.clear()
    llm_module._models.update(original)


# ---------------------------------------------------------------------------
# node_analyst tests
# ---------------------------------------------------------------------------

def test_node_analyst_returns_draft_keys():
    """node_analyst returns a dict containing exactly draft_verdict and draft_justification."""
    canned = AnalystOutput(
        draft_verdict="APPROVED",
        draft_justification="Compressor failure is covered under Article 3.",
    )
    with patch("app.audit.nodes.get_audit_llm", return_value=_make_mock_llm(canned)):
        result = node_analyst(_BASE_STATE)

    assert set(result.keys()) == {"draft_verdict", "draft_justification"}


def test_node_analyst_verdict_in_enum():
    """The draft_verdict returned by node_analyst is always one of the 3 valid values."""
    valid_verdicts = {"APPROVED", "REJECTED", "INSPECTION_REQUIRED"}
    canned = AnalystOutput(
        draft_verdict="REJECTED",
        draft_justification="Damage caused by user misuse, excluded by Article 7.",
    )
    with patch("app.audit.nodes.get_audit_llm", return_value=_make_mock_llm(canned)):
        result = node_analyst(_BASE_STATE)

    assert result["draft_verdict"] in valid_verdicts


def test_node_analyst_does_not_write_final_fields():
    """node_analyst must NOT write final_verdict, corrections_applied, etc."""
    canned = AnalystOutput(
        draft_verdict="INSPECTION_REQUIRED",
        draft_justification="Evidence is ambiguous regarding the failure mode.",
    )
    forbidden_keys = {"final_verdict", "final_justification", "corrections_applied", "rag_citation"}
    with patch("app.audit.nodes.get_audit_llm", return_value=_make_mock_llm(canned)):
        result = node_analyst(_BASE_STATE)

    assert not (set(result.keys()) & forbidden_keys), (
        f"node_analyst wrote forbidden keys: {set(result.keys()) & forbidden_keys}"
    )


# ---------------------------------------------------------------------------
# node_auditor tests
# ---------------------------------------------------------------------------

def test_node_auditor_pass_through():
    """When auditor accepts the draft unchanged, corrections_applied is False."""
    canned = AuditorOutput(
        corrections_applied=False,
        final_verdict="APPROVED",
        final_justification="Evidence confirms the compressor failure is covered.",
        rag_citation="compressor failures covered for 12 months",
    )
    with patch("app.audit.nodes.get_audit_llm", return_value=_make_mock_llm(canned)):
        result = node_auditor(_BASE_STATE)

    assert result["corrections_applied"] is False


def test_node_auditor_hallucination_catch():
    """Auditor detects a draft that cites a fact absent from rag_chunks, applies
    corrections, and propagates the corrected fields to the output.

    The state's draft_justification references 'Article 9: lifetime guarantee' which
    does NOT appear in rag_chunks — making it ungrounded. The mocked auditor LLM
    returns corrections_applied=True and a rewritten final_justification.

    Real hallucination DETECTION is validated by the Slice-3 @pytest.mark.slow
    integration test — this unit test proves wiring and correction propagation only.
    """
    ungrounded_state: AuditState = {
        **_BASE_STATE,
        # draft cites a clause that is verifiably absent from rag_chunks
        "draft_justification": (
            "Article 9 provides a lifetime guarantee, so the claim is fully covered."
        ),
        "rag_chunks": ["compressor failures covered for 12 months from purchase date"],
    }

    corrected_justification = (
        "Article 9 lifetime guarantee is not present in the retrieved evidence; "
        "downgrading to INSPECTION_REQUIRED per grounding policy."
    )
    corrected_output = AuditorOutput(
        corrections_applied=True,
        final_verdict="INSPECTION_REQUIRED",
        final_justification=corrected_justification,
        rag_citation="compressor failures covered for 12 months",
    )

    mock_llm = _make_mock_llm(corrected_output)

    with patch("app.audit.nodes.get_audit_llm", return_value=mock_llm):
        result = node_auditor(ungrounded_state)

    # Correction propagation assertions
    assert result["corrections_applied"] is True
    assert result["final_verdict"] == "INSPECTION_REQUIRED"
    assert result["final_justification"] == corrected_justification

    # Verify the LLM was invoked with a prompt containing the ungrounded draft
    invoke_call_args = mock_llm.with_structured_output.return_value.invoke.call_args
    prompt_arg = invoke_call_args[0][0]  # first positional arg
    assert "Article 9 provides a lifetime guarantee" in prompt_arg, (
        "Auditor LLM was not invoked with a prompt containing the ungrounded draft text"
    )


def test_node_auditor_returns_correct_keys():
    """node_auditor returns exactly the 4 keys it owns, no more."""
    canned = AuditorOutput(
        corrections_applied=False,
        final_verdict="APPROVED",
        final_justification="All facts are grounded in the evidence.",
        rag_citation="compressor failures covered for 12 months",
    )
    expected_keys = {"corrections_applied", "final_verdict", "final_justification", "rag_citation"}
    with patch("app.audit.nodes.get_audit_llm", return_value=_make_mock_llm(canned)):
        result = node_auditor(_BASE_STATE)

    assert set(result.keys()) == expected_keys


# ---------------------------------------------------------------------------
# Temperature tests
# ---------------------------------------------------------------------------

def test_node_analyst_uses_analyst_temperature():
    """node_analyst calls get_audit_llm with settings.AUDIT_ANALYST_TEMPERATURE (0.2)."""
    canned = AnalystOutput(
        draft_verdict="APPROVED",
        draft_justification="Covered under Article 3.",
    )
    with patch("app.audit.nodes.get_audit_llm", return_value=_make_mock_llm(canned)) as mock_factory:
        node_analyst(_BASE_STATE)

    mock_factory.assert_called_once_with(settings.AUDIT_ANALYST_TEMPERATURE)


def test_node_auditor_uses_auditor_temperature():
    """node_auditor calls get_audit_llm with settings.AUDIT_AUDITOR_TEMPERATURE (0.0)."""
    canned = AuditorOutput(
        corrections_applied=False,
        final_verdict="APPROVED",
        final_justification="All facts are grounded in the evidence.",
        rag_citation="compressor failures covered for 12 months",
    )
    with patch("app.audit.nodes.get_audit_llm", return_value=_make_mock_llm(canned)) as mock_factory:
        node_auditor(_BASE_STATE)

    mock_factory.assert_called_once_with(settings.AUDIT_AUDITOR_TEMPERATURE)


# ---------------------------------------------------------------------------
# _join helper tests  (Fix A — RNF-02 regression lock)
# ---------------------------------------------------------------------------

def test_join_single_chunk_passes_through_verbatim():
    """A single chunk must be returned unchanged — no index prefix.

    This fails against the old `f"[{i+1}] {chunk}"` form because that would
    produce '[1] compressor failures covered for 12 months' instead of the raw text.
    """
    chunk = "compressor failures covered for 12 months"
    assert _join([chunk]) == chunk


def test_join_multiple_chunks_no_numbering():
    """Multiple chunks are joined with a newline; no '[N]' prefix is added.

    If _join reintroduces numbered prefixes the '[1]' assertion fails.
    If newline joining breaks, the equality assertion fails.
    """
    result = _join(["a", "b"])
    assert "[1]" not in result, "_join must not add numbered prefixes"
    assert result == "a\nb", f"Expected 'a\\nb' but got {result!r}"


def test_join_empty_list_returns_sentinel():
    """An empty chunk list returns the designated sentinel string."""
    assert _join([]) == "(no evidence retrieved)"

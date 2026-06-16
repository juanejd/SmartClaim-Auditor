"""Unit tests for the compiled audit graph and run_audit() entrypoint in graph.py.

Both nodes are mocked so no real LLM call occurs. Tests cover:
- Correct node execution order (analyst -> auditor)
- Final state has all 6 output fields
- Input fields are passed through unchanged
- Citation backstop: pass -> verdict unchanged; fail -> downgrade to INSPECTION_REQUIRED
- Graph structure: no back-edge from auditor to analyst (no cycle)
"""

import logging

import pytest
from unittest.mock import patch, MagicMock

import app.audit.llm as llm_module
import app.audit.graph as graph_module
from app.audit.graph import run_audit


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset LLM model cache and the compiled graph singleton before each test."""
    original_models = llm_module._models.copy()
    llm_module._models.clear()

    original_compiled = graph_module._compiled
    graph_module._compiled = None

    yield

    llm_module._models.clear()
    llm_module._models.update(original_models)
    graph_module._compiled = original_compiled


# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

_COMPLAINT = "The refrigerator compressor failed after 3 months."
_CLAUSES = "Article 3: compressor failures covered for 12 months."
_CHUNKS = ["compressor failures covered for 12 months from purchase date"]

_ANALYST_RETURN = {
    "draft_verdict": "APPROVED",
    "draft_justification": "Compressor failure is covered under Article 3.",
}

_AUDITOR_RETURN = {
    "corrections_applied": False,
    "final_verdict": "APPROVED",
    "final_justification": "Evidence confirms coverage; no corrections required.",
    "rag_citation": "compressor failures covered for 12 months",
}


# ---------------------------------------------------------------------------
# Graph wiring tests
# ---------------------------------------------------------------------------

def test_graph_invokes_analyst_then_auditor():
    """node_analyst runs STRICTLY BEFORE node_auditor, and the auditor receives
    the analyst's draft_verdict in its state input."""
    call_order: list[str] = []

    def analyst_side_effect(state):
        call_order.append("analyst")
        return _ANALYST_RETURN

    def auditor_side_effect(state):
        call_order.append("auditor")
        # Verify the auditor's incoming state carries the analyst's draft_verdict.
        assert state["draft_verdict"] == _ANALYST_RETURN["draft_verdict"], (
            f"Auditor state missing analyst draft_verdict; got {state.get('draft_verdict')!r}"
        )
        return _AUDITOR_RETURN

    analyst_mock = MagicMock(side_effect=analyst_side_effect)
    auditor_mock = MagicMock(side_effect=auditor_side_effect)

    with patch("app.audit.graph.node_analyst", analyst_mock), \
         patch("app.audit.graph.node_auditor", auditor_mock):
        run_audit(
            complaint_text=_COMPLAINT,
            contract_clauses=_CLAUSES,
            rag_chunks=_CHUNKS,
        )

    assert call_order == ["analyst", "auditor"], (
        f"Expected ['analyst', 'auditor'] but got {call_order}"
    )


def test_graph_final_state_has_all_output_fields():
    """run_audit result contains all 6 output fields with non-None values."""
    expected_keys = {
        "draft_verdict", "draft_justification",
        "corrections_applied", "final_verdict", "final_justification", "rag_citation",
    }
    with patch("app.audit.graph.node_analyst", return_value=_ANALYST_RETURN), \
         patch("app.audit.graph.node_auditor", return_value=_AUDITOR_RETURN):
        result = run_audit(
            complaint_text=_COMPLAINT,
            contract_clauses=_CLAUSES,
            rag_chunks=_CHUNKS,
        )

    assert expected_keys.issubset(result.keys()), (
        f"Missing keys: {expected_keys - result.keys()}"
    )
    for key in expected_keys:
        assert result[key] is not None, f"Field {key!r} is None"


def test_input_fields_unchanged_after_run():
    """The 3 input fields in the result match what was passed in."""
    with patch("app.audit.graph.node_analyst", return_value=_ANALYST_RETURN), \
         patch("app.audit.graph.node_auditor", return_value=_AUDITOR_RETURN):
        result = run_audit(
            complaint_text=_COMPLAINT,
            contract_clauses=_CLAUSES,
            rag_chunks=_CHUNKS,
        )

    assert result["complaint_text"] == _COMPLAINT
    assert result["contract_clauses"] == _CLAUSES
    assert result["rag_chunks"] == _CHUNKS


# ---------------------------------------------------------------------------
# Citation backstop tests
# ---------------------------------------------------------------------------

def test_citation_pass_returns_correct_final_verdict():
    """When rag_citation is verbatim in a chunk, final_verdict is not downgraded."""
    auditor_return = {
        **_AUDITOR_RETURN,
        "rag_citation": "compressor failures covered for 12 months",  # present in _CHUNKS
    }
    with patch("app.audit.graph.node_analyst", return_value=_ANALYST_RETURN), \
         patch("app.audit.graph.node_auditor", return_value=auditor_return):
        result = run_audit(
            complaint_text=_COMPLAINT,
            contract_clauses=_CLAUSES,
            rag_chunks=_CHUNKS,
        )

    assert result["final_verdict"] == "APPROVED"


def test_citation_fail_downgrades_to_inspection_required(caplog):
    """When rag_citation is NOT verbatim in any chunk, final_verdict is downgraded
    and a WARNING is emitted via the audit.graph logger.

    Fix B (RNF-02 / PII-safe logging lock): the citation used here is >40 chars
    and ends with a distinctive sentinel tail.  The test asserts:
    1. The warning contains the truncation indicator ('first 40 chars') — proving
       the bounded-preview path was taken.
    2. The distinctive tail is NOT present in any warning — proving the raw full
       citation was NOT logged.

    Both assertions would FAIL against the old code that logged the citation raw
    (no truncation), because:
    - 'first 40 chars' would be absent from the log message.
    - The tail 'DISTINCTIVE_TAIL_MUST_NOT_BE_LOGGED' would appear verbatim.
    """
    # Citation is >60 chars; tail is a distinctive sentinel that must never appear
    # in any log output (it would if the raw value were logged without truncation).
    _DISTINCTIVE_TAIL = "DISTINCTIVE_TAIL_MUST_NOT_BE_LOGGED"
    long_citation = (
        "this citation does not appear in any chunk and is very long indeed "
        + _DISTINCTIVE_TAIL
    )
    assert len(long_citation) > 60, "Precondition: citation must exceed truncation bound"

    auditor_return = {
        **_AUDITOR_RETURN,
        "final_verdict": "APPROVED",
        "rag_citation": long_citation,
    }
    with caplog.at_level(logging.WARNING, logger="app.audit.graph"), \
         patch("app.audit.graph.node_analyst", return_value=_ANALYST_RETURN), \
         patch("app.audit.graph.node_auditor", return_value=auditor_return):
        result = run_audit(
            complaint_text=_COMPLAINT,
            contract_clauses=_CLAUSES,
            rag_chunks=_CHUNKS,
        )

    assert result["final_verdict"] == "INSPECTION_REQUIRED"

    warning_messages = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]

    # Existing lock: faithfulness-failure warning must be present.
    assert any("faithfulness failure" in m for m in warning_messages), (
        f"Expected a faithfulness-failure WARNING in app.audit.graph; got: {warning_messages}"
    )

    # Fix B lock #1: truncation indicator must appear in the warning.
    assert any("first 40 chars" in m for m in warning_messages), (
        f"Expected 'first 40 chars' in WARNING (proves truncation ran); got: {warning_messages}"
    )

    # Fix B lock #2: the distinctive tail must NOT appear in any warning message.
    assert not any(_DISTINCTIVE_TAIL in m for m in warning_messages), (
        f"Raw citation tail found in WARNING — PII-safe truncation was bypassed; "
        f"got: {warning_messages}"
    )


# ---------------------------------------------------------------------------
# Graph structure test
# ---------------------------------------------------------------------------

def test_no_cycle_auditor_to_analyst():
    """The compiled graph must NOT have an edge from 'auditor' back to 'analyst'."""
    with patch("app.audit.graph.node_analyst", return_value=_ANALYST_RETURN), \
         patch("app.audit.graph.node_auditor", return_value=_AUDITOR_RETURN):
        # Force graph compilation by calling run_audit once
        run_audit(
            complaint_text=_COMPLAINT,
            contract_clauses=_CLAUSES,
            rag_chunks=_CHUNKS,
        )

    compiled = graph_module._compiled
    assert compiled is not None, "Graph was not compiled"

    # Inspect the graph's edge map — LangGraph stores edges in .builder.edges
    # as a set of (source, target) tuples.
    try:
        edges = set(compiled.builder.edges)
    except AttributeError:
        # Fallback: check via graph.get_graph().edges if the above is unavailable
        graph_repr = compiled.get_graph()
        edges = {(e.source, e.target) for e in graph_repr.edges}

    assert ("auditor", "analyst") not in edges, (
        "Cycle detected: edge from 'auditor' back to 'analyst' exists"
    )

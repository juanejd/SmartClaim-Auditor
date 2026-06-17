from fastapi.testclient import TestClient

from app.main import app
from app.ml.classifier import ClassificationResult
from unittest.mock import patch


client = TestClient(app)

VALID_PAYLOAD = {
    "complaint_text": "The refrigerator compressor stopped working after only 3 months.",
    "contract_clauses": "Clause 5: All major components are warranted for 12 months.",
}


# POST /api/claims — happy path
def test_post_claim_returns_202():
    response = client.post("/api/claims", json=VALID_PAYLOAD)
    assert response.status_code == 202


def test_post_claim_returns_claim_id():
    response = client.post("/api/claims", json=VALID_PAYLOAD)
    body = response.json()
    assert "claim_id" in body
    # must be a non-empty string (UUID form)
    assert isinstance(body["claim_id"], str)
    assert len(body["claim_id"]) > 0


def test_post_claim_returns_status():
    response = client.post("/api/claims", json=VALID_PAYLOAD)
    body = response.json()
    assert "status" in body


def test_post_claim_returns_received_at():
    response = client.post("/api/claims", json=VALID_PAYLOAD)
    body = response.json()
    assert "received_at" in body


# POST /api/claims — validation errors (expect 422)
def test_post_claim_missing_complaint_text_returns_422():
    payload = {"contract_clauses": VALID_PAYLOAD["contract_clauses"]}
    response = client.post("/api/claims", json=payload)
    assert response.status_code == 422


def test_post_claim_empty_complaint_text_returns_422():
    payload = {**VALID_PAYLOAD, "complaint_text": ""}
    response = client.post("/api/claims", json=payload)
    assert response.status_code == 422


def test_post_claim_too_short_complaint_text_returns_422():
    # min_length is 10; this is 9 chars
    payload = {**VALID_PAYLOAD, "complaint_text": "Too short"}
    response = client.post("/api/claims", json=payload)
    assert response.status_code == 422


# GET /api/claims/{claim_id}
def test_get_claim_returns_stored_claim():
    post_response = client.post("/api/claims", json=VALID_PAYLOAD)
    claim_id = post_response.json()["claim_id"]

    get_response = client.get(f"/api/claims/{claim_id}")
    assert get_response.status_code == 200
    body = get_response.json()
    assert body["claim_id"] == claim_id
    assert body["complaint_text"] == VALID_PAYLOAD["complaint_text"]
    assert body["contract_clauses"] == VALID_PAYLOAD["contract_clauses"]


def test_get_claim_excludes_rag_chunks():
    post_response = client.post("/api/claims", json=VALID_PAYLOAD)
    claim_id = post_response.json()["claim_id"]

    get_response = client.get(f"/api/claims/{claim_id}")
    assert get_response.status_code == 200
    assert "rag_chunks" not in get_response.json()


def test_get_claim_received_at_is_utc():
    post_response = client.post("/api/claims", json=VALID_PAYLOAD)
    claim_id = post_response.json()["claim_id"]

    get_response = client.get(f"/api/claims/{claim_id}")
    assert get_response.status_code == 200
    received_at = get_response.json()["received_at"]
    assert received_at.endswith("+00:00") or received_at.endswith("Z"), (
        f"received_at is not UTC-aware: {received_at}"
    )


def test_get_unknown_claim_returns_404():
    response = client.get("/api/claims/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@patch("app.api.claims.classify")
def test_post_claim_classifies_and_forwards(mock_classify):
    mock_classify.return_value = ClassificationResult(
        label="ELECTRICAL_FAILURE", confidence=0.85, status="CLASSIFIED"
    )
    response = client.post("/api/claims", json=VALID_PAYLOAD)
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "CLASSIFIED"

    get_res = client.get(f"/api/claims/{body['claim_id']}")
    saved = get_res.json()
    assert saved["status"] == "CLASSIFIED"
    assert saved["intent_label"] == "ELECTRICAL_FAILURE"
    assert saved["confidence"] == 0.85


@patch("app.api.claims.classify")
def test_post_claim_halts_on_low_confidence(mock_classify):
    mock_classify.return_value = ClassificationResult(
        label="OTHER", confidence=0.55, status="LOW_CONFIDENCE"
    )
    response = client.post("/api/claims", json=VALID_PAYLOAD)
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "LOW_CONFIDENCE"


# ---------------------------------------------------------------------------
# Phase E — audit wiring tests
# ---------------------------------------------------------------------------

_AUDIT_RESULT = {
    "complaint_text": VALID_PAYLOAD["complaint_text"],
    "contract_clauses": VALID_PAYLOAD["contract_clauses"],
    "rag_chunks": ["The compressor is covered for 12 months under clause 5."],
    "draft_verdict": "APPROVED",
    "draft_justification": "Compressor failure within warranty period.",
    "corrections_applied": False,
    "final_verdict": "APPROVED",
    "final_justification": "Confirmed: compressor within 12-month warranty.",
    "rag_citation": "The compressor is covered for 12 months",
}


@patch("app.api.claims.run_audit", return_value=_AUDIT_RESULT)
@patch("app.api.claims.retrieve")
@patch("app.api.claims.classify")
def test_post_claim_invokes_run_audit_when_classified(
    mock_classify, mock_retrieve, mock_run_audit
):
    from app.models.claim import RagChunk

    mock_classify.return_value = ClassificationResult(
        label="MECHANICAL_FAILURE", confidence=0.9, status="CLASSIFIED"
    )
    mock_retrieve.return_value = [
        RagChunk(
            text="The compressor is covered for 12 months under clause 5.",
            source_section="Warranty",
            page=1,
            score=0.95,
        )
    ]

    response = client.post("/api/claims", json=VALID_PAYLOAD)
    assert response.status_code == 202

    # run_audit must have been called exactly once with the correct kwargs
    mock_run_audit.assert_called_once()
    call_kwargs = mock_run_audit.call_args.kwargs
    assert call_kwargs["complaint_text"] == VALID_PAYLOAD["complaint_text"]
    assert call_kwargs["contract_clauses"] == VALID_PAYLOAD["contract_clauses"]
    assert isinstance(call_kwargs["rag_chunks"], list)
    assert len(call_kwargs["rag_chunks"]) == 1
    assert isinstance(call_kwargs["rag_chunks"][0], str)

    # GET the claim and verify status + all 6 audit fields
    claim_id = response.json()["claim_id"]
    get_res = client.get(f"/api/claims/{claim_id}")
    saved = get_res.json()
    assert saved["status"] == "AUDITED"
    assert saved["draft_verdict"] == "APPROVED"
    assert saved["draft_justification"] is not None
    assert saved["corrections_applied"] is False
    assert saved["final_verdict"] == "APPROVED"
    assert saved["final_justification"] is not None
    assert saved["rag_citation"] is not None


@patch("app.api.claims.run_audit", return_value=_AUDIT_RESULT)
@patch("app.api.claims.retrieve")
@patch("app.api.claims.classify")
def test_post_claim_status_audited_on_success(
    mock_classify, mock_retrieve, mock_run_audit
):
    from app.models.claim import RagChunk

    mock_classify.return_value = ClassificationResult(
        label="MECHANICAL_FAILURE", confidence=0.9, status="CLASSIFIED"
    )
    mock_retrieve.return_value = [
        RagChunk(
            text="The compressor is covered for 12 months under clause 5.",
            source_section="Warranty",
            page=1,
            score=0.95,
        )
    ]

    response = client.post("/api/claims", json=VALID_PAYLOAD)
    assert response.status_code == 202

    # POST response is still a lightweight ClaimAccepted — no audit detail
    body = response.json()
    assert "claim_id" in body
    assert "status" in body
    assert "draft_verdict" not in body
    assert "final_verdict" not in body

    # Audit fields visible only via GET
    claim_id = body["claim_id"]
    saved = client.get(f"/api/claims/{claim_id}").json()
    assert saved["status"] == "AUDITED"


@patch("app.api.claims.run_audit", side_effect=RuntimeError("Groq unavailable"))
@patch("app.api.claims.retrieve")
@patch("app.api.claims.classify")
def test_post_claim_audit_failure_does_not_advance_status(
    mock_classify, mock_retrieve, mock_run_audit
):
    from app.models.claim import RagChunk

    mock_classify.return_value = ClassificationResult(
        label="MECHANICAL_FAILURE", confidence=0.9, status="CLASSIFIED"
    )
    mock_retrieve.return_value = [
        RagChunk(
            text="Compressor covered for 12 months.",
            source_section="Warranty",
            page=1,
            score=0.9,
        )
    ]

    # POST must still return 202 — the claim is saved even when audit fails
    response = client.post("/api/claims", json=VALID_PAYLOAD)
    assert response.status_code == 202

    claim_id = response.json()["claim_id"]
    saved = client.get(f"/api/claims/{claim_id}").json()

    # Status must NOT be AUDITED when the audit graph raised
    assert saved["status"] != "AUDITED"
    # All 6 audit fields must be null — no fabricated values
    assert saved["draft_verdict"] is None
    assert saved["draft_justification"] is None
    assert saved["corrections_applied"] is None
    assert saved["final_verdict"] is None
    assert saved["final_justification"] is None
    assert saved["rag_citation"] is None


@patch("app.api.claims.classify")
def test_post_claim_run_audit_not_called_when_low_confidence(mock_classify):
    mock_classify.return_value = ClassificationResult(
        label="OTHER", confidence=0.55, status="LOW_CONFIDENCE"
    )

    with patch("app.api.claims.run_audit") as mock_run_audit:
        response = client.post("/api/claims", json=VALID_PAYLOAD)
        assert response.status_code == 202
        mock_run_audit.assert_not_called()

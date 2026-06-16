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

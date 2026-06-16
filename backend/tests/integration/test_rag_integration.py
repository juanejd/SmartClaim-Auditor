from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlmodel import Session

from app.main import app
from app.db.database import engine
from app.ml.classifier import ClassificationResult
from app.models.claim import RagChunk, Claim

client = TestClient(app)

VALID_PAYLOAD = {
    "complaint_text": "The refrigerator compressor stopped working after only 3 months.",
    "contract_clauses": "Clause 5: All major components are warranted for 12 months.",
}


@patch("app.api.claims.classify")
@patch("app.api.claims.retrieve")
def test_rag_integration_with_classified_claim(mock_retrieve, mock_classify):
    mock_classify.return_value = ClassificationResult(
        label="ELECTRICAL_FAILURE", confidence=0.85, status="CLASSIFIED"
    )
    mock_retrieve.return_value = [
        RagChunk(text="Chunk 1", source_section="S1", page=1, score=0.9),
        RagChunk(text="Chunk 2", source_section="S1", page=2, score=1.1),
    ]

    response = client.post("/api/claims", json=VALID_PAYLOAD)
    assert response.status_code == 202

    claim_id = response.json()["claim_id"]

    get_res = client.get(f"/api/claims/{claim_id}")
    assert get_res.status_code == 200
    assert "rag_chunks" not in get_res.json()
    assert get_res.json()["status"] == "CLASSIFIED"

    with Session(engine) as session:
        saved = session.get(Claim, claim_id)
    assert saved.status == "CLASSIFIED"
    assert saved.rag_chunks is not None
    assert len(saved.rag_chunks) == 2
    assert saved.rag_chunks[0]["text"] == "Chunk 1"


@patch("app.api.claims.classify")
@patch("app.api.claims.retrieve")
def test_low_confidence_skips_rag(mock_retrieve, mock_classify):
    mock_classify.return_value = ClassificationResult(
        label="UNKNOWN", confidence=0.2, status="LOW_CONFIDENCE"
    )

    response = client.post("/api/claims", json=VALID_PAYLOAD)
    assert response.status_code == 202

    mock_retrieve.assert_not_called()

    claim_id = response.json()["claim_id"]

    with Session(engine) as session:
        saved = session.get(Claim, claim_id)
    assert saved.status == "LOW_CONFIDENCE"
    assert saved.rag_chunks is None

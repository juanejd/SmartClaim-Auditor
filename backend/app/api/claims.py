from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.models.claim import ClaimAccepted, ClaimRead, Claim, CreateClaim

from app.db.database import SessionDep
from app.ml.classifier import classify
from app.rag.retriever import retrieve

router = APIRouter(prefix="/api/claims", tags=["claims"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ClaimAccepted,
)
def submit_claim(claim_request: CreateClaim, session: SessionDep) -> ClaimAccepted:
    received_at = datetime.now(tz=timezone.utc)

    classification = classify(claim_request.complaint_text)

    rag_chunks = None
    if classification.status == "CLASSIFIED":
        raw_chunks = retrieve(claim_request.complaint_text)
        rag_chunks = [chunk.model_dump() for chunk in raw_chunks]

    ingested = Claim(
        complaint_text=claim_request.complaint_text,
        contract_clauses=claim_request.contract_clauses,
        received_at=received_at,
        status=classification.status,
        intent_label=classification.label,
        confidence=classification.confidence,
        rag_chunks=rag_chunks,
    )

    session.add(ingested)
    session.commit()
    session.refresh(ingested)

    return ClaimAccepted(
        claim_id=ingested.claim_id,
        intent_label=classification.label,
        confidence=classification.confidence,
        status=classification.status,
        received_at=received_at,
    )


@router.get(
    "/{claim_id}",
    status_code=status.HTTP_200_OK,
    response_model=ClaimRead,
)
def get_claim(claim_id: str, session: SessionDep) -> ClaimRead:
    claim = session.get(Claim, claim_id)

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="claim not found"
        )
    return claim

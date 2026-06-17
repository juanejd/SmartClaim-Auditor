import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from sqlmodel import select

from app.models.claim import ClaimAccepted, ClaimRead, ClaimSummary, Claim, CreateClaim

from app.db.database import SessionDep
from app.ml.classifier import classify
from app.rag.retriever import retrieve
from app.audit.graph import run_audit

logger = logging.getLogger(__name__)

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
    audit: dict | None = None
    claim_status = classification.status

    if classification.status == "CLASSIFIED":
        raw_chunks = retrieve(claim_request.complaint_text)
        rag_chunks = [chunk.model_dump() for chunk in raw_chunks]

        chunk_texts: list[str] = [c["text"] for c in rag_chunks]
        try:
            audit = run_audit(
                complaint_text=claim_request.complaint_text,
                contract_clauses=claim_request.contract_clauses,
                rag_chunks=chunk_texts,
            )
            claim_status = "AUDITED"
        except Exception:
            logger.exception(
                "audit graph failed for claim; persisting without audit fields"
            )

    ingested = Claim(
        complaint_text=claim_request.complaint_text,
        contract_clauses=claim_request.contract_clauses,
        received_at=received_at,
        status=claim_status,
        intent_label=classification.label,
        confidence=classification.confidence,
        rag_chunks=rag_chunks,
        draft_verdict=audit["draft_verdict"] if audit else None,
        draft_justification=audit["draft_justification"] if audit else None,
        corrections_applied=audit["corrections_applied"] if audit else None,
        final_verdict=audit["final_verdict"] if audit else None,
        final_justification=audit["final_justification"] if audit else None,
        rag_citation=audit["rag_citation"] if audit else None,
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
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[ClaimSummary],
)
def list_claims(session: SessionDep) -> list[ClaimSummary]:
    statement = select(Claim).order_by(Claim.received_at.desc())
    claims = session.exec(statement).all()
    return list(claims)


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

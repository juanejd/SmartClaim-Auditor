import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.models.claim import ClaimAccepted, ClaimIngested, ClaimRequest
from app.db.database import SessionDep


router = APIRouter(prefix="/api/claims", tags=["claims"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ClaimAccepted,
)
async def submit_claim(
    claimrequest: ClaimRequest, session: SessionDep
) -> ClaimAccepted:
    claim_id = str(uuid.uuid4())
    received_at = datetime.now(tz=timezone.utc)

    ingested = ClaimIngested(
        claim_id=claim_id,
        complaint_text=claimrequest.complaint_text,
        contract_clauses=claimrequest.contract_clauses,
        received_at=received_at,
    )
    session.add(ingested)
    session.commit()
    session.refresh(ingested)

    return ClaimAccepted(
        claim_id=claim_id,
        status="ACCEPTED",
        received_at=received_at,
    )


@router.get(
    "/{claim_id}",
    status_code=status.HTTP_200_OK,
    response_model=ClaimIngested,
)
def get_claim(claim_id: str, session: SessionDep) -> ClaimIngested:
    claim = session.get(ClaimIngested, claim_id)

    if not claim:
        raise HTTPException(status_code=404, detail="claim not found")
    return claim

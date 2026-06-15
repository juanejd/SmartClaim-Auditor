import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.models.claim import ClaimAccepted, Claim, CreateClaim


from app.db.database import SessionDep


router = APIRouter(prefix="/api/claims", tags=["claims"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ClaimAccepted,
)
async def submit_claim(
    claim_request: CreateClaim, session: SessionDep
) -> ClaimAccepted:
    claim_id = str(uuid.uuid4())
    received_at = datetime.now(tz=timezone.utc)

    ingested = Claim(
        claim_id=claim_id,
        complaint_text=claim_request.complaint_text,
        contract_clauses=claim_request.contract_clauses,
        received_at=received_at,
    )

    claim_dict = claim_request.model_dump()
    print("claim_dict", claim_dict)
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
    response_model=Claim,
)
def get_claim(claim_id: str, session: SessionDep) -> Claim:
    claim = session.get(Claim, claim_id)

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="claim not found"
        )
    return claim

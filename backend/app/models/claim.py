from datetime import datetime
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

from app.core.config import COMPLAINT_TEXT_MIN_LENGTH


class ClaimBase(SQLModel):
    complaint_text: str = Field(min_length=COMPLAINT_TEXT_MIN_LENGTH)
    contract_clauses: str = Field(min_length=1)


class ClaimAccepted(BaseModel):
    claim_id: str
    status: str
    received_at: datetime


class CreateClaim(ClaimBase):
    pass


class Claim(ClaimBase, table=True):
    claim_id: str | None = Field(default=None, primary_key=True)
    received_at: datetime

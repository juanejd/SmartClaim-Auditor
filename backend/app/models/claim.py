from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, field_serializer
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON, DateTime

from app.core.config import COMPLAINT_TEXT_MIN_LENGTH


class RagChunk(BaseModel):
    text: str
    source_section: str
    page: int
    score: float


class _ReceivedAtMixin(BaseModel):
    received_at: datetime

    @field_serializer("received_at")
    def serialize_received_at(self, dt: datetime) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class ClaimBase(SQLModel):
    complaint_text: str = Field(min_length=COMPLAINT_TEXT_MIN_LENGTH)
    contract_clauses: str = Field(min_length=1)


class ClaimAccepted(_ReceivedAtMixin):
    claim_id: str
    intent_label: str
    confidence: float
    status: str


class CreateClaim(ClaimBase):
    pass


class Claim(ClaimBase, table=True):
    claim_id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
    )
    status: str = Field(default="RECEIVED")
    intent_label: str | None = Field(default=None)
    confidence: float | None = Field(default=None)
    received_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    rag_chunks: list[dict] | None = Field(default=None, sa_column=Column(JSON))

    draft_verdict: str | None = Field(default=None)
    draft_justification: str | None = Field(default=None)
    corrections_applied: bool | None = Field(default=None)
    final_verdict: str | None = Field(default=None)
    final_justification: str | None = Field(default=None)
    rag_citation: str | None = Field(default=None)


class ClaimRead(_ReceivedAtMixin):
    claim_id: str
    complaint_text: str
    contract_clauses: str
    status: str
    intent_label: str | None
    confidence: float | None
    draft_verdict: str | None = None
    draft_justification: str | None = None
    corrections_applied: bool | None = None
    final_verdict: str | None = None
    final_justification: str | None = None
    rag_citation: str | None = None

    model_config = {"from_attributes": True}

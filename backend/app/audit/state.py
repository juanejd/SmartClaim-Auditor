from typing import Literal, TypedDict

from pydantic import BaseModel, Field

Verdict = Literal["APPROVED", "REJECTED", "INSPECTION_REQUIRED"]


class AuditState(TypedDict):
    complaint_text: str
    contract_clauses: str | None
    rag_chunks: list[str]

    draft_verdict: Verdict
    draft_justification: str

    corrections_applied: bool
    final_verdict: Verdict
    final_justification: str
    rag_citation: str


class AnalystOutput(BaseModel):
    draft_verdict: Verdict
    draft_justification: str = Field(..., min_length=1)


class AuditorOutput(BaseModel):
    corrections_applied: bool
    final_verdict: Verdict
    final_justification: str = Field(..., min_length=1)
    rag_citation: str = Field(..., min_length=1)

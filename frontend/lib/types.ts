export type RagChunk = {
  text: string;
  source_section: string;
  page: number;
  score: number;
};

export type Verdict = "APPROVED" | "REJECTED" | "INSPECTION_REQUIRED";

export type ClaimStatus =
  | "RECEIVED"
  | "CLASSIFIED"
  | "AUDITED"
  | "LOW_CONFIDENCE"
  | "PENDING"
  | "PROCESSING"
  | "FAILED";

export type ClaimRead = {
  claim_id: string;
  complaint_text: string;
  contract_clauses?: string | null;
  status: ClaimStatus;
  intent_label: string | null;
  confidence: number | null;
  draft_verdict: string | null;
  draft_justification: string | null;
  corrections_applied: boolean | null;
  final_verdict: string | null;
  final_justification: string | null;
  rag_citation: string | null;
  rag_chunks: RagChunk[] | null;
  received_at: string;
};

export type ClaimAccepted = {
  claim_id: string;
  intent_label: string;
  confidence: number;
  status: ClaimStatus;
  received_at: string;
};

export type ClaimSummary = {
  claim_id: string;
  complaint_text: string;
  intent_label: string | null;
  status: ClaimStatus;
  final_verdict: string | null;
  received_at: string;
};

export type DocumentMeta = {
  filename: string;
  label: string;
  size_bytes: number;
};

export type ClauseItem = {
  id: string;
  ref: string;
  title: string;
  text: string;
};

export type ClausesSection = {
  id: string;
  title: string;
  clauses: ClauseItem[];
};

export type ClausesDoc = {
  id: string;
  document: string;
  code?: string;
  sections: ClausesSection[];
};

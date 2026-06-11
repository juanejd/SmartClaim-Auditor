# SmartClaim Auditor v1.0 — Project Core Context

## Purpose
Web application that automates the classification, retrieval and auditing of technical/financial claims. Replaces manual lookup of contracts and product manuals with a local NLP pipeline that emits a justified, hallucination-resistant verdict.

---

## Architecture: 5-Layer Pipeline (strictly sequential)

```
[POST /api/claims] → [HuggingFace Classifier] → [FAISS RAG] → [LangGraph Audit] → [Next.js Console]
```

| # | Layer | Technology | Input → Output |
|---|-------|-----------|----------------|
| 1 | API Gateway | FastAPI (Python 3.11) | JSON payload → validated claim object |
| 2 | Intent Classification | HuggingFace Transformers (DistilBERT / RoBERTa) | complaint text → intent label + confidence score |
| 3 | Semantic Retrieval | FAISS + Sentence-Transformers (`all-MiniLM-L6-v2`) | complaint vector → top-2 manual chunks (cosine similarity) |
| 4 | Dual Audit | LangGraph (2-node graph) | {complaint, contract, chunks} → audited verdict |
| 5 | Observability UI | Next.js 14 + Tailwind CSS | audit JSON → rendered reasoning trace |

---

## Core AI Component: LangGraph Dual-Audit Graph

**State schema (input to graph):**
```json
{
  "complaint_text": "string",
  "contract_clauses": "string",
  "rag_chunks": ["string", "string"]
}
```

**Node 1 — Technical Analyst:**
- Reads all three state fields
- Emits `draft_verdict`: one of `APPROVED | REJECTED | INSPECTION_REQUIRED`
- Provides logical justification referencing the retrieved chunks
- Temperature: `0.2` (allows reasoning fluency)

**Node 2 — Quality Auditor:**
- Receives Node 1 output + original state
- Validates that every factual claim in the draft is traceable to `rag_chunks` or `contract_clauses`
- If hallucination detected: revokes and rewrites the verdict
- Temperature: `0.0` (strict factual grounding only)
- **Output requirement:** final verdict MUST include a verbatim citation from `rag_chunks`

**Graph output schema:**
```json
{
  "draft_verdict": "string",
  "draft_justification": "string",
  "corrections_applied": "boolean",
  "final_verdict": "APPROVED | REJECTED | INSPECTION_REQUIRED",
  "final_justification": "string",
  "rag_citation": "string"
}
```

---

## Tech Stack

| Component | Choice | Key Constraint |
|-----------|--------|---------------|
| Frontend | Next.js 14 | SSR/CSR hybrid for real-time trace rendering |
| Backend | FastAPI | Async, Pydantic validation, auto Swagger docs |
| Classifier | HuggingFace Transformers | Local only — no external API calls |
| Embeddings | `all-MiniLM-L6-v2` | 22M params, CPU-runnable |
| Vector index | FAISS `IndexFlatL2` | In-memory, sub-ms search |
| Chunking | LangChain `RecursiveCharacterTextSplitter` | overlap=200 tokens |
| Audit graph | LangGraph | 2-node deterministic state machine |
| Persistence | SQLite / JSON files | University scope only |

**Hard constraint: 100% local execution.** No data leaves the machine during claim processing.

---

## Intent Classification

**Predefined label catalog:**
- `ELECTRICAL_FAILURE`
- `OPERATION_ERROR`
- `FINANCIAL_WARRANTY`
- `PHYSICAL_DAMAGE`
- `OTHER`

**Threshold:** confidence score must exceed `0.70` to proceed. Below threshold → status `LOW_CONFIDENCE`, routed to manual review.

---

## RAG Configuration

- **Chunk size:** 512 tokens
- **Overlap:** 200 tokens
- **k (retrieved chunks):** 2
- **Similarity metric:** cosine similarity
- **Index type:** `IndexFlatL2` (suitable for < 10,000 chunks)
- **Source documents:** product technical manuals (PDF → chunked → embedded → indexed)
- **Chunk metadata stored:** source section, page number, similarity score

---

## Functional Requirements (5 core)

| ID | Name | Acceptance Criterion |
|----|------|---------------------|
| RF-01 | Claim ingestion via REST | `POST /api/claims` returns `202 + claim_id` in < 200ms; `422` for invalid schema |
| RF-02 | Intent auto-classification | Label + confidence score returned; pipeline halts if score < 0.70 |
| RF-03 | RAG retrieval from FAISS | Top-2 chunks returned with similarity score and source section reference |
| RF-04 | LangGraph dual-audit verdict | Response JSON exposes `draft_verdict` and `final_verdict` as separate fields |
| RF-05 | Reasoning trace UI | Panel shows: RAG chunks, Node 1 draft, Node 2 corrections, final verdict with color-coded status |

---

## Non-Functional Requirements (5 core)

| ID | Attribute | Metric |
|----|-----------|--------|
| RNF-01 | Latency | Full pipeline ≤ 5s on CPU-only, 8GB RAM (excludes initial FAISS index load) |
| RNF-02 | Factual fidelity | 100% of final verdicts cite at least one RAG chunk verbatim |
| RNF-03 | Data privacy | Zero outbound requests to external AI APIs during claim processing (verifiable via network trace) |
| RNF-04 | Modularity | Updating FAISS index with a new PDF requires zero changes to FastAPI or Next.js code |
| RNF-05 | Reproducibility | Fresh environment setup < 15 min using `requirements.txt` + `package.json` + `README.md` |

---

## Key Design Decisions

1. **No general-purpose LLM for classification.** A fine-tunable Encoder-Only model (DistilBERT) handles intent classification instead of a generative model, avoiding hallucination risk at the labeling stage.

2. **LangGraph over a single prompt.** The two-node graph makes the audit step explicit, testable, and auditable. Node 2 can be unit-tested against known hallucination cases independently from Node 1.

3. **FAISS over external vector DB.** Eliminates infrastructure dependency for the university scope. Migration path to ChromaDB or Qdrant is straightforward when persistence across restarts is needed.

4. **Prompts externalized.** LangGraph node prompts live in `.yaml` / `.env` config files, not hardcoded. Allows iteration on verdict quality without touching application code.

---

## Evaluation Metrics (for project delivery)

| Metric | Description |
|--------|-------------|
| Classification Accuracy | % correctly labeled over 20+ manually labeled test cases |
| MRR@2 | Mean Reciprocal Rank — correct manual chunk in top-2 FAISS results |
| Faithfulness Score | % of final verdicts with explicit RAG citation (target: 100%) |
| Auditor Correction Rate | % of Node 1 drafts modified by Node 2 (hallucination detection rate) |
| Latency per Stage | Timestamp breakdown per pipeline node to identify bottlenecks |

---

## Out of Scope (university version)

- JWT authentication / RBAC
- Cloud deployment
- ERP / CRM integration
- Real-time streaming (SSE)
- Fine-tuning the classifier on domain data
- FAISS IVF index (for > 10,000 chunks)
- Cross-encoder reranking
- Analytics dashboard

# 00 — System Overview & Mental Model

> Read this **before** anything else. This is the map. The other documents
> (`01` → `05`) are the territory. If the map is clear, you will never get lost
> in the territory.

---

## 1. What are we actually building?

SmartClaim Auditor is a **local-only NLP pipeline** that takes a technical/financial
claim written in natural language and returns a **justified, auditable verdict**:
`APPROVED`, `REJECTED`, or `INSPECTION_REQUIRED`.

The whole point is **trust**. Anyone can build a system that spits out a verdict.
The hard part — and the reason this project exists — is producing a verdict that:

1. Is **grounded** in real source documents (product manuals + contract clauses),
   not in the model's imagination.
2. Is **auditable** — you can see exactly *why* the system decided what it decided.
3. Never **hallucinates** — every factual claim in the final verdict must trace
   back to a retrieved chunk or a contract clause.

If you remember nothing else, remember this: **the verdict is worthless without
its citation.** That is the north star of the entire system.

---

## 2. The 5-layer pipeline (the spine of the project)

The system is a **strictly sequential pipeline**. Data flows in one direction.
Each layer has one job, takes a defined input, and produces a defined output for
the next layer.

```
                    ┌─────────────────────────────────────────────┐
  HTTP POST  ─────▶ │  LAYER 1 · API Gateway (FastAPI)             │
  claim JSON        │  validate → assign claim_id → 202 Accepted   │
                    └───────────────────┬─────────────────────────┘
                                        │ validated claim
                    ┌───────────────────▼─────────────────────────┐
                    │  LAYER 2 · Intent Classifier (HuggingFace)  │
                    │  text → label + confidence                  │
                    │  confidence < 0.70  →  LOW_CONFIDENCE (stop) │
                    └───────────────────┬─────────────────────────┘
                                        │ classified claim
                    ┌───────────────────▼─────────────────────────┐
                    │  LAYER 3 · Semantic Retrieval (FAISS + ST)  │
                    │  claim vector → top-2 manual chunks          │
                    └───────────────────┬─────────────────────────┘
                                        │ {claim, contract, chunks}
                    ┌───────────────────▼─────────────────────────┐
                    │  LAYER 4 · Dual Audit (LangGraph, 2 nodes)  │
                    │  Node 1 drafts → Node 2 audits/corrects     │
                    └───────────────────┬─────────────────────────┘
                                        │ audited verdict JSON
                    ┌───────────────────▼─────────────────────────┐
                    │  LAYER 5 · Observability UI (Next.js 16)    │
                    │  render the full reasoning trace             │
                    └─────────────────────────────────────────────┘
```

**Why sequential and not one big model call?** Because each layer is independently
**testable** and **swappable**. You can unit-test the classifier without the RAG.
You can swap FAISS for ChromaDB without touching FastAPI. This is the modularity
requirement (RNF-04), and it is an architectural decision, not an accident.

---

## 3. The build order (why we go 1 → 5)

You build in pipeline order because **each layer depends on the output shape of the
previous one**. You cannot meaningfully build the LangGraph audit (Layer 4) until
you know what the RAG (Layer 3) hands it.

| Phase doc | Layer | You can start when… | It is "done" when… |
|-----------|-------|---------------------|--------------------|
| `01` | API Gateway | now (greenfield) | `POST /api/claims` validates + returns `202 + claim_id` |
| `02` | Classifier | Layer 1 accepts claims | text → label + confidence, threshold gate works |
| `03` | RAG / FAISS | you have manuals to index | claim → top-2 chunks with scores + source |
| `04` | LangGraph | Layer 3 produces chunks | dual-node verdict with mandatory citation |
| `05` | Frontend | Layer 4 returns audit JSON | UI renders the full trace, color-coded |

> **Mentor note:** Do NOT try to build all five at once. Build Layer 1 to a *real*
> "done", then move on. A half-built layer infects every layer above it. This is the
> single most common way university projects die.

---

## 4. The contracts between layers (the most important part)

The layers talk to each other through **data contracts** — fixed JSON shapes. If
you nail these contracts early, you can build each layer in isolation and they will
snap together like Lego. If you improvise them, you will be refactoring forever.

**Claim ingested (Layer 1 output):**
```json
{
  "claim_id": "uuid",
  "complaint_text": "string",
  "contract_clauses": "string",
  "received_at": "ISO-8601"
}
```

**After classification (Layer 2 output adds):**
```json
{
  "intent_label": "ELECTRICAL_FAILURE | OPERATION_ERROR | FINANCIAL_WARRANTY | PHYSICAL_DAMAGE | OTHER",
  "confidence": 0.0,
  "status": "CLASSIFIED | LOW_CONFIDENCE"
}
```

**After retrieval (Layer 3 output adds):**
```json
{
  "rag_chunks": [
    { "text": "string", "source_section": "string", "page": 0, "score": 0.0 }
  ]
}
```

**Final audit (Layer 4 output — this is what the UI consumes):**
```json
{
  "draft_verdict": "string",
  "draft_justification": "string",
  "corrections_applied": true,
  "final_verdict": "APPROVED | REJECTED | INSPECTION_REQUIRED",
  "final_justification": "string",
  "rag_citation": "string"
}
```

Keep these shapes in a single source of truth (Pydantic models on the backend,
matching TypeScript types on the frontend). When they drift, the system breaks
silently. We will define them as we build each layer.

---

## 5. Hard constraints (non-negotiable rules)

These are the walls of the building. You do not get to move them.

- **100% local execution.** No outbound calls to external AI APIs during claim
  processing. This is verifiable via network trace (RNF-03). It drives almost every
  tech choice: local HuggingFace model, local FAISS index, local LLM for LangGraph.
- **Every final verdict cites a RAG chunk verbatim** (RNF-02, target 100%). The
  auditor node enforces this. A verdict without a citation is a **bug**, not a verdict.
- **≤ 5s full pipeline** on CPU-only, 8GB RAM (RNF-01). This is why we use small models
  (`all-MiniLM-L6-v2`, 22M params; DistilBERT, not a 7B LLM for classification).
- **Modularity** (RNF-04): adding a new PDF to the index must not require touching
  FastAPI or Next.js code.

---

## 6. ⚠️ Reality check: the repo vs. the core doc

Before you trust `smartclaim_core.md` blindly, know these **two real discrepancies**
found in the current codebase. The core doc is the *intent*; the repo is the *truth*.

### 6.1 Next.js version mismatch
- `smartclaim_core.md` says **Next.js 14**.
- `frontend/package.json` actually installs **Next.js 16.2.9 + React 19.2.4 + Tailwind v4**.
- `frontend/AGENTS.md` explicitly warns:
  > "This is NOT the Next.js you know — APIs, conventions, and file structure may
  > all differ from your training data. Read the relevant guide in
  > `node_modules/next/dist/docs/` before writing any code."

**Action:** treat Next.js 16 as the real target. Read the local docs in
`node_modules/next/dist/docs/` before writing frontend code. See `05-fase-frontend.md`.

### 6.2 The backend is currently a "Hello World"
The backend today (`backend/main.py`) is the FastAPI tutorial stub (`/items/{item_id}`).
Installed dependencies are **only** `fastapi` + `uvicorn` (+ `pytest`, `ruff` for dev).

**None of these are installed yet:** `transformers`, `torch`, `faiss-cpu`,
`sentence-transformers`, `langgraph`, `langchain`. That is fine — it is your
starting line. But it means: **everything from Layer 2 onward is a plan, not code.**
Each phase doc tells you exactly what to add and when.

---

## 7. Tooling already in place

| Area | Tool | Notes |
|------|------|-------|
| Backend pkg mgr | **uv** | `backend/uv.lock` present. Use `uv add <pkg>`, not raw pip. |
| Backend runtime | Python **3.11** | pinned in `.python-version` |
| Backend test | **pytest** | already a dev dependency — TDD from day one |
| Backend lint | **ruff** | already a dev dependency |
| Frontend pkg mgr | **pnpm** | `pnpm-lock.yaml` present. Use `pnpm add`, not npm. |
| Frontend | Next.js 16 + React 19 + Tailwind v4 | see §6.1 warning |

---

## 8. How to use this documentation set

1. Read this overview until the **pipeline + contracts** feel obvious.
2. Open `glosario.md` and skim it — you will refer back to it constantly.
3. Go to `01-fase-api-gateway.md` and build Layer 1 to its Definition of Done.
4. Only then move to `02`. Repeat. **One layer at a time, to a real "done".**

Each phase doc follows the same structure:
**Concept → Why it exists → What to build → Suggested structure → Definition of
Done → Gotchas → Dependencies.**

---

### Next: [`01-fase-api-gateway.md`](./01-fase-api-gateway.md)

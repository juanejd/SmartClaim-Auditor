# Glossary — SmartClaim Auditor

> Quick reference for every term, technology, and number in the project. When a phase
> doc uses a word you're unsure of, it's here. Concepts before code — know what these
> mean before you build with them.

---

## Core domain terms

| Term | Meaning |
|------|---------|
| **Claim** | A technical/financial complaint submitted for auditing. The unit of work. |
| **Verdict** | The system's decision: `APPROVED`, `REJECTED`, or `INSPECTION_REQUIRED`. |
| **Draft verdict** | Node 1's first attempt (before audit). May contain errors. |
| **Final verdict** | Node 2's audited, grounded decision. The one that counts. |
| **Citation** | A **verbatim** quote from a retrieved chunk that justifies the final verdict. Mandatory — no citation, no valid verdict. |
| **Reasoning trace** | The full visible path: claim → intent → evidence → draft → correction → final. Rendered by the UI. |
| **Hallucination** | A factual claim the model states but that is NOT supported by the source evidence. The enemy. The whole architecture exists to prevent it. |

---

## The 5 layers

| # | Layer | Tech | One-line job |
|---|-------|------|--------------|
| 1 | API Gateway | FastAPI | Validate the claim, give it an ID. |
| 2 | Intent Classifier | HuggingFace (DistilBERT) | Label the complaint + confidence. |
| 3 | Semantic Retrieval | FAISS + Sentence-Transformers | Find the top-2 relevant manual passages. |
| 4 | Dual Audit | LangGraph (2 nodes) | Draft a verdict, then audit it for grounding. |
| 5 | Observability UI | Next.js 16 | Render the reasoning trace, color-coded. |

---

## Technologies

| Tech | What it is | Why we use it here |
|------|-----------|--------------------|
| **FastAPI** | Async Python web framework with Pydantic validation + auto Swagger. | Fast, typed boundary; free `422` validation; auto docs. |
| **Pydantic** | Data validation via Python type hints. | The data contracts between layers; rejects bad input automatically. |
| **uv** | Fast Python package/dependency manager (lockfile-based). | The backend's package manager. Use `uv add`, `uv run`. |
| **HuggingFace Transformers** | Library of pretrained transformer models, run locally. | Local intent classification — no external API (RNF-03). |
| **DistilBERT / RoBERTa** | Encoder-only transformer models. | Classification, not generation → can't hallucinate labels. |
| **Encoder-only model** | A transformer built to *understand* text and output a class (softmax), not generate. | The right tool for classification; deterministic, small. |
| **Sentence-Transformers** | Library producing sentence/passage **embeddings**. | Turns text into vectors for semantic search. |
| **`all-MiniLM-L6-v2`** | A small embedding model: 22M params, 384-dim output, CPU-runnable. | Fits the ≤5s / 8GB budget; the RAG workhorse. |
| **Embedding** | A fixed-length vector of floats that represents the *meaning* of text. | Lets us compare meaning via geometry (distance/angle). |
| **FAISS** | Facebook AI Similarity Search — a fast vector index/database. | Sub-ms nearest-neighbor search over chunk vectors, fully local. |
| **`IndexFlatL2`** | A FAISS index doing brute-force **exact** L2 (Euclidean) search. | Exact, no training, perfect for < 10,000 chunks. |
| **`IndexFlatIP`** | FAISS index using **inner product**. With normalized vectors = cosine. | Alternative to get true cosine ranking. |
| **Cosine similarity** | Similarity = cosine of the angle between two vectors (direction = meaning). | Standard for comparing text embeddings; ignores magnitude. |
| **L2 / Euclidean distance** | Straight-line distance between two vectors. | What `IndexFlatL2` measures; equals cosine ranking *if vectors are normalized*. |
| **Normalization** | Scaling a vector to unit length (length 1). | REQUIRED so L2 distance behaves like cosine similarity. The #1 silent RAG bug if skipped. |
| **RAG** | Retrieval-Augmented Generation: fetch relevant text, then reason over it. | Grounds verdicts in real, citable evidence — anti-hallucination. |
| **Chunk** | A fixed-size slice of a source document (here 512 tokens, 200 overlap). | The unit that gets embedded, indexed, retrieved, and cited. |
| **`RecursiveCharacterTextSplitter`** | LangChain utility that splits text into overlapping chunks. | Produces the 512/200 chunks from manuals. |
| **LangChain** | LLM application framework. | Used here ONLY for the text splitter (chunking). |
| **LangGraph** | Build LLM workflows as a state-machine/graph of nodes. | Makes the 2-step audit explicit, testable, and auditable. |
| **Node** (LangGraph) | A function that reads the shared state, does work, writes back. | Node 1 = analyst, Node 2 = auditor. |
| **State** (LangGraph) | The shared, typed object that flows through the graph accumulating fields. | Carries claim + chunks + draft + final between nodes. |
| **Temperature** | LLM randomness dial. 0.0 = deterministic; higher = more varied/creative. | Analyst 0.2 (some fluency), Auditor 0.0 (strict grounding). |
| **Ollama** | Tool to run LLMs locally via a simple API. | A practical way to satisfy the 100%-local LLM constraint in Layer 4. |
| **Next.js 16** | React framework (App Router, SSR/CSR). **Note: repo uses 16, not 14.** | The observability console. ⚠ Read local docs — APIs differ from older versions. |
| **React 19** | UI library. | Component model for the trace UI. |
| **Tailwind CSS v4** | Utility-first CSS, **config-less** (`@import "tailwindcss"`). | Styling. v4 differs from v3 — no classic config file. |
| **pnpm** | Fast, disk-efficient JS package manager. | The frontend's package manager. Use `pnpm add`. |

---

## The magic numbers (and what they mean)

| Number | Where | Meaning |
|--------|-------|---------|
| **0.70** | Layer 2 | Confidence threshold. Below → `LOW_CONFIDENCE`, pipeline halts to manual review. |
| **512** | Layer 3 | Chunk size in tokens. Coherent idea, still specific. |
| **200** | Layer 3 | Chunk overlap in tokens. Prevents ideas being lost at boundaries. |
| **2** | Layer 3 | `k` — number of chunks retrieved. Enough evidence, tight prompt. |
| **0.2** | Layer 4 | Node 1 (Analyst) temperature — reasoning fluency. |
| **0.0** | Layer 4 | Node 2 (Auditor) temperature — strict, deterministic grounding. |
| **< 200ms** | RF-01 | Max claim-ingestion response time. |
| **≤ 5s** | RNF-01 | Max full-pipeline latency (CPU-only, 8GB RAM). |
| **100%** | RNF-02 | Target % of final verdicts with a verbatim citation. |
| **10,000** | Layer 3 | Chunk ceiling for `IndexFlatL2` to stay fast. |

---

## Status values

| Status | Stage | Meaning |
|--------|-------|---------|
| `CLASSIFIED` | Layer 2 | Confidence ≥ 0.70; proceeds down the pipeline. |
| `LOW_CONFIDENCE` | Layer 2 | Confidence < 0.70; halts → manual review. |
| `APPROVED` | Layer 4 | Final verdict: claim is valid/covered (green). |
| `REJECTED` | Layer 4 | Final verdict: claim is denied (red). |
| `INSPECTION_REQUIRED` | Layer 4 | Final verdict: needs physical/human inspection (amber). |

---

## Intent label catalog (closed set)

`ELECTRICAL_FAILURE` · `OPERATION_ERROR` · `FINANCIAL_WARRANTY` · `PHYSICAL_DAMAGE` · `OTHER`

The classifier can ONLY output one of these. No free-text labels.

---

## Requirement IDs

| ID | Type | Short |
|----|------|-------|
| RF-01 | Functional | Claim ingestion: `202 + claim_id` < 200ms; `422` on bad schema. |
| RF-02 | Functional | Intent classification + confidence; halt if < 0.70. |
| RF-03 | Functional | RAG returns top-2 chunks with score + source section. |
| RF-04 | Functional | Audit exposes `draft_verdict` and `final_verdict` separately. |
| RF-05 | Functional | UI shows chunks, draft, corrections, color-coded final verdict. |
| RNF-01 | Non-functional | Latency ≤ 5s, CPU-only, 8GB RAM. |
| RNF-02 | Non-functional | 100% of finals cite a chunk verbatim. |
| RNF-03 | Non-functional | Zero outbound AI API calls during processing. |
| RNF-04 | Non-functional | New PDF → re-index with zero FastAPI/Next.js code changes. |
| RNF-05 | Non-functional | Fresh setup < 15 min from `requirements.txt`/`package.json`/`README`. |

---

## Evaluation metrics (for delivery)

| Metric | Measures |
|--------|----------|
| **Classification Accuracy** | % correctly labeled over 20+ manually labeled test cases. |
| **MRR@2** | Mean Reciprocal Rank — was the correct chunk in the top-2? |
| **Faithfulness Score** | % of finals with explicit RAG citation (target 100%). |
| **Auditor Correction Rate** | % of Node 1 drafts that Node 2 had to fix (`corrections_applied`). |
| **Latency per Stage** | Per-node timing breakdown to find bottlenecks. |

---

## Out of scope (university version — don't build these)

JWT auth/RBAC · cloud deployment · ERP/CRM integration · real-time streaming (SSE) ·
fine-tuning the classifier on domain data · FAISS IVF index (> 10k chunks) ·
cross-encoder reranking · analytics dashboard.

---

### Back to: [`00-overview.md`](./00-overview.md)

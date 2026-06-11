# 03 — Phase 3: Semantic Retrieval (FAISS + Sentence-Transformers)

> **Layer 3 of 5.** This is the "R" in RAG (Retrieval-Augmented Generation). It
> finds the *evidence* the audit layer will reason over.

**Prerequisite:** Layer 2 ([`02`](./02-fase-classifier.md)) produces a classified claim.

---

## Concept

The classifier told us *what kind* of problem this is. The retriever answers a
different question: **"Which passages in the product manuals are relevant to THIS
specific complaint?"**

It works by **semantic similarity**, not keyword matching:
1. Product manuals (PDFs) are split into **chunks**.
2. Each chunk is turned into a **vector** (embedding) by a sentence-transformer.
3. All vectors live in a **FAISS index** (a fast vector database).
4. At query time, the complaint is embedded into the *same* vector space, and FAISS
   returns the **top-2 nearest chunks** by cosine similarity.

"Nearest in vector space" ≈ "closest in meaning". That's the magic — and it's just
geometry, not intelligence.

---

## Why it exists

Why retrieve at all? Because of the **anti-hallucination mandate** (RNF-02). The audit
layer (Layer 4) is forbidden from inventing facts. It can only reason over evidence we
hand it. **Layer 3 IS that evidence supply.**

Without RAG, the audit model would have to "know" the manual from its training — which
it doesn't, and even if it did, you couldn't *cite* it. RAG makes the system's
knowledge **explicit, current, and quotable**. Change the PDF, change the answer. That
is the entire value proposition.

This also satisfies **RNF-04 (modularity)**: adding a new manual means re-indexing,
with zero changes to FastAPI or Next.js code.

---

## The configuration (and what each number means)

From the core doc — and you must understand, not just copy, these:

| Setting | Value | What it means / why |
|---------|-------|---------------------|
| **Chunk size** | 512 tokens | Big enough to hold a coherent idea, small enough to be specific. Too big → noisy retrieval; too small → fragmented meaning. |
| **Overlap** | 200 tokens | Adjacent chunks share 200 tokens so an idea split across a boundary isn't lost. The price is some redundancy. |
| **k** | 2 | Return the top-2 chunks. Enough evidence to audit, few enough to keep the prompt tight and the latency low. |
| **Similarity** | cosine | Measures *angle* between vectors (direction = meaning), ignoring magnitude. Standard for text embeddings. |
| **Index type** | `IndexFlatL2` | Brute-force exact search. Perfect for < 10,000 chunks. Sub-ms. No training, no approximation. |
| **Embedding model** | `all-MiniLM-L6-v2` | 22M params, CPU-runnable, 384-dim vectors. The budget-friendly workhorse. |

> **The `IndexFlatL2` vs cosine nuance — read this twice.** `IndexFlatL2` measures
> *Euclidean (L2)* distance. To get *cosine* similarity behavior, you **normalize the
> vectors to unit length** before adding/searching (then L2 distance and cosine rank
> identically). `sentence-transformers` can do this with `normalize_embeddings=True`,
> or use `faiss.normalize_L2()`. If you skip normalization, your "cosine" similarity
> is a lie. This is the #1 silent bug in FAISS RAG. (Alternative: use
> `IndexFlatIP` — inner product — with normalized vectors, which IS cosine.)

---

## What to build

### 1. Add dependencies
```bash
uv add faiss-cpu sentence-transformers langchain
# PDF parsing — pick one:
uv add pypdf            # lightweight, common
```
> `faiss-cpu` (NOT `faiss-gpu`) — local/CPU constraint. `langchain` is used **only**
> for its `RecursiveCharacterTextSplitter` here (the core doc specifies it for chunking).

### 2. The two distinct flows
RAG has **two separate pipelines** people often conflate. Keep them separate:

**A. Indexing (offline, run once per manual):**
```
PDF → load text → RecursiveCharacterTextSplitter (512/200)
    → embed each chunk (all-MiniLM-L6-v2, normalized)
    → add to FAISS IndexFlatL2
    → persist: faiss.write_index() + a sidecar JSON of chunk metadata
```

**B. Retrieval (online, per claim):**
```
complaint_text → embed (same model, normalized)
    → faiss.search(k=2)
    → map result indices back to chunk text + metadata
    → return top-2 {text, source_section, page, score}
```

### 3. Suggested structure
```
backend/app/
├── rag/
│   ├── indexer.py       # build/persist the index from PDFs (CLI-runnable)
│   ├── retriever.py     # load index once, expose retrieve(text, k=2)
│   ├── chunking.py      # RecursiveCharacterTextSplitter config
│   └── embeddings.py    # the sentence-transformer wrapper (load once)
├── data/
│   ├── manuals/         # source PDFs (gitignore the big ones)
│   └── index/           # persisted .faiss + metadata.json
```

### 4. Metadata is mandatory
FAISS stores **vectors**, not text. When you search, you get back **integer indices**
and **distances** — NOT the chunk text. You MUST keep a parallel structure
(list / dict / JSON) mapping `index → {text, source_section, page}`. Per the core doc,
store: **source section, page number, similarity score**. Without this mapping you have
verdicts you can't cite — which violates the whole project.

### 5. Wire into the pipeline
After classification (and only if `status == CLASSIFIED`), call `retrieve(complaint_text)`
and attach `rag_chunks` to the claim object (see [`00`](./00-overview.md) §4).

---

## Suggested approach (TDD)

1. **Index a tiny fixture corpus** (2–3 short text files or a 1-page PDF) in a test.
2. **Red:** `test_retrieve_returns_k_chunks` — query → assert exactly 2 results, each
   with text + score + source.
3. **Red:** `test_relevant_chunk_ranks_first` — craft a query whose answer is in a
   known chunk; assert that chunk is in the top-2 (this is your MRR@2 metric in embryo).
4. **Green + Refactor.**
5. **Verify normalization:** assert scores are in the expected cosine range — catches
   the normalization bug early.

---

## Definition of Done ✅

- [ ] An **indexer** turns a PDF into a persisted FAISS index + metadata sidecar.
- [ ] `retrieve(text)` returns the **top-2** chunks, each with `text`, `source_section`,
      `page`, and a similarity `score`.
- [ ] Vectors are **normalized** → scores reflect true cosine similarity.
- [ ] The embedding model and the index are loaded **once**, not per request.
- [ ] Adding a new PDF + re-running the indexer updates retrieval with **zero changes**
      to FastAPI route code (RNF-04 verified).
- [ ] Retrieval is wired in after classification; the claim object carries `rag_chunks`.
- [ ] Tests: returns k results, relevant chunk ranks in top-2, scores in cosine range.

---

## Gotchas

- **Normalization (again).** Re-read the `IndexFlatL2` vs cosine box above. This will
  bite you if you ignore it.
- **Same model, both sides.** You MUST embed queries with the *exact same* model used
  for indexing. Different models = different vector spaces = garbage results.
- **Chunk count vs token count.** `RecursiveCharacterTextSplitter` splits on
  *characters* by default; "512 tokens" ≈ ~2000 chars (rough 4 chars/token). Configure
  deliberately and document your choice — don't conflate chars and tokens.
- **PDF extraction is messy.** PDFs have headers, footers, page numbers, broken
  hyphenation. Garbage in → garbage chunks → garbage retrieval. Inspect your extracted
  text before trusting it. This is 50% of real-world RAG pain.
- **Index/metadata drift.** If you rebuild the index but not the metadata (or vice
  versa), indices point to the wrong text. Build and persist them together, atomically.
- **Empty/short manuals.** If a PDF yields < k chunks, handle `k > available` gracefully.

---

## Dependencies to add

```bash
uv add faiss-cpu sentence-transformers langchain pypdf
```

---

## What this unlocks

Now you have the full evidence package: `{complaint_text, contract_clauses, rag_chunks}`.
This is **exactly** the input the dual-audit graph needs. Proceed to
[`04-fase-langgraph.md`](./04-fase-langgraph.md) — the heart of the system.

---

### Prev: [`02-fase-classifier.md`](./02-fase-classifier.md) · Next: [`04-fase-langgraph.md`](./04-fase-langgraph.md)

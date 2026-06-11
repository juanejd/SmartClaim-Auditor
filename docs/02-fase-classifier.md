# 02 — Phase 2: Intent Classifier (HuggingFace)

> **Layer 2 of 5.** Turns free-text complaints into a structured label the rest of
> the pipeline can route on.

**Prerequisite:** Layer 1 ([`01`](./01-fase-api-gateway.md)) accepts validated claims.

---

## Concept

The classifier reads `complaint_text` and answers one question:
**"What kind of problem is this?"** — returning one label from a fixed catalog plus a
**confidence score**.

The catalog (closed set — the model can only pick from these):
- `ELECTRICAL_FAILURE`
- `OPERATION_ERROR`
- `FINANCIAL_WARRANTY`
- `PHYSICAL_DAMAGE`
- `OTHER`

The model is a **fine-tunable Encoder-Only transformer** (DistilBERT / RoBERTa),
run **locally** via HuggingFace `transformers`. Encoder-only means it is built for
*understanding* text and producing a classification — not for *generating* text.

---

## Why it exists (and why NOT an LLM)

This is the single most important architectural decision in the project, so internalize it:

> **We do NOT use a generative LLM for classification.**

Why? Because a generative model *invents*. Ask GPT-style model "classify this" and it can
hallucinate a label that isn't in your catalog, or reason its way into a wrong bucket
with confident prose. At the **labeling stage**, hallucination is poison — every layer
downstream trusts this label.

An **encoder-only classifier**:
- Can **only** output one of your predefined labels (it's a softmax over N classes).
- Gives a **calibrated confidence score** you can threshold on.
- Is **small and fast** (DistilBERT ≈ 66M params) — fits the ≤5s / 8GB budget.
- Is **deterministic** given the same input — testable.

This is the "right tool for the job" principle. A generative LLM is a chainsaw;
classification is a job for a scalpel. (Design Decision #1 in the core doc.)

---

## The confidence threshold (the gate)

> **Threshold: confidence must exceed `0.70` to proceed.**
> Below → status `LOW_CONFIDENCE`, routed to manual review. Pipeline **halts**.

This is **RF-02**. It is a humility mechanism: the system admits when it isn't sure
instead of forcing a guess through four more layers. A claim the model is 55% sure about
should NOT get an automated verdict — it goes to a human.

Make the threshold a **config value** (`core/config.py`), not a magic number buried in code.
You will tune it.

---

## What to build

### 1. Add the dependencies
```bash
uv add transformers torch
```
> `torch` is large. The CPU-only wheel is what you want (no CUDA). On a constrained
> machine, install the CPU build explicitly to avoid pulling GPU packages.

### 2. The classifier service
```
backend/app/
├── ml/
│   ├── classifier.py        # load model once, expose classify(text) -> (label, score)
│   └── labels.py            # the LABEL catalog (single source of truth)
```

Key design points:
- **Load the model ONCE** at startup, not per request. Model loading is seconds;
  inference is milliseconds. Loading per request blows the latency budget instantly.
- Expose a clean function: `classify(text: str) -> ClassificationResult` where the
  result has `label`, `confidence`, and a `status` derived from the threshold.
- Keep the label catalog in **one place** (`labels.py`) shared with the rest of the app.

### 3. Wire it into the pipeline
After Layer 1 stores the claim, call the classifier. Extend the claim object with
`intent_label`, `confidence`, `status` (see [`00`](./00-overview.md) §4 contract).

### 4. The model choice — start pragmatic
The core doc lists DistilBERT/RoBERTa and explicitly puts **fine-tuning OUT OF SCOPE**
for the university version. So:
- **Phase 2a (now):** use a pre-trained zero-shot or sentiment/topic model as a
  *placeholder*, OR a `zero-shot-classification` pipeline (`facebook/bart-large-mnli`
  is common but heavier — mind the budget) with your labels as candidate classes.
- **Phase 2b (later, optional):** fine-tune DistilBERT on your 20+ labeled examples
  for real accuracy. Out of scope per core doc, but the structure should *allow* it.

> **Mentor honesty:** zero-shot classification is the fastest path to a working
> Layer 2 without training data. It won't be as accurate as a fine-tuned model, but
> it lets you build Layers 3–5 against real output *today*. Document this tradeoff.

---

## Suggested approach (TDD)

1. **Red:** `test_classify_returns_known_label` — feed an obviously-electrical
   complaint, assert the label is in the catalog and confidence ∈ [0, 1].
2. **Green:** implement `classify()`.
3. **Red:** `test_low_confidence_sets_status` — feed gibberish / ambiguous text,
   assert `status == "LOW_CONFIDENCE"` when score < threshold. (You may need to mock
   the model output to force a low score deterministically.)
4. **Green + Refactor.**

> **Testing gotcha:** real model inference in tests is slow and non-deterministic.
> Mock the model call for *logic* tests (threshold gating) and keep one or two
> *integration* tests that actually load the model, marked slow.

---

## Definition of Done ✅

- [ ] `classify(text)` returns a label **strictly from the catalog** + a confidence score.
- [ ] Confidence **< 0.70 → status `LOW_CONFIDENCE`** and the pipeline halts (no RAG, no audit).
- [ ] Confidence **≥ 0.70 → status `CLASSIFIED`**, claim object carries the label forward.
- [ ] The model is loaded **once** at startup, not per request.
- [ ] Threshold lives in config, not hardcoded.
- [ ] Tests cover: valid label output, threshold gating both sides.
- [ ] The `POST /api/claims` response (or a follow-up endpoint) exposes the label + score.

---

## Gotchas

- **Cold start latency.** First inference after load can be slow (graph warm-up).
  Consider a warm-up call at startup so the first *real* request isn't the slow one.
- **Label leakage.** Never let the model return a free-text label. Constrain output
  to the catalog. With zero-shot, pass exactly your labels as candidates.
- **Confidence ≠ correctness.** A high score means the model is *confident*, not
  *right*. This is exactly why Layers 3–4 (RAG + audit) exist — to ground the decision.
- **torch install size & arch.** On 8GB RAM, watch memory. Use CPU wheels. Don't
  accidentally pull a multi-GB CUDA stack.
- **Determinism in tests.** Set seeds / mock where you assert exact behavior.

---

## Dependencies to add

```bash
uv add transformers torch
# optional, if you go the sentence-level route early:
# (sentence-transformers is added in Phase 3 anyway)
```

---

## What this unlocks

A classified claim with a trusted label. Now **Layer 3 (RAG)** can retrieve the
relevant manual passages. Continue to [`03-fase-rag-faiss.md`](./03-fase-rag-faiss.md).

---

### Prev: [`01-fase-api-gateway.md`](./01-fase-api-gateway.md) · Next: [`03-fase-rag-faiss.md`](./03-fase-rag-faiss.md)

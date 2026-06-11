# 04 — Phase 4: Dual Audit (LangGraph, 2-node graph)

> **Layer 4 of 5. THE HEART OF THE PROJECT.** Everything before this gathered
> evidence. This layer turns evidence into a *justified, hallucination-resistant
> verdict*. If you only get one layer truly right, make it this one.

**Prerequisite:** Layer 3 ([`03`](./03-fase-rag-faiss.md)) produces `rag_chunks`.

---

## Concept

LangGraph lets you build an LLM workflow as a **state machine / graph** instead of one
monolithic prompt. Here the graph has **two nodes** that run in sequence over a shared
**state object**:

```
        ┌──────────────────────┐        ┌──────────────────────┐
 STATE  │  NODE 1              │  STATE │  NODE 2              │  FINAL
 ─────▶ │  Technical Analyst  │ ─────▶ │  Quality Auditor    │ ─────▶ STATE
        │  drafts a verdict   │  (+draft) │  validates/corrects │
        │  temperature 0.2    │        │  temperature 0.0    │
        └──────────────────────┘        └──────────────────────┘
```

**The state** flows through and accumulates fields. Each node reads the state, does its
job, writes its result back into the state, and passes it on.

---

## Why TWO nodes and not one prompt? (the core design decision)

This is **Design Decision #2** and it's the soul of the project. You *could* ask a
single LLM "read this and give a grounded verdict with a citation." Why split it?

1. **Separation of concerns.** Drafting a verdict (creative reasoning) and auditing a
   verdict for hallucinations (skeptical verification) are **different cognitive jobs**.
   A model doing both at once does neither well — it grades its own homework.
2. **Testability.** Node 2 can be **unit-tested in isolation** against known
   hallucination cases. Feed it a draft that cites a fact NOT in the chunks → assert it
   catches and corrects it. You cannot test "the prompt" that way.
3. **Auditability.** The two-step makes the reasoning **visible**. The UI (Layer 5)
   shows the draft AND the correction — the user sees the system catch its own mistake.
   That transparency *is* the product.
4. **Different temperatures for different jobs** (see below).

This is the difference between a black box and a glass box. We are building a glass box.

---

## The two nodes in detail

### Node 1 — Technical Analyst (`temperature 0.2`)
- **Reads:** all three state fields (`complaint_text`, `contract_clauses`, `rag_chunks`).
- **Produces:** `draft_verdict` ∈ `{APPROVED, REJECTED, INSPECTION_REQUIRED}` +
  `draft_justification` that references the retrieved chunks.
- **Temperature 0.2** — slightly above zero. Why? It needs a little **reasoning fluency**
  to connect the complaint to the evidence and write a coherent justification. Not zero
  (too rigid), not high (too inventive). 0.2 = "think, but don't improvise facts."

### Node 2 — Quality Auditor (`temperature 0.0`)
- **Reads:** Node 1's output **+** the original state.
- **Job:** verify that **every factual claim** in the draft is traceable to `rag_chunks`
  or `contract_clauses`. If it finds a claim with no source → it's a **hallucination** →
  **revoke and rewrite** the verdict.
- **Temperature 0.0** — fully deterministic. The auditor must NOT be creative. Its only
  job is strict factual grounding. Same input → same audit, every time.
- **Hard output requirement:** the final verdict **MUST include a verbatim citation**
  from `rag_chunks`. No citation = invalid output = bug (RNF-02, 100% target).

---

## The state schema (the contract)

**Input to the graph** (from Layer 3):
```json
{
  "complaint_text": "string",
  "contract_clauses": "string",
  "rag_chunks": ["string", "string"]
}
```

**Output of the graph** (to Layer 5 — see [`00`](./00-overview.md) §4):
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

`corrections_applied` is gold: it's literally your **Auditor Correction Rate** metric —
did Node 2 have to fix Node 1? Expose it.

---

## What to build

### 1. Choose the local LLM (the 100%-local constraint strikes here)
The hard constraint (RNF-03): **no external AI APIs.** So the LLM behind both nodes must
run **locally**. Realistic options for 8GB RAM / CPU:
- **Ollama** running a small model (e.g. `llama3.2`, `phi3`, `qwen2.5` 1.5–3B). Easiest
  local setup; LangChain/LangGraph integrate cleanly.
- **HuggingFace `transformers`** with a small instruct model (heavier to wire).

> **Mentor honesty + a decision you must make:** a 1.5–3B model on CPU is **slow** and
> **less reliable** at strict instruction-following. Node 2's "find unsupported claims"
> task is hard for small models. Plan for: tight prompts, low temperature, and possibly
> a deterministic *post-check* in code (does `rag_citation` actually appear verbatim in
> a chunk? if not, fail/retry). Don't trust the model to self-enforce — verify in code.

### 2. Externalize the prompts (Design Decision #4)
Node prompts live in **`.yaml` / config files**, NOT hardcoded. Why? So you can iterate
on verdict quality without touching application code. Structure:
```
backend/app/
├── audit/
│   ├── graph.py          # builds the LangGraph (nodes + edges + state)
│   ├── nodes.py          # node_1_analyst(), node_2_auditor()
│   ├── state.py          # the typed graph State (TypedDict / pydantic)
│   ├── llm.py            # local LLM client (Ollama / transformers), loaded once
│   └── prompts/
│       ├── analyst.yaml
│       └── auditor.yaml
```

### 3. Build the graph
- Define the **State** (a `TypedDict` is the LangGraph idiom).
- Add **two nodes** as functions `(state) -> partial state update`.
- Wire edges: `START → analyst → auditor → END`. Linear, deterministic. No cycles
  needed for v1 (a retry loop is a nice v2, but keep v1 simple).
- Compile the graph once; invoke per claim.

### 4. Enforce the citation in code (belt + suspenders)
After the graph runs, **verify in Python** that `rag_citation` is a verbatim substring
of one of the `rag_chunks`. If not, that's a faithfulness failure — log it, and either
retry or downgrade to `INSPECTION_REQUIRED`. Don't ship a verdict that violates RNF-02.

### 5. Wire into the pipeline
After Layer 3 attaches `rag_chunks`, invoke the graph, attach the audit output to the
claim, and that becomes the API's final response body.

---

## Suggested approach (TDD — this is where TDD pays off most)

The whole reason for two nodes is testability. Use it:

1. **Test Node 2 in isolation with a MOCKED LLM** (don't run a real model in unit tests):
   - Feed a draft that cites a fact present in chunks → assert `corrections_applied == false`.
   - Feed a draft that cites a fact **absent** from chunks → assert it gets corrected.
2. **Test the code-level citation check:** given an output whose `rag_citation` is NOT in
   any chunk → assert your post-check rejects it.
3. **Test the graph wiring:** mock both nodes, assert state flows analyst → auditor → end
   and the final shape matches the contract.
4. **One slow integration test** with the real local LLM, marked slow, for sanity.

> **Why mock the LLM?** Unit tests must be fast and deterministic. A real CPU LLM call is
> neither. Mock it to test *your logic* (state flow, citation enforcement, the threshold
> for `corrections_applied`). Test the *model* separately, in evaluation, not in CI.

---

## Definition of Done ✅

- [ ] A 2-node LangGraph runs `analyst → auditor` over a shared typed state.
- [ ] Node 1 emits `draft_verdict` (from the 3-value enum) + `draft_justification`.
- [ ] Node 2 validates grounding, sets `corrections_applied`, and produces
      `final_verdict` + `final_justification` + **`rag_citation`**.
- [ ] The response exposes `draft_verdict` and `final_verdict` as **separate fields** (RF-04).
- [ ] **Every** final verdict contains a `rag_citation` that is **verbatim** in a chunk —
      enforced in code, not just hoped for (RNF-02).
- [ ] Temperatures: analyst `0.2`, auditor `0.0`, set in config/prompts.
- [ ] Prompts live in external `.yaml`/config files, not hardcoded.
- [ ] The LLM runs **100% locally** — verifiable zero outbound AI calls (RNF-03).
- [ ] Node 2 has isolated unit tests for the hallucination-catch behavior.

---

## Gotchas

- **The citation requirement is the whole project.** A verdict without a verbatim
  citation is a *failure*, not a verdict. Enforce it in code as a backstop.
- **Small local models drift.** They may ignore "respond in JSON" or invent labels.
  Use structured output / strict parsing and validate against the enum. Reject + retry
  on malformed output.
- **Latency.** Two LLM calls on CPU can blow the 5s budget. Use small models, short
  prompts, cap output tokens. Measure per-node latency (it's an eval metric anyway).
- **Temperature 0.0 ≠ perfectly deterministic** on all backends, but it's as close as
  you get. Don't rely on bit-identical output; rely on the code-level citation check.
- **Don't over-engineer the graph.** v1 is linear: analyst → auditor → end. Resist
  adding conditional edges / retry loops until v1 works. (Out of scope: streaming/SSE.)
- **State immutability.** In LangGraph, nodes return *updates* to state. Don't mutate
  shared objects in place — follow the framework's state-merge model.

---

## Dependencies to add

```bash
uv add langgraph langchain-core
# plus your local LLM client, e.g.:
uv add langchain-ollama        # if using Ollama (install Ollama separately)
```

---

## What this unlocks

You now produce the **complete audit JSON** — draft, corrections, final verdict, and
citation. That is exactly what the UI needs to render the reasoning trace. Final layer:
[`05-fase-frontend.md`](./05-fase-frontend.md).

---

### Prev: [`03-fase-rag-faiss.md`](./03-fase-rag-faiss.md) · Next: [`05-fase-frontend.md`](./05-fase-frontend.md)

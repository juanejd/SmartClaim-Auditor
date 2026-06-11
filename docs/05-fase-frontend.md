# 05 — Phase 5: Observability UI (Next.js 16)

> **Layer 5 of 5.** The glass box. This is where the system's reasoning becomes
> *visible* to a human. The backend produces the verdict; this layer makes it
> **trustworthy** by showing the work.

**Prerequisite:** Layer 4 ([`04`](./04-fase-langgraph.md)) returns the full audit JSON.

---

## ⚠️ READ THIS FIRST — version reality

Your `frontend/AGENTS.md` says, verbatim:

> **"This is NOT the Next.js you know — APIs, conventions, and file structure may all
> differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/`
> before writing any code."**

The actual stack in `frontend/package.json`:
- **Next.js 16.2.9** (the core doc's "Next.js 14" is outdated — trust the package.json)
- **React 19.2.4**
- **Tailwind CSS v4** (config-less, CSS-first `@import "tailwindcss"`)
- **pnpm** (use `pnpm add`, never `npm install`)

**Before writing a single component**, open `frontend/node_modules/next/dist/docs/` and
read the routing / data-fetching guides for THIS version. Do not assume App Router
conventions from memory. This is non-negotiable — the warning is in your own repo.

---

## Concept

The UI has **one job**: render the **reasoning trace** of a claim audit so a human can
*see why* the system decided what it decided. It is an **observability console**, not a
CRUD app. The data is already computed by the backend — the frontend just makes it legible.

This maps to **RF-05**:
> Panel shows: RAG chunks, Node 1 draft, Node 2 corrections, final verdict with
> color-coded status.

---

## Why it exists

A verdict in a JSON blob convinces no one. A verdict you can **trace** — "here's the
manual passage it found, here's its first draft, here's where the auditor corrected it,
here's the final call with the exact quote it's based on" — *that* convinces.

The UI is where **RNF-02 (faithfulness)** becomes tangible: the user literally sees the
citation next to the verdict. Transparency is the feature. If the UI hides the draft and
the correction, you've thrown away the entire point of the two-node design (Layer 4).

---

## What to render (the reasoning trace)

Lay it out as a **vertical pipeline** mirroring the backend flow — the UI structure
should *teach* the user how the system thinks:

```
┌─────────────────────────────────────────────────────────┐
│  CLAIM                                                   │
│  "The unit stopped working after a power surge…"         │
├─────────────────────────────────────────────────────────┤
│  ① INTENT          ELECTRICAL_FAILURE   (conf 0.91) ✅   │
├─────────────────────────────────────────────────────────┤
│  ② RETRIEVED EVIDENCE (top-2)                            │
│   ▸ chunk 1  · §4.2 Power · p.12 · score 0.87            │
│   ▸ chunk 2  · §4.5 Surge · p.14 · score 0.81            │
├─────────────────────────────────────────────────────────┤
│  ③ NODE 1 · DRAFT VERDICT                                │
│     REJECTED — "not covered because…"                    │
├─────────────────────────────────────────────────────────┤
│  ④ NODE 2 · AUDIT      corrections_applied: TRUE ⚠       │
│     "Draft cited an unsupported clause; corrected."      │
├─────────────────────────────────────────────────────────┤
│  ⑤ FINAL VERDICT   ▌ INSPECTION_REQUIRED ▌  (yellow)    │
│     Justification: …                                     │
│     📎 Citation (verbatim): "…surge damage requires…"    │
└─────────────────────────────────────────────────────────┘
```

**Color-coding the status (RF-05):**
- `APPROVED` → green
- `REJECTED` → red
- `INSPECTION_REQUIRED` → yellow/amber
- `LOW_CONFIDENCE` (from Layer 2 halt) → gray/neutral

---

## What to build

### 1. Type the contract
Create TypeScript types that **mirror the backend Pydantic models** exactly
([`00`](./00-overview.md) §4). This is your frontend's half of the data contract.
When the backend shape changes, this type changes — keep them in lockstep.

```
frontend/app/
├── lib/
│   └── types.ts          # ClaimAudit, RagChunk, etc. — mirror backend
│   └── api.ts            # fetch wrapper to the FastAPI backend
├── components/
│   ├── ClaimForm.tsx      # submit a claim
│   ├── ReasoningTrace.tsx  # the whole vertical trace
│   ├── EvidencePanel.tsx   # the RAG chunks with scores + source
│   ├── VerdictBadge.tsx    # color-coded status pill
│   └── AuditDiff.tsx       # draft vs final, corrections highlighted
```

> **Atomic-design nudge:** `VerdictBadge` and `EvidencePanel` are small, reusable
> presentational components. `ReasoningTrace` composes them. Keep data-fetching
> (containers) separate from rendering (presentational). Don't dump everything into
> `page.tsx`.

### 2. Talk to the backend
- A small `api.ts` that POSTs to `http://localhost:8000/api/claims` and fetches results.
- Remember **CORS** must be enabled on the FastAPI side (see [`01`](./01-fase-api-gateway.md)
  gotchas). Different ports = browser blocks it without `CORSMiddleware`.
- Decide server vs client component per Next 16 conventions (read the local docs). The
  form is interactive → client component. The trace render can be server-fetched.

### 3. Render states honestly
The UI must handle every backend outcome:
- `LOW_CONFIDENCE` → "Routed to manual review", neutral, no fake verdict.
- `corrections_applied: true` → visually highlight that the auditor intervened. This is
  the most interesting moment in the whole system — don't bury it.
- Loading / error states (the pipeline can take up to 5s — show progress).

---

## Suggested approach

1. **Mock the backend first.** Hardcode a sample audit JSON (use the [`00`](./00-overview.md)
   §4 shape) and build the entire trace UI against it. This decouples frontend progress
   from backend readiness — you can build Layer 5 in parallel with Layer 4.
2. Build presentational components bottom-up: `VerdictBadge` → `EvidencePanel` →
   `ReasoningTrace`.
3. Wire the real API last, once the components render the mock perfectly.

---

## Definition of Done ✅

- [ ] A form submits a claim to the backend (`POST /api/claims`).
- [ ] The reasoning trace renders **all five stages**: claim, intent+confidence,
      RAG chunks (with source section + page + score), Node 1 draft, Node 2 corrections,
      final verdict.
- [ ] Final verdict is **color-coded** by status (green/red/amber).
- [ ] The **verbatim RAG citation** is displayed alongside the final verdict.
- [ ] `corrections_applied: true` is visually distinct (the auditor caught something).
- [ ] `LOW_CONFIDENCE` claims show a manual-review state, not a fabricated verdict.
- [ ] Loading + error states handled (pipeline may take up to 5s).
- [ ] TypeScript types mirror the backend contract; no `any` on the audit shape.
- [ ] Code written against **Next.js 16** conventions (verified via local docs), not
      remembered Next 14 patterns.

---

## Gotchas

- **The version trap.** Saying it a third time because it matters: Next 16 + React 19 +
  Tailwind v4 differ from older versions. `next.config.ts`, async request APIs, the
  Tailwind v4 CSS-first config — all changed. **Read `node_modules/next/dist/docs/`.**
- **CORS.** The #1 "why won't it connect" bug. Backend must allow the frontend origin.
- **Tailwind v4 is config-less.** No `tailwind.config.js` the old way — it's
  `@import "tailwindcss"` in CSS + `@theme`. Don't paste a v3 config and expect it to work.
- **Don't put logic in the UI.** The verdict, the citation, the corrections — all decided
  by the backend. The frontend *renders*; it never *re-decides*. If you find yourself
  computing a verdict in React, stop — that belongs in Layer 4.
- **Hydration mismatches.** Color-coding by status is fine, but be careful with
  server/client rendering of dynamic data in Next 16 — follow its current guidance.

---

## Dependencies

Already installed (Next 16, React 19, Tailwind v4). You may want a small fetch/data lib,
but native `fetch` is enough for this scope. Add with `pnpm add` if needed.

---

## What this completes

The full pipeline is now end-to-end: **claim in → validated → classified → retrieved →
audited → rendered with citation.** You've built all five layers. Cross-check against
the **Evaluation Metrics** in `smartclaim_core.md` (Classification Accuracy, MRR@2,
Faithfulness Score, Auditor Correction Rate, Latency per Stage) to prepare for delivery.

---

### Prev: [`04-fase-langgraph.md`](./04-fase-langgraph.md) · Back to: [`00-overview.md`](./00-overview.md)

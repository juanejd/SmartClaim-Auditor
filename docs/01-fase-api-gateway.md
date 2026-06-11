# 01 — Phase 1: API Gateway (FastAPI)

> **Layer 1 of 5.** This is the front door of the entire system. Everything else
> depends on this layer producing a clean, validated claim object.

**Prerequisite reading:** [`00-overview.md`](./00-overview.md) §4 (data contracts).

---

## Concept

The API Gateway is the **boundary** between the messy outside world (raw HTTP,
malformed JSON, missing fields) and the clean, typed internal world of the pipeline.
Its single responsibility: **accept a claim, validate it, give it an identity, and
hand a guaranteed-valid object to the rest of the pipeline.**

In FastAPI, this is built on two pillars:
- **Pydantic models** — declarative validation. You describe the shape; FastAPI
  rejects anything that doesn't match with an automatic `422`.
- **ASGI / async** — the server can handle the request without blocking while
  downstream work happens.

---

## Why it exists (the *why* before the code)

Why not just let the classifier receive raw JSON directly? Because of the
**fail-fast principle**. The cheapest place to reject bad data is at the boundary,
*before* you spend CPU loading models and running inference.

A claim with a missing `complaint_text` should die in **microseconds** with a `422`,
not after 4 seconds of pointless pipeline work. The gateway is your bouncer. It
checks IDs at the door so the expensive club inside never deals with troublemakers.

This maps directly to **RF-01**:
> `POST /api/claims` returns `202 + claim_id` in < 200ms; `422` for invalid schema.

Note the **`202 Accepted`**, not `200 OK`. That is deliberate: `202` means "I have
accepted this for processing", which is the honest semantic for a pipeline that may
process asynchronously. Detail matters.

---

## What to build

### 1. Project structure (move beyond `main.py`)
The current `backend/main.py` is the FastAPI tutorial stub. Replace it with a real,
layered structure. Suggested:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app factory + router registration
│   ├── api/
│   │   └── claims.py        # POST /api/claims route
│   ├── models/
│   │   └── claim.py         # Pydantic request/response models
│   ├── services/
│   │   └── claim_store.py   # in-memory or SQLite persistence (start in-memory)
│   └── core/
│       └── config.py        # settings (env-driven)
└── tests/
    └── test_claims_api.py
```

> This is a *Screaming Architecture* nudge: the folder names tell you what the system
> does (claims, audit), not what framework it uses. You will thank yourself in Layer 4.

### 2. The request/response contract
Define Pydantic models that match [`00-overview.md`](./00-overview.md) §4:

- **Request** (`ClaimRequest`): `complaint_text: str`, `contract_clauses: str`.
  Add validation: `complaint_text` must be non-empty, min length (e.g. 10 chars).
- **Response** (`ClaimAccepted`): `claim_id: str` (UUID), `status: str`,
  `received_at: datetime`.

### 3. The endpoint
- `POST /api/claims` → validate → generate `claim_id` (UUID) → store → return
  `202` with `ClaimAccepted`.
- Let FastAPI's automatic validation produce the `422` for free. Do **not**
  hand-roll validation that Pydantic already does.

### 4. Persistence (start simple)
Per the core doc, persistence is **SQLite / JSON files** (university scope). Start
with an **in-memory dict** behind a `claim_store` service interface. Why an interface?
So you can swap in SQLite later without touching the route (RNF-04 thinking applies
internally too).

---

## Suggested approach (TDD — your project is set up for it)

`pytest` is already a dev dependency. Use it. Write the test first:

1. **Red:** test `POST /api/claims` with valid payload → expect `202` + a `claim_id`.
2. **Green:** implement the route until the test passes.
3. **Red:** test invalid payload (missing `complaint_text`) → expect `422`.
4. **Green:** confirm Pydantic handles it.
5. **Refactor:** extract the store, clean up.

Run with: `uv run pytest`. Use FastAPI's `TestClient` (Starlette) — no live server needed.

---

## Definition of Done ✅

- [ ] `POST /api/claims` accepts a valid claim and returns **`202` + a unique `claim_id`**.
- [ ] Invalid payloads (missing/empty required fields) return **`422`** with a clear error body.
- [ ] Response time for ingestion is **< 200ms** (trivial at this stage — no models loaded).
- [ ] A claim, once accepted, can be retrieved by `claim_id` (`GET /api/claims/{id}`).
- [ ] Auto-generated Swagger docs at `/docs` show the endpoint with correct schemas.
- [ ] Tests cover the happy path **and** the `422` path; `uv run pytest` is green.
- [ ] `main.py` no longer contains the `/items/{item_id}` tutorial stub.

---

## Gotchas (learn these now, not at 2am)

- **CORS.** The Next.js frontend (Layer 5) runs on a different port (`:3000`) than
  FastAPI (`:8000`). Without `CORSMiddleware`, the browser will silently block
  requests. Add it now or remember this when Layer 5 "mysteriously" can't reach the API.
- **`202` vs `200`.** FastAPI defaults to `200`. You must set
  `status_code=status.HTTP_202_ACCEPTED` explicitly on the route.
- **UUIDs are strings over the wire.** Generate with `uuid.uuid4()`, serialize as
  `str`. Keep the type consistent in your Pydantic model.
- **Don't store business logic in the route.** The route orchestrates; the service
  stores. Keep the route thin — it will need to call Layers 2–4 later.
- **Use `uv add`, not `pip install`.** The project uses `uv` with a lockfile.
  Bypassing it desyncs `uv.lock`.

---

## Dependencies to add

Already present: `fastapi`, `uvicorn`. You likely need:
```bash
uv add "uvicorn[standard]"   # if you want auto-reload + better perf
# pydantic comes transitively with fastapi (v2)
```
Nothing AI-related yet. Keep this layer lean.

---

## What this unlocks

Once Layer 1 returns a validated claim object, **Layer 2 (Classifier)** has a clean,
typed input to consume. You are ready for [`02-fase-classifier.md`](./02-fase-classifier.md).

---

### Prev: [`00-overview.md`](./00-overview.md) · Next: [`02-fase-classifier.md`](./02-fase-classifier.md)

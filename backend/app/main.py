from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.claims import router as claims_router
from app.api.clauses import router as clauses_router
from app.api.documents import router as documents_router
from app.core.config import settings
from app.db.database import create_all_tables

app = FastAPI(
    title="SmartClaim Auditor API",
    description="Local-only NLP pipeline for auditable claim verdicts.",
    version="0.1.0",
    lifespan=create_all_tables,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip().rstrip("/")
        for origin in settings.ALLOWED_ORIGINS.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(claims_router)
app.include_router(documents_router)
app.include_router(clauses_router)

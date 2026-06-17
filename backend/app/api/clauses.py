import functools
import json
from pathlib import Path

from fastapi import APIRouter, status

_CLAUSES_PATH = Path(__file__).resolve().parent.parent / "data" / "clauses.json"

router = APIRouter(prefix="/api/clauses", tags=["clauses"])


@functools.lru_cache(maxsize=1)
def _load_clauses() -> list:
    with _CLAUSES_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
)
def get_clauses() -> list:
    return _load_clauses()

import re
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

_MANUALS_DIR = Path(__file__).resolve().parent.parent / "data" / "manuals"

_PREFIX_RE = re.compile(r"^\d+_")

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _label_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    label = _PREFIX_RE.sub("", stem)
    return label.replace("_", " ")


@router.get(
    "",
    status_code=status.HTTP_200_OK,
)
def list_documents() -> list[dict]:
    items = []
    for path in sorted(_MANUALS_DIR.iterdir()):
        if path.suffix.lower() == ".pdf":
            items.append(
                {
                    "filename": path.name,
                    "label": _label_from_filename(path.name),
                    "size_bytes": path.stat().st_size,
                }
            )
    return items


@router.get(
    "/{filename}",
    status_code=status.HTTP_200_OK,
)
def get_document(filename: str) -> FileResponse:
    if (
        ".." in filename
        or "/" in filename
        or "\\" in filename
        or filename.startswith("/")
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="document not found",
        )

    candidate = (_MANUALS_DIR / filename).resolve()

    try:
        candidate.relative_to(_MANUALS_DIR.resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="document not found",
        )

    if not candidate.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="document not found",
        )

    return FileResponse(str(candidate), media_type="application/pdf")

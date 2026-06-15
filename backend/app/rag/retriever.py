from pathlib import Path
from langchain_community.vectorstores import FAISS

from app.rag.embeddings import NormalizedMiniLMEmbeddings
from app.models.claim import RagChunk
from app.core.config import FAISS_INDEX_PATH

_vectorstore = None


def _load_data():
    global _vectorstore
    if _vectorstore is None:
        # verificar si el archivo existe
        if (
            Path(FAISS_INDEX_PATH).exists()
            and (Path(FAISS_INDEX_PATH) / "index.faiss").exists()
        ):
            _vectorstore = FAISS.load_local(
                FAISS_INDEX_PATH,
                NormalizedMiniLMEmbeddings(),
                allow_dangerous_deserialization=True,
            )
        else:
            _vectorstore = None


def retrieve(text: str, k: int = 2) -> list[RagChunk]:

    _load_data()

    if _vectorstore is None:
        return []

    # encuentra los textos mas cercanos, por defecto 2
    results_with_score = _vectorstore.similarity_search_with_score(text, k=k)

    results = []
    for doc, score in results_with_score:
        results.append(
            RagChunk(
                text=doc.page_content,
                source_section=doc.metadata.get("source_section", "unknown"),
                page=doc.metadata.get("page", 0),
                score=float(score),
            )
        )

    return results

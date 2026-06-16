from pathlib import Path
from langchain_community.vectorstores import FAISS

from app.rag.embeddings import NormalizedMiniLMEmbeddings
from app.models.claim import RagChunk
from app.core.config import FAISS_INDEX_PATH, RAG_TOP_K

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


def retrieve(text: str, k: int = RAG_TOP_K) -> list[RagChunk]:

    _load_data()

    if _vectorstore is None:
        return []

    # encuentra los textos mas cercanos, por defecto 2
    results_with_score = _vectorstore.similarity_search_with_score(text, k=k)

    results = []
    for doc, distance in results_with_score:
        similarity = max(0.0, min(1.0, 1.0 - float(distance) / 2.0))
        results.append(
            RagChunk(
                text=doc.page_content,
                source_section=doc.metadata.get("source_section", "unknown"),
                page=doc.metadata.get("page", 0),
                score=similarity,
            )
        )

    return results

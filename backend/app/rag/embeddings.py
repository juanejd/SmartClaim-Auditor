import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings

from app.core.config import EMBEDDING_MODEL

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _encode_normalized(texts: list[str]) -> np.ndarray:
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True)

    if not isinstance(embeddings, np.ndarray):
        embeddings = np.array(embeddings)
    faiss.normalize_L2(embeddings)
    return embeddings


class NormalizedMiniLMEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return _encode_normalized(texts).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


def embed_texts(texts: list[str]) -> np.ndarray:
    return _encode_normalized(texts)

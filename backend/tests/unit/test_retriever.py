import pytest
import app.rag.retriever as retriever_module
from unittest.mock import patch
from langchain_community.vectorstores import FAISS
from app.rag.embeddings import NormalizedMiniLMEmbeddings
from app.rag.retriever import retrieve
from app.models.claim import RagChunk


@pytest.fixture(autouse=True)
def reset_vectorstore_singleton():
    original = retriever_module._vectorstore
    retriever_module._vectorstore = None
    yield
    retriever_module._vectorstore = original


@pytest.fixture
def mock_index_and_metadata(tmp_path):
    # Create fake langchain faiss index
    index_path = tmp_path / "index"

    texts = [
        "This is about refund policies.",
        "This is about delayed shipping.",
        "This is an irrelevant chunk.",
    ]
    metadatas = [
        {"source_section": "policy.pdf", "page": 1},
        {"source_section": "shipping.pdf", "page": 2},
        {"source_section": "other.pdf", "page": 3},
    ]

    embeddings = NormalizedMiniLMEmbeddings()
    vectorstore = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
    vectorstore.save_local(str(index_path))

    return index_path, texts, embeddings


def test_retrieve_returns_k_chunks(mock_index_and_metadata):
    index_path, texts, embeddings = mock_index_and_metadata

    with patch("app.rag.retriever.FAISS_INDEX_PATH", str(index_path)):
        results = retrieve("delayed shipping", k=2)

        assert len(results) == 2
        assert isinstance(results[0], RagChunk)
        # Should match chunk 1 ("delayed shipping")
        assert results[0].text == "This is about delayed shipping."
        assert results[0].source_section == "shipping.pdf"
        assert results[0].page == 2
        assert hasattr(results[0], "score")


def test_relevant_chunk_ranks_first(mock_index_and_metadata):
    index_path, texts, embeddings = mock_index_and_metadata

    with patch("app.rag.retriever.FAISS_INDEX_PATH", str(index_path)):
        results = retrieve("refund policies", k=2)

        # The exact match vector should rank first
        assert results[0].text == "This is about refund policies."


def test_scores_in_cosine_range(mock_index_and_metadata):
    index_path, texts, embeddings = mock_index_and_metadata

    with patch("app.rag.retriever.FAISS_INDEX_PATH", str(index_path)):
        results = retrieve("refund policies", k=3)

        for r in results:
            assert 0.0 <= r.score <= 1.0


def test_best_match_score_near_one(mock_index_and_metadata):
    index_path, texts, embeddings = mock_index_and_metadata

    with patch("app.rag.retriever.FAISS_INDEX_PATH", str(index_path)):
        results = retrieve("refund policies", k=1)

        assert results[0].score >= 0.9

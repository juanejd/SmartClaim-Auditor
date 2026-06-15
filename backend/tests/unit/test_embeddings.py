import numpy as np
import pytest
from app.rag.embeddings import embed_texts, NormalizedMiniLMEmbeddings


def test_embed_texts_returns_normalized_vectors():
    texts = ["This is a test document.", "Another piece of text."]
    embeddings = embed_texts(texts)

    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (2, 384)

    norms = np.linalg.norm(embeddings, axis=1)
    for norm in norms:
        assert pytest.approx(norm, 0.01) == 1.0


def test_normalized_minilm_embeddings_returns_normalized_list():
    texts = ["This is a test document.", "Another piece of text."]
    emb_model = NormalizedMiniLMEmbeddings()
    embeddings = emb_model.embed_documents(texts)

    assert isinstance(embeddings, list)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384

    # Check L2 normalization
    for emb in embeddings:
        norm = np.linalg.norm(emb)
        assert pytest.approx(norm, 0.01) == 1.0


def test_normalized_minilm_embeddings_embed_query():
    emb_model = NormalizedMiniLMEmbeddings()
    emb = emb_model.embed_query("Query test")

    assert isinstance(emb, list)
    assert len(emb) == 384
    norm = np.linalg.norm(emb)
    assert pytest.approx(norm, 0.01) == 1.0

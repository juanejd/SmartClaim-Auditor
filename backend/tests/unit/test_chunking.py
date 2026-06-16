from app.rag.chunking import chunk_text
from app.core.config import RAG_CHUNK_SIZE

def test_chunk_text_splits_correctly():
    # Create a dummy text that is 3 times the chunk size minus some overlap
    dummy_text = "A" * (RAG_CHUNK_SIZE * 2 + 100)
    
    chunks = chunk_text(dummy_text)
    
    # We should have more than 1 chunk
    assert len(chunks) > 1
    
    # Each chunk should not exceed RAG_CHUNK_SIZE
    for chunk in chunks:
        assert len(chunk) <= RAG_CHUNK_SIZE
        
    # Check overlap approximately if possible, or at least that chunks are produced.
    # The first chunk should be the beginning.
    assert chunks[0].startswith("AAAA")

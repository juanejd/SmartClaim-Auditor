ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
COMPLAINT_TEXT_MIN_LENGTH: int = 10
CLASSIFIER_THRESHOLD: float = 0.7

RAG_CHUNK_SIZE: int = 2048
RAG_CHUNK_OVERLAP: int = 800
RAG_TOP_K: int = 2
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
FAISS_INDEX_PATH: str = "app/data/index"
METADATA_PATH: str = "app/data/index/metadata.json"
DATA_DIR: str = "app/data"

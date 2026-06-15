from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )


def chunk_text(text: str) -> list[str]:

    splitter = get_text_splitter()
    return splitter.split_text(text)

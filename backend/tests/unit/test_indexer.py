from unittest.mock import patch

from langchain_core.documents import Document

from app.rag.indexer import build_index


def test_build_index_creates_files(tmp_path):
    pdf_dir = tmp_path / "manuals"
    output_dir = tmp_path / "index"
    pdf_dir.mkdir()
    output_dir.mkdir()

    # Create dummy pdf
    (pdf_dir / "test.pdf").touch()

    # Mock DirectoryLoader
    with patch("app.rag.indexer.DirectoryLoader") as mock_loader_class:
        mock_loader_inst = mock_loader_class.return_value
        # Return a sample Document with metadata mapped correctly
        mock_loader_inst.load.return_value = [
            Document(
                page_content="This is some test content for the PDF.",
                metadata={"source": "test.pdf", "page": 0},
            )
        ]

        build_index(pdf_dir, output_dir)

    faiss_file = output_dir / "index.faiss"
    pkl_file = output_dir / "index.pkl"

    assert faiss_file.exists()
    assert pkl_file.exists()

    # We can also check if we can load it
    from langchain_community.vectorstores import FAISS
    from app.rag.embeddings import NormalizedMiniLMEmbeddings

    loaded = FAISS.load_local(
        str(output_dir),
        NormalizedMiniLMEmbeddings(),
        allow_dangerous_deserialization=True,
    )

    res = loaded.similarity_search("test content", k=1)
    assert len(res) == 1
    assert "This is some test content" in res[0].page_content
    # Mapped metadata check
    assert res[0].metadata["source_section"] == "test.pdf"
    assert res[0].metadata["page"] == 1


def test_new_pdf_updates_retrieval(tmp_path):
    pdf_dir = tmp_path / "manuals"
    output_dir = tmp_path / "index"
    pdf_dir.mkdir()
    output_dir.mkdir()

    (pdf_dir / "new.pdf").touch()

    with patch("app.rag.indexer.DirectoryLoader") as mock_loader_class:
        mock_loader_inst = mock_loader_class.return_value
        mock_loader_inst.load.return_value = [
            Document(
                page_content="Brand new PDF content.",
                metadata={"source": "new.pdf", "page": 0},
            )
        ]

        build_index(pdf_dir, output_dir)

    faiss_file = output_dir / "index.faiss"
    assert faiss_file.exists()

    from langchain_community.vectorstores import FAISS
    from app.rag.embeddings import NormalizedMiniLMEmbeddings

    loaded = FAISS.load_local(
        str(output_dir),
        NormalizedMiniLMEmbeddings(),
        allow_dangerous_deserialization=True,
    )

    res = loaded.similarity_search("Brand new PDF content", k=1)
    assert len(res) == 1
    assert "Brand new" in res[0].page_content

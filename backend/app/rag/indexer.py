from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS

from app.rag.chunking import get_text_splitter
from app.rag.embeddings import NormalizedMiniLMEmbeddings


def build_index(pdf_dir: Path, output_dir: Path):
    # cargar todos los pdfs
    loader = DirectoryLoader(str(pdf_dir), glob="**/*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()

    if not docs:
        embeddings = NormalizedMiniLMEmbeddings()
        vectorstore = FAISS.from_texts(["__empty__"], embeddings)
        vectorstore.save_local(str(output_dir))
        return

    # verificar de que archivo y pagina proviene
    for doc in docs:
        source_path = Path(doc.metadata.get("source", ""))
        doc.metadata["source_section"] = (
            source_path.name if source_path.name else "unknown.pdf"
        )
        page_val = doc.metadata.get("page", 0)
        doc.metadata["page"] = int(page_val) + 1

    splitter = get_text_splitter()
    splits = splitter.split_documents(docs)

    if not splits:
        embeddings = NormalizedMiniLMEmbeddings()
        vectorstore = FAISS.from_texts(["__empty__"], embeddings)
        vectorstore.save_local(str(output_dir))
        return

    embeddings = NormalizedMiniLMEmbeddings()
    vectorstore = FAISS.from_documents(splits, embeddings)
    vectorstore.save_local(str(output_dir))


if __name__ == "__main__":
    import argparse
    from app.core.config import DATA_DIR

    parser = argparse.ArgumentParser(description="Build FAISS index from PDFs")
    parser.add_argument(
        "--pdf-dir",
        type=str,
        default=str(Path(DATA_DIR) / "manuals"),
        help="Directory containing PDFs",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(DATA_DIR) / "index"),
        help="Directory to save the index",
    )

    args = parser.parse_args()

    pdf_path = Path(args.pdf_dir)
    out_path = Path(args.output_dir)

    pdf_path.mkdir(parents=True, exist_ok=True)
    out_path.mkdir(parents=True, exist_ok=True)

    print(f"Building index from {pdf_path} to {out_path}...")
    build_index(pdf_path, out_path)
    print("Done!")

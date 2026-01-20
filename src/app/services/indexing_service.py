"""Service functions for indexing documents into the vector database."""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

from ..core.retrieval.vector_store import index_documents


def index_pdf_file(file_path: Path, namespace: str = "") -> int:
    """Load a PDF from disk and index it into the vector DB in a specific namespace.

    Args:
        file_path: Path to the PDF file on disk.
        namespace: Pinecone namespace for session isolation.

    Returns:
        Number of document chunks indexed.
    """
    loader = PyPDFLoader(str(file_path))
    docs = loader.load()
    return index_documents(docs, namespace=namespace)

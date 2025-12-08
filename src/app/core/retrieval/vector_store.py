"""Vector store wrapper for Pinecone integration with LangChain."""

from functools import lru_cache
from typing import List

from pinecone import Pinecone
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

from ..config import get_settings


@lru_cache(maxsize=1)
def _get_vector_store() -> PineconeVectorStore:
    """Create a PineconeVectorStore instance configured from settings."""
    settings = get_settings()

    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=settings.openai_api_key,
    )

    return PineconeVectorStore(
        index=index,
        embedding=embeddings,
    )


def get_retriever(k: int | None = None) -> PineconeVectorStore:
    """Get a Pinecone retriever instance.

    Args:
        k: Number of documents to retrieve (defaults to config value).

    Returns:
        PineconeVectorStore instance configured as a retriever.
    """
    settings = get_settings()
    if k is None:
        k = settings.retrieval_k

    vector_store = _get_vector_store()
    return vector_store.as_retriever(search_kwargs={"k": k})


def retrieve(query: str, k: int | None = None) -> List[Document]:
    """Retrieve documents from Pinecone for a given query.

    Args:
        query: Search query string.
        k: Number of documents to retrieve (defaults to config value).

    Returns:
        List of Document objects with metadata (including page numbers).
    """
    retriever = get_retriever(k=k)
    return retriever.invoke(query)


def index_documents(docs: List[Document]) -> int:
    """Index a list of Document objects into the Pinecone vector store.

    Args:
        docs: Documents to embed and upsert into the vector index.

    Returns:
        The number of documents indexed.
    """
    vector_store = _get_vector_store()
    vector_store.add_documents(docs)
    return len(docs)

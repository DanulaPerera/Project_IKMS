"""Vector store wrapper for Pinecone integration with LangChain."""

from pathlib import Path
from functools import lru_cache
from typing import List

from pinecone import Pinecone
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


from ..config import get_settings


@lru_cache(maxsize=1)
def _get_vector_store() -> PineconeVectorStore:
    """Create a PineconeVectorStore instance configured from settings."""
    settings = get_settings()

    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)

    embeddings = OpenAIEmbeddings(
        model=settings.openai_embedding_model_name,
        api_key=settings.openai_api_key,
    )

    return PineconeVectorStore(
        index=index,
        embedding=embeddings,
    )

def get_retriever(k: int | None = None, namespace: str = ""):
    """Get a Pinecone retriever instance for a specific namespace.

    Args:
        k: Number of documents to retrieve (defaults to config value).
        namespace: Pinecone namespace to retrieve from (for session isolation).

    Returns:
        PineconeVectorStore instance configured as a retriever.
    """
    settings = get_settings()
    if k is None:
        k = settings.retrieval_k

    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)
    embeddings = OpenAIEmbeddings(
        model=settings.openai_embedding_model_name,
        api_key=settings.openai_api_key,
    )
    
    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings,
        namespace=namespace
    )
    return vector_store.as_retriever(search_kwargs={"k": k})


def retrieve(query: str, k: int | None = None, namespace: str = "") -> List[Document]:
    """Retrieve documents from Pinecone for a given query in a specific namespace.

    Args:
        query: Search query string.
        k: Number of documents to retrieve (defaults to config value).
        namespace: Pinecone namespace to retrieve from (for session isolation).

    Returns:
        List of Document objects with metadata (including page numbers).
    """
    retriever = get_retriever(k=k, namespace=namespace)
    return retriever.invoke(query)

def index_documents(docs: List[Document], namespace: str = "") -> int:
    """Index a list of Document objects into the Pinecone vector store in a specific namespace.

    Args:
        docs: Documents to embed and upsert into the vector index.
        namespace: Pinecone namespace to index into (for session isolation).

    Returns:
        The number of documents indexed.
    """

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(docs)

    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)
    embeddings = OpenAIEmbeddings(
        model=settings.openai_embedding_model_name,
        api_key=settings.openai_api_key,
    )
    
    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings,
        namespace=namespace
    )
    vector_store.add_documents(texts)
    return len(texts)

def check_namespace_has_vectors(namespace: str) -> bool:
    """Check if a specific namespace contains any vectors.
    
    Args:
        namespace: The namespace to check.
    
    Returns:
        True if the namespace has vectors, False otherwise.
    """
    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)
    
    stats = index.describe_index_stats()
    namespaces = stats.get('namespaces', {})
    
    if namespace not in namespaces:
        return False
    
    vector_count = namespaces[namespace].get('vector_count', 0)
    return vector_count > 0

def clear_namespace(namespace: str) -> int:
    """Clear all vectors from a specific namespace.
    
    Args:
        namespace: The namespace to clear.
    
    Returns:
        The number of vectors that were in the namespace before clearing.
    """
    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)
    
    # Get vector count before deletion
    stats = index.describe_index_stats()
    namespaces = stats.get('namespaces', {})
    vector_count = namespaces.get(namespace, {}).get('vector_count', 0)
    
    if vector_count > 0:
        try:
            index.delete(delete_all=True, namespace=namespace)
        except Exception as e:
            print(f"Warning: Could not delete from namespace '{namespace}': {e}")
    
    return vector_count
 
 
def check_index_has_vectors() -> bool:
    """Check if the Pinecone index contains any vectors across all namespaces."""
    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)
    stats = index.describe_index_stats()
    return stats.get('total_vector_count', 0) > 0

def clear_index() -> int:
    """Clear all vectors from the Pinecone index across all namespaces."""
    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    index = pc.Index(settings.pinecone_index_name)
    stats = index.describe_index_stats()
    total_vectors = stats.get('total_vector_count', 0)
    namespaces = stats.get('namespaces', {})
    if not namespaces:
        try:
            index.delete(delete_all=True, namespace="")
        except Exception:
            pass
    else:
        for namespace_name in namespaces.keys():
            try:
                index.delete(delete_all=True, namespace=namespace_name)
            except Exception as e:
                print(f"Warning: Could not delete from namespace '{namespace_name}': {e}")
    return total_vectors

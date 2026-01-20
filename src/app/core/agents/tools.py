"""Tools available to agents in the multi-agent RAG system."""

from langchain_core.tools import tool

from ..retrieval.vector_store import retrieve, check_namespace_has_vectors
from ..retrieval.serialization import serialize_chunks


def create_retrieval_tool(session_id: str = ""):
    """Create a retrieval tool for a specific session.
    
    Args:
        session_id: The session ID to create the tool for.
        
    Returns:
        A retrieval tool bound to the session's namespace.
    """
    namespace = f"session_{session_id}" if session_id else ""
    
    @tool(response_format="content_and_artifact")
    def retrieval_tool(query: str):
        """Search the vector database for relevant document chunks.

        This tool retrieves the top 4 most relevant chunks from the Pinecone
        vector store based on the query. The chunks are formatted with page
        numbers and indices for easy reference.

        Args:
            query: The search query string to find relevant document chunks.

        Returns:
            Tuple of (serialized_content, artifact) where:
            - serialized_content: A formatted string containing the retrieved chunks
              with metadata. Format: "Chunk 1 (page=X): ...\n\nChunk 2 (page=Y): ..."
            - artifact: List of Document objects with full metadata for reference
        """
        from ...services.session_manager import session_manager
        
        # Check if session has a document
        if session_id and not session_manager.has_document(session_id):
            error_message = (
                "❌ No document uploaded for this conversation yet.\n\n"
                "Please upload a PDF document using the 'Upload Document' button "
                "before asking questions. Each conversation requires its own document."
            )
            return error_message, []
        
        # Check if namespace has vectors
        if session_id and not check_namespace_has_vectors(namespace):
            error_message = (
                "❌ No document found for this session.\n\n"
                "The document may have been deleted or not uploaded yet. "
                "Please upload a PDF document to continue."
            )
            return error_message, []
        
        # Retrieve documents from session namespace
        docs = retrieve(query, k=4, namespace=namespace)
        
        # Handle case where retrieve returns empty results
        if not docs:
            error_message = (
                "⚠️ No relevant information found in the uploaded document.\n\n"
                "This could mean:\n"
                "- The question is outside the scope of the uploaded document\n"
                "- Try rephrasing your question\n"
                "- Consider uploading a different document"
            )
            return error_message, []

        # Serialize chunks into formatted string (content)
        context = serialize_chunks(docs)

        # Return tuple: (serialized content, artifact documents)
        # This follows LangChain's content_and_artifact response format
        return context, docs
    
    return retrieval_tool


# Legacy tool for backward compatibility (non-conversational flows)
@tool(response_format="content_and_artifact") 
def retrieval_tool(query: str):
    """Search the vector database for relevant document chunks (global namespace)."""
    docs = retrieve(query, k=4, namespace="")
    if not docs:
        return "No documents found.", []
    context = serialize_chunks(docs)
    return context, docs

"""Service for managing session-document bindings and enforcing limits."""

from typing import Dict, Optional
from datetime import datetime


class SessionManager:
    """Manage session-document bindings and enforce session limits."""
    
    def __init__(self, max_sessions: int = 3):
        """Initialize the session manager.
        
        Args:
            max_sessions: Maximum number of sessions with documents allowed.
        """
        self.max_sessions = max_sessions
        # session_id -> {document_name, upload_time, vector_count, namespace}
        self.sessions: Dict[str, dict] = {}
    
    def has_document(self, session_id: str) -> bool:
        """Check if session has an uploaded document.
        
        Args:
            session_id: The session ID to check.
            
        Returns:
            True if session has a document, False otherwise.
        """
        return session_id in self.sessions
    
    def add_session_document(self, session_id: str, document_name: str, vector_count: int):
        """Register document for session. Evict oldest if limit reached.
        
        Args:
            session_id: The session ID.
            document_name: Name of the uploaded document.
            vector_count: Number of vectors indexed.
        """
        from ..core.retrieval.vector_store import clear_namespace
        
        # Check if we need to evict
        if len(self.sessions) >= self.max_sessions and session_id not in self.sessions:
            # Evict oldest session
            oldest = min(self.sessions.items(), key=lambda x: x[1]['upload_time'])
            oldest_session_id, oldest_data = oldest
            
            print(f"📊 Session limit reached. Evicting oldest session: {oldest_session_id}")
            print(f"   Document: {oldest_data['document_name']}")
            
            # Clear the namespace
            namespace = oldest_data['namespace']
            cleared = clear_namespace(namespace)
            print(f"   Cleared {cleared} vectors from namespace {namespace}")
            
            # Remove from tracking
            del self.sessions[oldest_session_id]
        
        # Add or update session
        namespace = f"session_{session_id}"
        self.sessions[session_id] = {
            'document_name': document_name,
            'upload_time': datetime.now(),
            'vector_count': vector_count,
            'namespace': namespace
        }
        
        print(f"✅ Registered document '{document_name}' for session {session_id}")
        print(f"   Active sessions: {len(self.sessions)}/{self.max_sessions}")
    
    def remove_session(self, session_id: str):
        """Remove session and clear its namespace.
        
        Args:
            session_id: The session ID to remove.
        """
        if session_id in self.sessions:
            from ..core.retrieval.vector_store import clear_namespace
            
            session_data = self.sessions[session_id]
            namespace = session_data['namespace']
            
            # Clear Pinecone namespace
            cleared = clear_namespace(namespace)
            print(f"🗑️  Cleared session {session_id}: {cleared} vectors deleted")
            
            del self.sessions[session_id]
    
    def get_session_count(self) -> int:
        """Get the number of active sessions.
        
        Returns:
            Number of sessions with documents.
        """
        return len(self.sessions)
    
    def get_session_info(self, session_id: str) -> Optional[dict]:
        """Get information about a specific session.
        
        Args:
            session_id: The session ID.
            
        Returns:
            Session info dict or None if not found.
        """
        return self.sessions.get(session_id)
    
    def get_all_sessions(self) -> Dict[str, dict]:
        """Get all active sessions.
        
        Returns:
            Dictionary of session_id -> session info.
        """
        return self.sessions.copy()


# Global instance
session_manager = SessionManager(max_sessions=3)

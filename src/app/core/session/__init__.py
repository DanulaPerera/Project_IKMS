"""Session storage for managing conversation state across multiple turns.

This module provides an in-memory storage solution for conversation sessions.
Each session maintains a history of question-answer turns and associated metadata.

Note: Sessions are stored in memory and will be lost on server restart.
For production use, consider migrating to persistent storage (Redis, database, etc.).
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid


@dataclass
class ConversationSession:
    """Represents a conversation session with history.
    
    Attributes:
        session_id: Unique identifier for the session
        history: List of conversation turns (question, answer, context, etc.)
        created_at: Timestamp when session was created
        last_accessed: Timestamp of last interaction
    """
    session_id: str
    history: List[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    
    def add_turn(self, turn_data: dict) -> None:
        """Add a conversation turn to the session history."""
        self.history.append(turn_data)
        self.last_accessed = datetime.now()
    
    def clear_history(self) -> None:
        """Clear all conversation history for this session."""
        self.history.clear()
        self.last_accessed = datetime.now()


class SessionStore:
    """In-memory storage for conversation sessions.
    
    This class manages multiple conversation sessions, providing CRUD operations
    and automatic cleanup of old sessions.
    
    Attributes:
        _sessions: Dictionary mapping session IDs to ConversationSession objects
        _max_sessions: Maximum number of sessions to keep in memory
    """
    
    def __init__(self, max_sessions: int = 100):
        """Initialize the session store.
        
        Args:
            max_sessions: Maximum number of sessions before cleanup is triggered
        """
        self._sessions: Dict[str, ConversationSession] = {}
        self._max_sessions = max_sessions
    
    def create_session(self) -> str:
        """Create a new session and return its ID.
        
        Returns:
            Unique session ID (UUID4)
        """
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = ConversationSession(session_id=session_id)
        
        # Cleanup if we exceed max sessions
        if len(self._sessions) > self._max_sessions:
            self._cleanup_oldest_sessions()
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Retrieve a session by ID.
        
        Args:
            session_id: The session identifier
            
        Returns:
            ConversationSession if found, None otherwise
        """
        session = self._sessions.get(session_id)
        if session:
            session.last_accessed = datetime.now()
        return session
    
    def add_turn(self, session_id: str, turn_data: dict) -> None:
        """Add a conversation turn to session history.
        
        Args:
            session_id: The session identifier
            turn_data: Dictionary containing turn information (question, answer, etc.)
            
        Raises:
            ValueError: If session_id is not found
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        session.add_turn(turn_data)
    
    def clear_session(self, session_id: str) -> None:
        """Clear all history for a session.
        
        Args:
            session_id: The session identifier
            
        Raises:
            ValueError: If session_id is not found
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        session.clear_history()
    
    def delete_session(self, session_id: str) -> None:
        """Delete a session completely.
        
        Args:
            session_id: The session identifier
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def get_all_sessions(self) -> List[str]:
        """Get list of all active session IDs.
        
        Returns:
            List of session ID strings
        """
        return list(self._sessions.keys())
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Remove sessions older than max_age_hours.
        
        Args:
            max_age_hours: Maximum age in hours for session retention
            
        Returns:
            Number of sessions cleaned up
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        old_session_ids = [
            sid for sid, session in self._sessions.items()
            if session.last_accessed < cutoff_time
        ]
        
        for sid in old_session_ids:
            del self._sessions[sid]
        
        return len(old_session_ids)
    
    def _cleanup_oldest_sessions(self, keep_count: int = None) -> None:
        """Remove oldest sessions to maintain max_sessions limit.
        
        Args:
            keep_count: Number of sessions to keep (defaults to max_sessions - 10)
        """
        if keep_count is None:
            keep_count = max(self._max_sessions - 10, 50)
        
        # Sort sessions by last_accessed and remove oldest
        sorted_sessions = sorted(
            self._sessions.items(),
            key=lambda x: x[1].last_accessed,
            reverse=True
        )
        
        # Keep only the most recent sessions
        sessions_to_keep = dict(sorted_sessions[:keep_count])
        self._sessions = sessions_to_keep


# Global singleton instance
_session_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """Get the global session store instance (singleton pattern).
    
    Returns:
        Global SessionStore instance
    """
    global _session_store
    if _session_store is None:
        _session_store = SessionStore()
    return _session_store


def reset_session_store() -> None:
    """Reset the global session store (useful for testing)."""
    global _session_store
    _session_store = None

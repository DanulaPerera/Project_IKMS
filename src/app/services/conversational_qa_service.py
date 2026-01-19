"""Service layer for conversational QA operations.

This module provides high-level functions for managing conversational question-answering
flows with session management and history tracking.
"""

from datetime import datetime
from typing import Dict, Any

from ..core.agents.graph import run_conversational_qa_flow
from ..core.session import get_session_store


def answer_conversational_question(
    question: str,
    session_id: str | None = None
) -> Dict[str, Any]:
    """Process a conversational question with history support.
    
    This function:
    1. Retrieves or creates a conversation session
    2. Fetches conversation history for context
    3. Runs the conversational QA flow with history
    4. Saves the new turn to session history
    5. Returns the complete result including session metadata
    
    Args:
        question: The user's question
        session_id: Optional session identifier (creates new session if None)
        
    Returns:
        Dictionary with keys:
        - answer: Final verified answer
        - context: Retrieved context
        - session_id: Session identifier
        - turn_number: Current turn number
        - history_used: Whether history influenced the answer
        
    Raises:
        ValueError: If session_id is provided but not found
    """
    store = get_session_store()
    
    # Get or create session
    if session_id:
        session = store.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        history = session.history
    else:
        session_id = store.create_session()
        history = []
    
    # Run conversational flow
    result = run_conversational_qa_flow(
        question=question,
        history=history,
        session_id=session_id
    )
    
    # Extract context excerpt for storage (first 200 chars)
    context_excerpt = result.get("context", "")[:200] if result.get("context") else ""
    
    # Add turn to session history
    turn_data = {
        "turn": result["turn_number"],
        "question": question,
        "answer": result["answer"],
        "context_used": [context_excerpt] if context_excerpt else [],
        "timestamp": datetime.now().isoformat()
    }
    store.add_turn(session_id, turn_data)
    
    # Return result with metadata
    return {
        "answer": result["answer"],
        "context": result.get("context", ""),
        "session_id": session_id,
        "turn_number": result["turn_number"],
        "history_used": len(history) > 0
    }


def get_conversation_history(session_id: str) -> Dict[str, Any]:
    """Retrieve full conversation history for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dictionary with keys:
        - session_id: Session identifier
        - turns: List of conversation turns
        - created_at: Session creation timestamp
        - total_turns: Total number of turns in conversation
        
    Raises:
        ValueError: If session_id is not found
    """
    store = get_session_store()
    session = store.get_session(session_id)
    
    if not session:
        raise ValueError(f"Session {session_id} not found")
    
    return {
        "session_id": session_id,
        "turns": session.history,
        "created_at": session.created_at.isoformat(),
        "total_turns": len(session.history)
    }


def create_new_session() -> str:
    """Create a new conversation session.
    
    Returns:
        New session ID
    """
    store = get_session_store()
    return store.create_session()


def clear_session_history(session_id: str) -> None:
    """Clear all history for a session.
    
    Args:
        session_id: Session identifier
        
    Raises:
        ValueError: If session_id is not found
    """
    store = get_session_store()
    store.clear_session(session_id)

"""LangGraph state schema for the multi-agent QA flow."""

from typing import TypedDict


class QAState(TypedDict):
    """State schema for the conversational multi-agent QA flow.

    The state flows through three agents:
    1. Retrieval Agent: populates `context` from `question` (with conversation history awareness)
    2. Summarization Agent: generates `draft_answer` from `question` + `context` + `history`
    3. Verification Agent: produces final `answer` from `question` + `context` + `draft_answer` + `history`
    
    Conversation memory fields enable multi-turn interactions where agents
    can understand references to previous turns (e.g., "it", "that method", etc.).
    """

    # Core QA fields
    question: str
    context: str | None
    draft_answer: str | None
    answer: str | None
    
    # Conversation memory fields
    history: list[dict] | None  # Previous conversation turns
    conversation_summary: str | None  # Compressed history (future feature)
    session_id: str | None  # Unique conversation identifier
    turn_number: int | None  # Current turn number in conversation

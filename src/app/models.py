from pydantic import BaseModel


class QuestionRequest(BaseModel):
    """Request body for the `/qa` endpoint.

    The PRD specifies a single field named `question` that contains
    the user's natural language question about the vector databases paper.
    """

    question: str


class QAResponse(BaseModel):
    """Response body for the `/qa` endpoint.

    From the API consumer's perspective we only expose the final,
    verified answer plus some metadata (e.g. context snippets).
    Internal draft answers remain inside the agent pipeline.
    """

    answer: str
    context: str


# ==============================================================================
# Conversational QA Models
# ==============================================================================

class ConversationTurn(BaseModel):
    """Single turn in a conversation.
    
    Represents one question-answer exchange with metadata.
    """
    turn: int
    question: str
    answer: str
    context_used: list[str] = []
    timestamp: str


class ConversationalQARequest(BaseModel):
    """Request body for the `/qa/conversation` endpoint.
    
    Supports multi-turn conversations by optionally including
    a session_id to continue an existing conversation.
    """
    question: str
    session_id: str | None = None  # If None, creates new session


class ConversationalQAResponse(BaseModel):
    """Response body for the `/qa/conversation` endpoint.
    
    Returns the answer along with session metadata to support
    tracking conversation state on the client side.
    """
    answer: str
    context: str
    session_id: str
    turn_number: int
    history_used: bool  # Indicates if previous turns influenced answer


class ConversationHistory(BaseModel):
    """Full conversation history for a session.
    
    Used by the `/qa/session/{session_id}/history` endpoint.
    """
    session_id: str
    turns: list[ConversationTurn]
    created_at: str
    total_turns: int


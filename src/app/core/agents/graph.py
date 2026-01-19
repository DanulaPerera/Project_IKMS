"""LangGraph orchestration for the linear multi-agent QA flow."""

from functools import lru_cache
from typing import Any, Dict

from langgraph.constants import END, START
from langgraph.graph import StateGraph

from .agents import retrieval_node, summarization_node, verification_node
from .state import QAState


def create_qa_graph() -> Any:
    """Create and compile the linear multi-agent QA graph.

    The graph executes in order:
    1. Retrieval Agent: gathers context from vector store
    2. Summarization Agent: generates draft answer from context
    3. Verification Agent: verifies and corrects the answer

    Returns:
        Compiled graph ready for execution.
    """
    builder = StateGraph(QAState)

    # Add nodes for each agent
    builder.add_node("retrieval", retrieval_node)
    builder.add_node("summarization", summarization_node)
    builder.add_node("verification", verification_node)

    # Define linear flow: START -> retrieval -> summarization -> verification -> END
    builder.add_edge(START, "retrieval")
    builder.add_edge("retrieval", "summarization")
    builder.add_edge("summarization", "verification")
    builder.add_edge("verification", END)

    return builder.compile()


@lru_cache(maxsize=1)
def get_qa_graph() -> Any:
    """Get the compiled QA graph instance (singleton via LRU cache)."""
    return create_qa_graph()


def run_qa_flow(question: str) -> Dict[str, Any]:
    """Run the complete multi-agent QA flow for a question.

    This is the main entry point for the QA system. It:
    1. Initializes the graph state with the question
    2. Executes the linear agent flow (Retrieval -> Summarization -> Verification)
    3. Extracts and returns the final results

    Args:
        question: The user's question about the vector databases paper.

    Returns:
        Dictionary with keys:
        - `answer`: Final verified answer
        - `draft_answer`: Initial draft answer from summarization agent
        - `context`: Retrieved context from vector store
    """
    graph = get_qa_graph()

    initial_state: QAState = {
        "question": question,
        "context": None,
        "draft_answer": None,
        "answer": None,
    }

    final_state = graph.invoke(initial_state)

    return final_state


# ==============================================================================
# Conversational QA Flow (History-Aware)
# ==============================================================================

def create_conversational_qa_graph() -> Any:
    """Create and compile the conversational multi-agent QA graph.
    
    This graph is history-aware and uses conversational agents that can
    understand references to previous turns.
    
    The graph executes in order:
    1. Conversational Retrieval Agent: gathers context with history awareness
    2. Conversational Summarization Agent: generates draft answer using history
    3. Conversational Verification Agent: verifies answer maintaining coherence
    
    Returns:
        Compiled graph ready for execution.
    """
    from .agents import (
        conversational_retrieval_node,
        conversational_summarization_node,
        conversational_verification_node,
    )
    
    builder = StateGraph(QAState)
    
    # Add conversational agent nodes
    builder.add_node("retrieval", conversational_retrieval_node)
    builder.add_node("summarization", conversational_summarization_node)
    builder.add_node("verification", conversational_verification_node)
    
    # Define linear flow: START -> retrieval -> summarization -> verification -> END
    builder.add_edge(START, "retrieval")
    builder.add_edge("retrieval", "summarization")
    builder.add_edge("summarization", "verification")
    builder.add_edge("verification", END)
    
    return builder.compile()


@lru_cache(maxsize=1)
def get_conversational_qa_graph() -> Any:
    """Get the compiled conversational QA graph instance (singleton via LRU cache)."""
    return create_conversational_qa_graph()


def run_conversational_qa_flow(
    question: str,
    history: list[dict] | None = None,
    session_id: str | None = None
) -> Dict[str, Any]:
    """Run the conversational multi-agent QA flow for a question.
    
    This function supports multi-turn conversations by:
    1. Accepting conversation history from previous turns
    2. Passing history to agents so they can resolve references
    3. Maintaining session context across multiple questions
    
    Args:
        question: The user's question
        history: List of previous conversation turns (optional)
        session_id: Unique session identifier (optional, will be generated if None)
        
    Returns:
        Dictionary with keys:
        - `answer`: Final verified answer
        - `draft_answer`: Initial draft answer
        - `context`: Retrieved context
        - `history`: Original history passed in
        - `session_id`: Session identifier
        - `turn_number`: Current turn number in conversation
    """
    import uuid
    
    graph = get_conversational_qa_graph()
    
    # Calculate turn number
    turn_number = len(history) + 1 if history else 1
    
    initial_state: QAState = {
        "question": question,
        "context": None,
        "draft_answer": None,
        "answer": None,
        "history": history or [],
        "conversation_summary": None,  # Future feature
        "session_id": session_id or str(uuid.uuid4()),
        "turn_number": turn_number,
    }
    
    final_state = graph.invoke(initial_state)
    
    return final_state


"""Agent implementations for the multi-agent RAG flow.

This module defines three LangChain agents (Retrieval, Summarization,
Verification) and thin node functions that LangGraph uses to invoke them.
"""

from typing import List

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from ..llm.factory import create_chat_model
from .prompts import (
    RETRIEVAL_SYSTEM_PROMPT,
    SUMMARIZATION_SYSTEM_PROMPT,
    VERIFICATION_SYSTEM_PROMPT,
)
from .state import QAState
from .tools import retrieval_tool


def _extract_last_ai_content(messages: List[object]) -> str:
    """Extract the content of the last AIMessage in a messages list."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            return str(msg.content)
    return ""


# Define agents at module level for reuse
retrieval_agent = create_agent(
    model=create_chat_model(),
    tools=[retrieval_tool],
    system_prompt=RETRIEVAL_SYSTEM_PROMPT,
)

summarization_agent = create_agent(
    model=create_chat_model(),
    tools=[],
    system_prompt=SUMMARIZATION_SYSTEM_PROMPT,
)

verification_agent = create_agent(
    model=create_chat_model(),
    tools=[],
    system_prompt=VERIFICATION_SYSTEM_PROMPT,
)


def retrieval_node(state: QAState) -> QAState:
    """Retrieval Agent node: gathers context from vector store.

    This node:
    - Sends the user's question to the Retrieval Agent.
    - The agent uses the attached retrieval tool to fetch document chunks.
    - Extracts the tool's content (CONTEXT string) from the ToolMessage.
    - Stores the consolidated context string in `state["context"]`.
    """
    question = state["question"]

    result = retrieval_agent.invoke({"messages": [HumanMessage(content=question)]})

    messages = result.get("messages", [])
    context = ""

    # Prefer the last ToolMessage content (from retrieval_tool)
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            context = str(msg.content)
            break

    return {
        "context": context,
    }


def summarization_node(state: QAState) -> QAState:
    """Summarization Agent node: generates draft answer from context.

    This node:
    - Sends question + context to the Summarization Agent.
    - Agent responds with a draft answer grounded only in the context.
    - Stores the draft answer in `state["draft_answer"]`.
    """
    question = state["question"]
    context = state.get("context")

    user_content = f"Question: {question}\n\nContext:\n{context}"

    result = summarization_agent.invoke(
        {"messages": [HumanMessage(content=user_content)]}
    )
    messages = result.get("messages", [])
    draft_answer = _extract_last_ai_content(messages)

    return {
        "draft_answer": draft_answer,
    }


def verification_node(state: QAState) -> QAState:
    """Verification Agent node: verifies and corrects the draft answer.

    This node:
    - Sends question + context + draft_answer to the Verification Agent.
    - Agent checks for hallucinations and unsupported claims.
    - Stores the final verified answer in `state["answer"]`.
    """
    question = state["question"]
    context = state.get("context", "")
    draft_answer = state.get("draft_answer", "")

    user_content = f"""Question: {question}

Context:
{context}

Draft Answer:
{draft_answer}

Please verify and correct the draft answer, removing any unsupported claims."""

    result = verification_agent.invoke(
        {"messages": [HumanMessage(content=user_content)]}
    )
    messages = result.get("messages", [])
    answer = _extract_last_ai_content(messages)

    return {
        "answer": answer,
    }


# ==============================================================================
# Conversational Agent Nodes (History-Aware)
# ==============================================================================

def format_history_for_prompt(history: List[dict] | None, max_turns: int = 5) -> str:
    """Format conversation history for inclusion in agent prompts.
    
    Args:
        history: List of conversation turn dictionaries
        max_turns: Maximum number of recent turns to include (default: 5)
        
    Returns:
        Formatted history string for prompt injection
    """
    if not history:
        return "No previous conversation."
    
    # Take only the most recent turns to avoid token overflow
    recent_history = history[-max_turns:] if len(history) > max_turns else history
    
    formatted_turns = []
    for turn in recent_history:
        formatted_turns.append(
            f"Turn {turn.get('turn', '?')}:\n"
            f"Q: {turn.get('question', 'N/A')}\n"
            f"A: {turn.get('answer', 'N/A')}\n"
        )
    
    return "\n".join(formatted_turns)


def conversational_retrieval_node(state: QAState) -> dict:
    """Conversational Retrieval Agent node: history-aware context gathering.
    
    This node:
    - Analyzes conversation history to understand references
    - Uses the Retrieval Agent with history context to fetch document chunks
    - Resolves references like "it", "that", "the method mentioned"
    - Stores the consolidated context string in state
    """
    from .prompts import CONVERSATIONAL_RETRIEVAL_PROMPT
    
    question = state["question"]
    history = state.get("history", [])
    
    # Format history for prompt
    history_text = format_history_for_prompt(history)
    
    # Create conversational retrieval agent with history-aware prompt
    conversational_retrieval_agent = create_agent(
        model=create_chat_model(),
        tools=[retrieval_tool],
        system_prompt=CONVERSATIONAL_RETRIEVAL_PROMPT,
    )
    
    # Format the user message with history context
    user_content = CONVERSATIONAL_RETRIEVAL_PROMPT.format(
        history=history_text,
        question=question
    )
    
    result = conversational_retrieval_agent.invoke(
        {"messages": [HumanMessage(content=user_content)]}
    )
    
    messages = result.get("messages", [])
    context = ""
    
    # Prefer the last ToolMessage content (from retrieval_tool)
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            context = str(msg.content)
            break
    
    return {
        "context": context,
    }


def conversational_summarization_node(state: QAState) -> dict:
    """Conversational Summarization Agent node: history-aware answer generation.
    
    This node:
    - Uses conversation history to understand references and context
    - Generates answers that build on previous turns
    - Maintains conversational coherence across turns
    """
    from .prompts import CONVERSATIONAL_SUMMARIZATION_PROMPT
    
    question = state["question"]
    context = state.get("context", "")
    history = state.get("history", [])
    
    # Format history for prompt
    history_text = format_history_for_prompt(history)
    
    # Create conversational summarization agent
    conversational_summarization_agent = create_agent(
        model=create_chat_model(),
        tools=[],
        system_prompt=CONVERSATIONAL_SUMMARIZATION_PROMPT,
    )
    
    # Format the user message with all context
    user_content = CONVERSATIONAL_SUMMARIZATION_PROMPT.format(
        history=history_text,
        question=question,
        context=context
    )
    
    result = conversational_summarization_agent.invoke(
        {"messages": [HumanMessage(content=user_content)]}
    )
    messages = result.get("messages", [])
    draft_answer = _extract_last_ai_content(messages)
    
    return {
        "draft_answer": draft_answer,
    }


def conversational_verification_node(state: QAState) -> dict:
    """Conversational Verification Agent node: history-aware answer verification.
    
    This node:
    - Verifies draft answer against context and conversation history
    - Ensures references to previous turns are accurate
    - Maintains conversation coherence while removing unsupported claims
    """
    from .prompts import CONVERSATIONAL_VERIFICATION_PROMPT
    
    question = state["question"]
    context = state.get("context", "")
    draft_answer = state.get("draft_answer", "")
    history = state.get("history", [])
    
    # Format history for prompt
    history_text = format_history_for_prompt(history)
    
    # Create conversational verification agent
    conversational_verification_agent = create_agent(
        model=create_chat_model(),
        tools=[],
        system_prompt=CONVERSATIONAL_VERIFICATION_PROMPT,
    )
    
    # Format the user message with all context
    user_content = CONVERSATIONAL_VERIFICATION_PROMPT.format(
        history=history_text,
        question=question,
        context=context,
        draft_answer=draft_answer
    )
    
    result = conversational_verification_agent.invoke(
        {"messages": [HumanMessage(content=user_content)]}
    )
    messages = result.get("messages", [])
    answer = _extract_last_ai_content(messages)
    
    return {
        "answer": answer,
    }


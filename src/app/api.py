from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    QuestionRequest,
    QAResponse,
    ConversationalQARequest,
    ConversationalQAResponse,
    ConversationHistory,
)
from .services.qa_service import answer_question
from .services.indexing_service import index_pdf_file
from .services.conversational_qa_service import (
    answer_conversational_question,
    get_conversation_history,
    create_new_session,
    clear_session_history,
)


app = FastAPI(
    title="IKMS Multi-Agent RAG with Conversational Memory",
    description=(
        "Multi-agent RAG system with conversational memory capabilities. "
        "Supports both single-shot QA via `/qa` and multi-turn conversations via `/qa/conversation`. "
        "The system can understand follow-up questions and maintain context across turns."
    ),
    version="1.0.0",
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path), html=True), name="static")


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:  # pragma: no cover - simple demo handler
    """Catch-all handler for unexpected errors.

    FastAPI will still handle `HTTPException` instances and validation errors
    separately; this is only for truly unexpected failures so API consumers
    get a consistent 500 response body.
    """

    if isinstance(exc, HTTPException):
        # Let FastAPI handle HTTPException as usual.
        raise exc

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.get("/")
async def root():
    """Redirect root URL to API documentation."""
    return RedirectResponse(url="/docs")


@app.post("/qa", response_model=QAResponse, status_code=status.HTTP_200_OK)
async def qa_endpoint(payload: QuestionRequest) -> QAResponse:
    """Submit a question about the vector databases paper.

    US-001 requirements:
    - Accept POST requests at `/qa` with JSON body containing a `question` field
    - Validate the request format and return 400 for invalid requests
    - Return 200 with `answer`, `draft_answer`, and `context` fields
    - Delegate to the multi-agent RAG service layer for processing
    """

    question = payload.question.strip()
    if not question:
        # Explicit validation beyond Pydantic's type checking to ensure
        # non-empty questions.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="`question` must be a non-empty string.",
        )

    # Delegate to the service layer which runs the multi-agent QA graph
    result = answer_question(question)

    return QAResponse(
        answer=result.get("answer", ""),
        context=result.get("context", ""),
    )


@app.post("/index-pdf", status_code=status.HTTP_200_OK)
async def index_pdf(file: UploadFile = File(...)) -> dict:
    """Upload a PDF and index it into the vector database.

    This endpoint:
    - Accepts a PDF file upload
    - Saves it to the local `data/uploads/` directory
    - Uses PyPDFLoader to load the document into LangChain `Document` objects
    - Indexes those documents into the configured Pinecone vector store
    """

    if file.content_type not in ("application/pdf",):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.filename
    contents = await file.read()
    file_path.write_bytes(contents)

    # Index the saved PDF
    chunks_indexed = index_pdf_file(file_path)

    return {
        "filename": file.filename,
        "chunks_indexed": chunks_indexed,
        "message": "PDF indexed successfully.",
    }


# ==============================================================================
# Conversational QA Endpoints
# ==============================================================================

@app.post("/qa/conversation", response_model=ConversationalQAResponse, status_code=status.HTTP_200_OK)
async def conversational_qa(payload: ConversationalQARequest) -> ConversationalQAResponse:
    """Submit a question in a conversational context.
    
    This endpoint supports multi-turn conversations with memory:
    - If session_id is provided, continues an existing conversation
    - If session_id is None, creates a new conversation session
    - Agents can resolve references to previous turns (e.g., "it", "that")
    - History is maintained across turns for context-aware answers
    
    The existing `/qa` endpoint remains for single-shot questions.
    """
    
    question = payload.question.strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="`question` must be a non-empty string."
        )
    
    try:
        result = answer_conversational_question(
            question=question,
            session_id=payload.session_id
        )
        
        return ConversationalQAResponse(
            answer=result["answer"],
            context=result["context"],
            session_id=result["session_id"],
            turn_number=result["turn_number"],
            history_used=result["history_used"]
        )
    except ValueError as e:
        # Session not found or other validation error
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.get("/qa/session/{session_id}/history", response_model=ConversationHistory, status_code=status.HTTP_200_OK)
async def get_session_history(session_id: str) -> ConversationHistory:
    """Retrieve conversation history for a session.
    
    Returns all turns in the conversation with timestamps and context used.
    Useful for displaying conversation history in the UI or debugging.
    """
    
    try:
        history_data = get_conversation_history(session_id)
        
        return ConversationHistory(
            session_id=history_data["session_id"],
            turns=history_data["turns"],
            created_at=history_data["created_at"],
            total_turns=history_data["total_turns"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.post("/qa/session/new", status_code=status.HTTP_201_CREATED)
async def create_session() -> dict:
    """Create a new conversation session.
    
    Returns a new session_id that can be used with the /qa/conversation endpoint.
    """
    
    session_id = create_new_session()
    
    return {
        "session_id": session_id,
        "message": "New conversation session created successfully."
    }


@app.delete("/qa/session/{session_id}/clear", status_code=status.HTTP_200_OK)
async def clear_session(session_id: str) -> dict:
    """Clear all history for a conversation session.
    
    The session ID remains valid, but all previous turns are removed.
    This is useful for starting fresh while keeping the same session.
    """
    
    try:
        clear_session_history(session_id)
        
        return {
            "session_id": session_id,
            "message": "Session history cleared successfully."
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


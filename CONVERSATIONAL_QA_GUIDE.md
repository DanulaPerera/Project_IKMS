# Conversational QA Setup and Testing Guide

## Quick Start

### 1. Start the FastAPI Server

```bash
# From the project root directory
python -m uvicorn src.app.api:app --reload --host 0.0.0.0 --port 8000
```

### 2. Access the Chat Interface

Open your web browser and navigate to:
```
http://localhost:8000/static/index.html
```

### 3. Test the System

Before using the conversational feature, make sure you have indexed a PDF document:

```bash
# Upload a PDF for indexing
# Use the Swagger UI at http://localhost:8000/docs
# Or use the existing /index-pdf endpoint
```

## Testing Conversational Memory

### Test Scenario 1: Basic Follow-up Questions

1. **Turn 1**: "What is HNSW indexing?"
2. **Turn 2**: "What are its main advantages?" (should understand "its" refers to HNSW)
3. **Turn 3**: "How does it compare to LSH?" (should know "it" still refers to HNSW)

### Test Scenario 2: Context Building

1. **Turn 1**: "Explain vector databases"
2. **Turn 2**: "What indexing methods do they use?"
3. **Turn 3**: "Which one is fastest?" (should refer to methods mentioned in turn 2)

### Test Scenario 3: Session Management

1. Ask a few questions in one conversation
2. Click "New Conversation" button
3. Ask an unrelated question - it should not reference previous session
4. Click "Clear History" button in the new session
5. Continue asking questions - history should be reset

## API Endpoints

### Conversational QA Endpoints

- **POST** `/qa/conversation` - Ask a question in a conversational context
- **GET** `/qa/session/{session_id}/history` - Get conversation history
- **POST** `/qa/session/new` - Create a new session
- **DELETE** `/qa/session/{session_id}/clear` - Clear session history

### Legacy Endpoints (backward compatible)

- **POST** `/qa` - Single-shot question (no memory)
- **POST** `/index-pdf` - Index a PDF document

## Troubleshooting

### Frontend not loading
- Check that the `frontend/` directory exists at the project root
- Verify the path in `api.py` is correct
- Check browser console for errors

### CORS errors
- CORS middleware is configured in `api.py`
- Make sure you're accessing from `localhost:8000`

### No responses from assistant
- Ensure you've indexed a PDF document first
- Check API keys in `.env` file (OPENAI_API_KEY, PINECONE_API_KEY)
- Check server logs for errors

### Session not persisting
- Sessions are stored in memory (will reset on server restart)
- This is expected behavior for the current implementation

## Swagger Documentation

FastAPI provides automatic API documentation at:
```
http://localhost:8000/docs
```

You can test all endpoints directly from the Swagger interface.

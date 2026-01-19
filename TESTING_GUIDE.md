# Testing Guide for Multi-Agent RAG System

This guide will help you set up and test the system to verify it's working correctly.

## Prerequisites Checklist

Before testing, ensure you have:

- [ ] Python 3.11+ installed
- [ ] `uv` package manager installed ([uv installation guide](https://github.com/astral-sh/uv))
- [ ] OpenAI API key
- [ ] Pinecone account and API key
- [ ] A Pinecone index created (dimension: 3072 for text-embedding-3-large)

## Step 1: Environment Setup

### 1.1 Create `.env` File

Create a `.env` file in the project root with your API keys:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL_NAME=gpt-4o-mini
OPENAI_EMBEDDING_MODEL_NAME=text-embedding-3-large

# Pinecone Configuration
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_INDEX_NAME=your-index-name

# Retrieval Configuration
RETRIEVAL_K=4
```

### 1.2 Create Pinecone Index

If you haven't created a Pinecone index yet:

1. Go to [Pinecone Console](https://app.pinecone.io/)
2. Create a new index with these settings:
   - **Name**: `class-12-rag` (or your choice)
   - **Dimension**: `3072` (for text-embedding-3-large)
   - **Metric**: `cosine`
   - **Cloud**: Choose your preferred region

### 1.3 Install Dependencies

```bash
# Install dependencies using uv
uv sync
```

## Step 2: Prepare Test Data

### 2.1 Get a Sample PDF

Download or create a sample PDF document. For testing, you can:

- Use the project's README as a test document
- Download a research paper about vector databases
- Use any PDF with technical content

Save it as `test_document.pdf` in the project root.

## Step 3: Start the Server

### 3.1 Run the FastAPI Server

```bash
# Activate the virtual environment (if using uv)
# uv creates a .venv automatically

# Windows
.venv\Scripts\activate

# Run the server
uvicorn src.app.api:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3.2 Verify Server is Running

Open your browser and go to:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Step 4: Test the System

### Test 4.1: Index a PDF Document

#### Using cURL (Command Line):

```bash
curl -X POST "http://localhost:8000/index-pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_document.pdf"
```

#### Using PowerShell:

```powershell
$filePath = "test_document.pdf"
$uri = "http://localhost:8000/index-pdf"

$boundary = [System.Guid]::NewGuid().ToString()
$fileName = [System.IO.Path]::GetFileName($filePath)
$fileBytes = [System.IO.File]::ReadAllBytes($filePath)

$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
    "Content-Type: application/pdf",
    "",
    [System.Text.Encoding]::GetEncoding("ISO-8859-1").GetString($fileBytes),
    "--$boundary--"
) -join "`r`n"

Invoke-RestMethod -Uri $uri -Method Post -ContentType "multipart/form-data; boundary=$boundary" -Body $bodyLines
```

#### Using Python:

```python
import requests

url = "http://localhost:8000/index-pdf"
files = {"file": open("test_document.pdf", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

#### Expected Response:

```json
{
  "filename": "test_document.pdf",
  "chunks_indexed": 42,
  "message": "PDF indexed successfully."
}
```

### Test 4.2: Ask Questions

#### Using cURL:

```bash
curl -X POST "http://localhost:8000/qa" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is a vector database?"}'
```

#### Using PowerShell:

```powershell
$body = @{
    question = "What is a vector database?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/qa" -Method Post -Body $body -ContentType "application/json"
```

#### Using Python:

```python
import requests

url = "http://localhost:8000/qa"
payload = {"question": "What is a vector database?"}

response = requests.post(url, json=payload)
result = response.json()

print(f"Question: {payload['question']}")
print(f"\nAnswer: {result['answer']}")
print(f"\nContext: {result['context']}")
```

#### Expected Response:

```json
{
  "answer": "A vector database is a specialized database designed to store and query high-dimensional vector embeddings...",
  "context": "CHUNK 1 (Page 2):\nVector databases store embeddings...\n\nCHUNK 2 (Page 5):\nCommon use cases include..."
}
```

### Test 4.3: Interactive Testing via Swagger UI

1. Go to http://localhost:8000/docs
2. Click on **POST /index-pdf**
   - Click "Try it out"
   - Upload a PDF file
   - Click "Execute"
   - Verify you get a success response

3. Click on **POST /qa**
   - Click "Try it out"
   - Enter a question in the request body
   - Click "Execute"
   - Verify you get a relevant answer

## Step 5: Verify Multi-Agent Flow

To verify the multi-agent system is working correctly, you can add debug logging:

### 5.1 Enable Debug Logging

Add this to the top of `src/app/api.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 5.2 Watch the Logs

When you ask a question, you should see in the terminal:
- Retrieval agent searching Pinecone
- Context being retrieved
- Summarization agent generating draft
- Verification agent checking the draft

## Troubleshooting

### Issue: "Module not found" errors
**Solution**: Make sure you're in the virtual environment and dependencies are installed
```bash
uv sync
```

### Issue: "OpenAI API key not found"
**Solution**: Check that `.env` file exists and contains valid `OPENAI_API_KEY`

### Issue: "Pinecone index not found"
**Solution**: 
- Verify the index exists in Pinecone console
- Check `PINECONE_INDEX_NAME` matches exactly

### Issue: "No results found" when asking questions
**Solution**: 
- Make sure you indexed a PDF first using `/index-pdf`
- Check that the question is related to the PDF content
- Try increasing `RETRIEVAL_K` in `.env`

### Issue: Empty or generic answers
**Solution**: 
- Check if the PDF was indexed correctly (verify chunks_indexed > 0)
- Ensure the question is relevant to the PDF content
- Try rephrasing the question

## Success Criteria

✅ Server starts without errors  
✅ PDF upload returns success with chunks_indexed > 0  
✅ Questions return relevant answers based on the PDF content  
✅ Context field shows retrieved document chunks  
✅ Answers are grounded in the context (no hallucinations)  

## Next Steps

Once basic testing is complete, you can:
- Test with different PDFs
- Experiment with different questions
- Adjust `RETRIEVAL_K` to change how many chunks are retrieved
- Try different OpenAI models
- Monitor token usage and costs

## Sample Test Questions

Based on the README content, try these questions:

1. "What is LangChain used for?"
2. "How does Pinecone work?"
3. "What are the three agents in this system?"
4. "What is retrieval-augmented generation?"
5. "How do you create a Pinecone index?"

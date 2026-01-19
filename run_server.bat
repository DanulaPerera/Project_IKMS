@echo off
echo Starting Multi-Agent RAG API Server...
echo.
echo Server will be available at:
echo - API Docs: http://localhost:8000/docs
echo - Alternative Docs: http://localhost:8000/redoc
echo.
echo Press CTRL+C to stop the server
echo.

.venv\Scripts\uvicorn.exe src.app.api:app --reload --host 0.0.0.0 --port 8000

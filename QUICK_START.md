# IKMS Conversational QA - Quick Start Guide

## 🚀 Starting the Application

### Step 1: Open Terminal in Project Directory

Open PowerShell or Command Prompt and navigate to your project:

```bash
cd "d:\Education\AI Engineer Bootcamp\IKMS\class-12"
```

### Step 2: Activate Virtual Environment & Start Server

Run this single command:

```bash
.venv\Scripts\activate.ps1; python -m uvicorn src.app.api:app --reload --host 0.0.0.0 --port 8000
```

**What you'll see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Application startup complete.
```

✅ **Server is now running!**

### Step 3: Open the Chat Interface

Open your web browser and go to:

```
http://localhost:8000/static/index.html
```

You should see the **IKMS Multi-Agent RAG Assistant** chat interface!

---

## 💬 Using the Chat Interface

### First Time? Index a PDF First!

Before asking questions, you need to upload a PDF document:

1. Open **Swagger UI**: http://localhost:8000/docs
2. Find the **`POST /index-pdf`** endpoint
3. Click **"Try it out"**
4. Click **"Choose File"** and select your PDF
5. Click **"Execute"**
6. Wait for: `"PDF indexed successfully"`

### Asking Questions

1. **Type your question** in the input box at the bottom
2. **Press Enter** or click the **blue send button**
3. **Wait for response** (you'll see typing indicator)
4. **Ask follow-up questions** - the assistant remembers context!

### Example Conversation

```
You: "What is this document about?"
Assistant: [Provides answer about your PDF]

You: "Can you summarize the main points?"
Assistant: [Summarizes, understanding "the" refers to the document]

You: "Tell me more about that"
Assistant: [Continues the conversation, remembering context]
```

### Session Controls

- **New Conversation** button (top right): Start fresh conversation
- **Clear History** button (top right): Clear current session history
- **Session ID** (bottom left): Shows your unique session
- **Turn counter** (bottom right): Tracks number of questions

---

## 🛑 Stopping the Application

To stop the server:

1. Go to your terminal/PowerShell window
2. Press **`CTRL + C`**
3. Wait for "Shutting down" message

---

## 🔄 Restarting After Closing

Simply repeat these steps:

1. **Open terminal** in project directory
2. **Run the command**:
   ```bash
   .venv\Scripts\activate.ps1; python -m uvicorn src.app.api:app --reload --host 0.0.0.0 --port 8000
   ```
3. **Open browser** to: http://localhost:8000/static/index.html

**Note**: Your conversation history is stored in memory, so it will be cleared when you restart the server!

---

## 📝 Quick Reference

| Action | Command/URL |
|--------|-------------|
| Start Server | `.venv\Scripts\activate.ps1; python -m uvicorn src.app.api:app --reload --host 0.0.0.0 --port 8000` |
| Chat Interface | http://localhost:8000/static/index.html |
| API Documentation | http://localhost:8000/docs |
| Upload PDF | http://localhost:8000/docs → `/index-pdf` |
| Stop Server | `CTRL + C` in terminal |

---

## ⚠️ Troubleshooting

### Server won't start?
- Make sure you're in the project directory
- Check if another program is using port 8000
- Verify your `.env` file has OPENAI_API_KEY and PINECONE_API_KEY

### Chat interface not loading?
- Make sure the server is running
- Check the URL is exactly: http://localhost:8000/static/index.html
- Try refreshing the page (F5)

### No responses from assistant?
- Make sure you've indexed a PDF first
- Check your API keys in `.env` file
- Look at the terminal for error messages

### "Session not found" error?
- Click "New Conversation" to create a fresh session
- This happens if you restart the server (sessions are in memory)

---

## 🎯 Testing Conversational Memory

Try this sequence to test the memory feature:

1. **Turn 1**: Ask about a specific topic in your PDF
2. **Turn 2**: Use "it" or "that" to refer to the previous answer
3. **Turn 3**: Ask "Can you explain more?" (implicit reference)
4. **Turn 4**: Test with "How does this compare to X?"

The assistant should understand all references and maintain context!

---

## 📚 Need More Help?

- Full documentation: See `CONVERSATIONAL_QA_GUIDE.md`
- Implementation details: See `walkthrough.md` in brain folder
- API reference: http://localhost:8000/docs

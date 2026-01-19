# Quick Testing Guide - Multi-Agent RAG System

## 🎯 Two Ways to Test

### Method 1: Swagger UI (EASIEST - No Postman Needed!)
### Method 2: Postman (Since you have it installed)

---

## 🌐 Method 1: Using Swagger UI (Recommended for Beginners)

**Swagger UI is a web interface built into your API that lets you test endpoints directly in your browser!**

### Step 1: Open the API Docs
Open your browser and go to: **http://localhost:8000/docs**

You'll see a page with two endpoints:
- `POST /index-pdf` - Upload a PDF to index
- `POST /qa` - Ask questions about the indexed PDF

### Step 2: Upload a PDF Document

1. **Click on** `POST /index-pdf` to expand it
2. **Click** the "Try it out" button (top right)
3. **Click** "Choose File" and select any PDF from your computer
   - You can use any PDF: research papers, textbooks, articles, etc.
   - For testing, you could even use the project's README.md converted to PDF
4. **Click** "Execute"

**Expected Response:**
```json
{
  "filename": "your_document.pdf",
  "chunks_indexed": 42,
  "message": "PDF indexed successfully."
}
```

### Step 3: Ask Questions

1. **Click on** `POST /qa` to expand it
2. **Click** "Try it out"
3. **Replace the example** with your question:
```json
{
  "question": "What is this document about?"
}
```
4. **Click** "Execute"

**Expected Response:**
```json
{
  "answer": "Based on the document, this is about...",
  "context": "CHUNK 1:\n[Text from your PDF]\n\nCHUNK 2:\n[More text...]"
}
```

---

## 📮 Method 2: Using Postman

### Test 1: Index a PDF

**Request:**
- **Method:** POST
- **URL:** `http://localhost:8000/index-pdf`
- **Body Type:** form-data
- **Key:** `file` (set type to "File")
- **Value:** Choose your PDF file

**Steps in Postman:**
1. Create a new request
2. Set method to POST
3. Enter URL: `http://localhost:8000/index-pdf`
4. Go to Body tab
5. Select "form-data"
6. Add key: `file`
7. Change type from "Text" to "File" (dropdown on right)
8. Click "Select Files" and choose a PDF
9. Click "Send"

### Test 2: Ask a Question

**Request:**
- **Method:** POST
- **URL:** `http://localhost:8000/qa`
- **Headers:** 
  - `Content-Type`: `application/json`
- **Body (raw JSON):**
```json
{
  "question": "What is the main topic of this document?"
}
```

**Steps in Postman:**
1. Create a new request
2. Set method to POST
3. Enter URL: `http://localhost:8000/qa`
4. Go to Body tab
5. Select "raw"
6. Select "JSON" from dropdown
7. Paste the question JSON
8. Click "Send"

---

## 📚 Sample Test PDFs to Use

If you don't have a PDF handy, try these:

1. **Convert the README.md to PDF:**
   - Open `README.md` in your browser
   - Print to PDF
   - Use that for testing

2. **Download a sample PDF:**
   - Any Wikipedia article saved as PDF
   - A research paper from arXiv
   - Any technical documentation

3. **Create a simple text document:**
   - Write a few paragraphs about any topic
   - Save as PDF
   - Test if the system can answer questions about it

---

## 🎯 Example Test Flow

**Scenario: Testing with a Document about Python**

1. **Upload** a PDF about Python programming
2. **Expected Result:** `chunks_indexed: 35`
3. **Ask Question:** "What is Python used for?"
4. **Expected Result:** Answer based on your PDF content with relevant context

**Good Test Questions:**
- "What is the main topic of this document?"
- "Summarize the key points"
- "What are the main concepts discussed?"
- "What is [specific term from your PDF]?"

**Testing Verification Agent:**
Try asking something NOT in the document:
- If you ask "Who invented Python?" but your PDF doesn't mention it
- The system should say "Based on the available document, I cannot answer..."

---

## ✅ What Success Looks Like

**After Indexing:**
✅ You get a success message with `chunks_indexed > 0`

**After Asking Questions:**
✅ You get a relevant answer based on your PDF
✅ The `context` field shows actual text from your PDF
✅ The answer makes sense and is grounded in the document
✅ If the answer isn't in the PDF, the system says it can't answer

**Processing Time:**
⏱️ Indexing: 5-30 seconds (depending on PDF size)
⏱️ Q&A: 3-10 seconds per question

---

## 🐛 Common Issues

**Issue: "Pinecone index not found"**
- Make sure you created a Pinecone index
- Check your `.env` file has the correct `PINECONE_INDEX_NAME`

**Issue: "OpenAI API error"**
- Verify your `OPENAI_API_KEY` in `.env` is correct
- Check you have API credits on your OpenAI account

**Issue: "Generic/vague answers"**
- Make sure the PDF was indexed first
- Try questions directly related to PDF content
- Check the `context` field to see what was retrieved

---

## 🎓 Pro Tips

1. **Start Simple:** Use a small PDF (2-5 pages) for your first test
2. **Check Context:** Always look at the `context` field to see what was retrieved
3. **Phrase Questions Clearly:** Be specific about what you want to know
4. **Test Edge Cases:** Ask questions the PDF can't answer to test the verification agent

---

## 📊 What's Happening Behind the Scenes

When you ask a question, the system:
1. 🔍 **Retrieval Agent** searches Pinecone for relevant chunks
2. ✍️ **Summarization Agent** creates a draft answer
3. ✅ **Verification Agent** checks for accuracy
4. 📤 Returns the final verified answer

You can see this in the terminal logs when the server is running!

"""
Simple test script for the Multi-Agent RAG API.

This script tests both endpoints:
1. /index-pdf - Upload and index a PDF
2. /qa - Ask questions about the indexed content

Usage:
    python test_api.py
"""

import requests
import time
from pathlib import Path


BASE_URL = "http://localhost:8000"


def test_index_pdf(pdf_path: str) -> dict:
    """Test the PDF indexing endpoint.
    
    Args:
        pdf_path: Path to the PDF file to index
        
    Returns:
        Response JSON from the API
    """
    print(f"\n{'='*60}")
    print("TEST 1: Indexing PDF Document")
    print(f"{'='*60}")
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: File not found: {pdf_path}")
        return None
    
    url = f"{BASE_URL}/index-pdf"
    
    print(f"📄 Uploading: {pdf_path}")
    print(f"🌐 Endpoint: {url}")
    
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": (Path(pdf_path).name, f, "application/pdf")}
            response = requests.post(url, files=files, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Success!")
            print(f"   - Filename: {result['filename']}")
            print(f"   - Chunks Indexed: {result['chunks_indexed']}")
            print(f"   - Message: {result['message']}")
            return result
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print("   Make sure the server is running: uvicorn src.app.api:app --reload")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def test_qa(question: str) -> dict:
    """Test the Q&A endpoint.
    
    Args:
        question: Question to ask about the indexed document
        
    Returns:
        Response JSON from the API
    """
    print(f"\n{'='*60}")
    print("TEST 2: Asking Questions")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/qa"
    
    print(f"❓ Question: {question}")
    print(f"🌐 Endpoint: {url}")
    print("\n🤖 Processing through multi-agent pipeline...")
    print("   → Retrieval Agent: Searching vector database...")
    print("   → Summarization Agent: Generating draft answer...")
    print("   → Verification Agent: Checking for accuracy...")
    
    try:
        payload = {"question": question}
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=60)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Success! (took {elapsed:.2f}s)")
            print(f"\n📝 ANSWER:")
            print(f"{'-'*60}")
            print(result['answer'])
            print(f"{'-'*60}")
            
            print(f"\n📚 CONTEXT (Retrieved Chunks):")
            print(f"{'-'*60}")
            context = result.get('context', 'No context available')
            # Truncate context if too long
            if len(context) > 500:
                print(context[:500] + "\n...(truncated)")
            else:
                print(context)
            print(f"{'-'*60}")
            
            return result
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print("   Make sure the server is running: uvicorn src.app.api:app --reload")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


def run_full_test():
    """Run a complete test of the system."""
    print("\n" + "="*60)
    print("🚀 Multi-Agent RAG System - Full Test Suite")
    print("="*60)
    
    # Configuration
    pdf_path = "test_document.pdf"
    test_questions = [
        "What is this document about?",
        "What are the main topics covered?",
    ]
    
    # Test 1: Index PDF
    index_result = test_index_pdf(pdf_path)
    
    if not index_result:
        print("\n⚠️  PDF indexing failed. Cannot proceed with Q&A tests.")
        print("\nTroubleshooting:")
        print("1. Make sure the server is running")
        print("2. Check that test_document.pdf exists in the project root")
        print("3. Verify your .env file has valid API keys")
        return
    
    # Wait a moment for indexing to complete
    print("\n⏳ Waiting for vectors to be indexed in Pinecone...")
    time.sleep(3)
    
    # Test 2: Ask questions
    for i, question in enumerate(test_questions, 1):
        result = test_qa(question)
        if result and i < len(test_questions):
            print("\n⏳ Waiting before next question...")
            time.sleep(2)
    
    # Summary
    print(f"\n{'='*60}")
    print("🎉 Testing Complete!")
    print(f"{'='*60}")
    print("\nNext Steps:")
    print("- Try asking your own questions")
    print("- Upload different PDF documents")
    print("- Check the Swagger UI at http://localhost:8000/docs")


if __name__ == "__main__":
    run_full_test()

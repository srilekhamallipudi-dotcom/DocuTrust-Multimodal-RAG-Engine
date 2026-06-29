#!/usr/bin/env python3
"""
Test script to validate PDF upload and RAG question-answering flow.
"""

import requests
import json
import time
import os

BASE_URL = "http://127.0.0.1:8000"
PDF_PATH = os.path.join(os.path.dirname(__file__), "sample_resume.pdf")

def test_upload():
    """Test PDF upload"""
    print("\n" + "="*60)
    print("TEST 1: PDF Upload")
    print("="*60)
    
    try:
        with open(PDF_PATH, "rb") as f:
            files = {"files": (PDF_PATH, f)}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if response.status_code == 200:
            print("✅ UPLOAD SUCCESSFUL")
            return True
        else:
            print("❌ UPLOAD FAILED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_ask_question(question):
    """Test asking a question"""
    print("\n" + "="*60)
    print(f"TEST 2: Ask Question - '{question}'")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": question},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        chunks_retrieved = data.get("timeline", [])
        if any("Retrieved" in str(line) for line in chunks_retrieved):
            print("✅ QUESTION ANSWERED")
            return True
        else:
            print("❌ NO CHUNKS RETRIEVED")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 Starting DocuTrust Flow Tests...")
    
    # Test 1: Upload PDF
    upload_ok = test_upload()
    
    if not upload_ok:
        print("\n❌ Upload failed. Stopping tests.")
        exit(1)
    
    # Wait for server to process
    print("\n⏳ Waiting 2 seconds for server to process...")
    time.sleep(2)
    
    # Test 2: Ask question
    test_ask_question("What is MERN Stack?")
    
    print("\n" + "="*60)
    print("✅ Tests Complete")
    print("="*60)

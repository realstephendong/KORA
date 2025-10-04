#!/usr/bin/env python3
"""
Simple test for Gemini API with free tier.
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_gemini_simple():
    """Test Gemini with a simple approach."""
    
    google_key = os.environ.get('GOOGLE_API_KEY')
    if not google_key:
        print("❌ GOOGLE_API_KEY not found")
        return
    
    print(f"✅ Google API key found: {google_key[:10]}...")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Try with the most basic setup (free tier)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=google_key
        )
        
        print("✅ Gemini model created successfully")
        
        # Test a simple message
        print("--- Testing simple message ---")
        response = llm.invoke("Hello, how are you?")
        print(f"✅ Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return False

if __name__ == "__main__":
    test_gemini_simple()

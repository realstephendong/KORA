#!/usr/bin/env python3
"""
Test script to check available Gemini models.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def test_gemini_models():
    """Test different Gemini model names."""
    
    google_key = os.environ.get('GOOGLE_API_KEY')
    if not google_key:
        print("❌ GOOGLE_API_KEY not found")
        return
    
    print(f"✅ Google API key found: {google_key[:10]}...")
    
    # Test different model names
    models_to_test = [
        "gemini-pro",
        "gemini-1.5-pro", 
        "gemini-1.5-flash",
        "gemini-1.0-pro",
        "models/gemini-pro",
        "models/gemini-1.5-pro"
    ]
    
    for model_name in models_to_test:
        print(f"\n--- Testing model: {model_name} ---")
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0,
                convert_system_message_to_human=True,
                google_api_key=google_key
            )
            
            # Try a simple invoke
            response = llm.invoke("Hello, how are you?")
            print(f"✅ {model_name}: {response.content[:50]}...")
            break  # If successful, stop testing
            
        except Exception as e:
            print(f"❌ {model_name}: {str(e)[:100]}...")

if __name__ == "__main__":
    test_gemini_models()

#!/usr/bin/env python
"""
Test script for direct Ollama API interaction.
This bypasses our app and tests the connection directly.
"""

import sys
import json
import argparse
import requests
from datetime import datetime

def test_ollama_direct(model="llama3.2"):
    """Test direct connection to Ollama API"""
    print(f"Testing direct connection to Ollama API with model {model}...")
    
    # First check the Ollama API endpoint
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✓ Connected to Ollama API: Found {len(models)} models")
            
            # Check if our model exists
            model_found = any(m.get("name") == model for m in models)
            if model_found:
                print(f"✓ Model '{model}' found in Ollama")
            else:
                print(f"✗ Model '{model}' NOT found in Ollama")
                print(f"Available models: {', '.join(m.get('name') for m in models)}")
                return False
        else:
            print(f"✗ Failed to connect to Ollama API: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Connection to Ollama API failed: {e}")
        return False
    
    # Now test a simple generation
    try:
        start_time = datetime.now()
        
        prompt = "Write a one sentence description of noir fiction."
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        print(f"Sending generation request to Ollama with model {model}...")
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if response.status_code == 200:
            response_data = response.json()
            response_text = response_data.get("response", "")
            print(f"✓ Generation successful in {duration:.2f} seconds")
            print(f"Prompt: {prompt}")
            print(f"Response: {response_text}")
            return True
        else:
            print(f"✗ Generation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Generation request failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Ollama API directly")
    parser.add_argument("--model", "-m", default="llama3.2-optimized", 
                      help="Model to test (default: llama3.2-optimized)")
    args = parser.parse_args()
    
    success = test_ollama_direct(args.model)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 
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
            
            # Check if our model exists - allow for model:latest format
            model_found = any(m.get("name").startswith(model) for m in models)
            if model_found:
                print(f"✓ Model '{model}' found in Ollama")
                model_name = next(m.get("name") for m in models if m.get("name").startswith(model))
                print(f"Using model: {model_name}")
                # Update model name for actual test
                model = model_name
            else:
                print(f"✗ Model '{model}' NOT found in Ollama")
                print(f"Available models: {', '.join(m.get('name') for m in models)}")
                assert False, f"Model '{model}' not found in Ollama"
        else:
            print(f"✗ Failed to connect to Ollama API: {response.status_code} - {response.text}")
            assert False, f"Failed to connect to Ollama API: {response.status_code}"
    except Exception as e:
        print(f"✗ Connection to Ollama API failed: {e}")
        assert False, f"Connection to Ollama API failed: {e}"
    
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
            assert True
        else:
            print(f"✗ Generation failed: {response.status_code} - {response.text}")
            assert False, f"Generation failed: {response.status_code}"
    except Exception as e:
        print(f"✗ Generation request failed: {e}")
        assert False, f"Generation request failed: {e}"

def main():
    parser = argparse.ArgumentParser(description="Test Ollama API directly")
    parser.add_argument("--model", "-m", default="llama3.2-optimized", 
                      help="Model to test (default: llama3.2-optimized)")
    args = parser.parse_args()
    
    try:
        test_ollama_direct(args.model)
        success = True
    except AssertionError as e:
        print(f"Test failed: {e}")
        success = False
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 
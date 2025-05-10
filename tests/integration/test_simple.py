#!/usr/bin/env python
"""
Simple test script for the Pulp Fiction Generator.
This tests just the basic command-line interface functionality.
"""

import subprocess
import sys

def main():
    print("Testing basic command functionality...")
    
    # Test 1: Check if the command exists and version command works
    try:
        result = subprocess.run(["./pulp-fiction", "--help"], 
                               capture_output=True, text=True, check=True)
        print("✓ Command exists and help works")
        print(f"Command output preview:\n{result.stdout[:200]}...")
    except Exception as e:
        print(f"✗ Basic command test failed: {e}")
        return 1
    
    # Test 2: Run a very simple test-step with direct output 
    print("\nTesting basic research1 step directly...")
    try:
        result = subprocess.run(
            ["./pulp-fiction", "test-step", "research1", 
             "--model", "llama3.2-optimized", "--genre", "noir"],
            capture_output=True, text=True, check=False)
        
        print(f"Exit code: {result.returncode}")
        print(f"Standard error: {result.stderr[:500]}")
        print(f"Standard output preview: {result.stdout[:500]}")
        
        if result.returncode == 0:
            print("✓ Basic research1 step worked")
        else:
            print("✗ Basic research1 step failed")
    except Exception as e:
        print(f"✗ Command execution error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
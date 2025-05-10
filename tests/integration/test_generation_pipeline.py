#!/usr/bin/env python
"""
Test script for Pulp Fiction Generator story generation pipeline.

This script runs tests on individual generation steps and sequences to verify proper operation.
"""

import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
from datetime import datetime

def run_command(cmd, check=True):
    """Run a command and return its output"""
    cmd_str = ' '.join(cmd)
    print(f"Running: {cmd_str}")
    
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error: {e.stderr.strip() if e.stderr else 'No error output'}")
        raise
    except Exception as e:
        print(f"Failed to execute command: {e}")
        raise

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Test the story generation pipeline")
    parser.add_argument("--model", "-m", default="llama3.2-optimized", 
                      help="Model to use for testing (default: llama3.2-optimized)")
    parser.add_argument("--genre", "-g", default="noir", 
                      help="Genre to use for testing (default: noir)")
    parser.add_argument("--output-dir", "-o", default="./test_results", 
                      help="Directory to save test results (default: ./test_results)")
    parser.add_argument("--save-artifacts", "-s", action="store_true",
                      help="Save artifacts from each step for inspection")
    parser.add_argument("--verbose", "-v", action="store_true", 
                      help="Show verbose output")
    parser.add_argument("--debug", "-d", action="store_true",
                      help="Enable debug mode with maximum output")
    parser.add_argument("--only", choices=["individual", "sequence", "all"], default="all",
                      help="Run only individual tests, sequence tests, or all tests (default: all)")
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = output_dir / f"test_{timestamp}"
    test_dir.mkdir()
    
    binary = "./pulp-fiction"
    model = args.model
    genre = args.genre
    
    # Track test results
    results = {
        "timestamp": timestamp,
        "model": model,
        "genre": genre,
        "individual_steps": {},
        "sequences": {},
        "full_pipeline": None
    }
    
    # Test each individual step if required
    if args.only in ["individual", "all"]:
        print("\n=== Testing Individual Steps ===\n")
        individual_steps = ["research1", "research2", "research3", "research", "world", "character", "plot", "write", "edit"]
        
        for step in individual_steps:
            print(f"\n--- Testing {step} step ---")
            output_file = test_dir / f"{step}.json"
            
            cmd = [binary, "test-step", step, "--genre", genre, "--model", model, "--output", str(output_file)]
            if args.verbose:
                cmd.append("--verbose")
            if args.debug:
                cmd.append("--debug")
            
            try:
                start_time = datetime.now()
                result = run_command(cmd, check=False)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                success = result.returncode == 0
                
                if success:
                    print(f"✓ {step} step passed in {duration:.2f} seconds")
                else:
                    print(f"✗ {step} step failed in {duration:.2f} seconds")
                    print(f"  Exit code: {result.returncode}")
                    if result.stderr:
                        print(f"  Error: {result.stderr.strip()}")
                    if result.stdout and args.debug:
                        print(f"  Output: {result.stdout.strip()}")
                
                # Save the test result
                results["individual_steps"][step] = {
                    "success": success,
                    "duration": duration,
                    "returncode": result.returncode,
                    "output_file": str(output_file) if args.save_artifacts else None,
                    "stderr": result.stderr if result.stderr else None
                }
                
                # Clean up if we're not saving artifacts
                if not args.save_artifacts and output_file.exists():
                    output_file.unlink()
                    
            except Exception as e:
                print(f"Error testing {step}: {str(e)}")
                results["individual_steps"][step] = {
                    "success": False,
                    "error": str(e)
                }
    
    # Test sequences of steps if required
    if args.only in ["sequence", "all"]:
        print("\n=== Testing Step Sequences ===\n")
        sequences = [
            "research1-research2",
            "research1-research2-research3",
            "research-world",
            "research-world-character",
            "research-world-character-plot",
            "research-world-character-plot-write",
            "research-world-character-plot-write-edit"
        ]
        
        # Now test each sequence, building up the pipeline
        for seq in sequences:
            print(f"\n--- Testing sequence: {seq} ---")
            output_file = test_dir / f"{seq.replace('-', '_')}.json"
            
            cmd = [binary, "test-step", seq, "--genre", genre, "--model", model, "--output", str(output_file)]
            if args.verbose:
                cmd.append("--verbose")
            if args.debug:
                cmd.append("--debug")
            
            try:
                start_time = datetime.now()
                result = run_command(cmd, check=False)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                success = result.returncode == 0
                
                if success:
                    print(f"✓ {seq} sequence passed in {duration:.2f} seconds")
                else:
                    print(f"✗ {seq} sequence failed in {duration:.2f} seconds")
                    print(f"  Exit code: {result.returncode}")
                    if result.stderr:
                        print(f"  Error: {result.stderr.strip()}")
                    if result.stdout and args.debug:
                        print(f"  Output: {result.stdout.strip()}")
                
                # Save the test result
                results["sequences"][seq] = {
                    "success": success,
                    "duration": duration,
                    "returncode": result.returncode,
                    "output_file": str(output_file) if args.save_artifacts else None,
                    "stderr": result.stderr if result.stderr else None
                }
                
                # Clean up if we're not saving artifacts
                if not args.save_artifacts and output_file.exists():
                    output_file.unlink()
                    
            except Exception as e:
                print(f"Error testing sequence {seq}: {str(e)}")
                results["sequences"][seq] = {
                    "success": False,
                    "error": str(e)
                }
    
    # Test the full pipeline through the generate command
    if args.only in ["all"]:
        print("\n=== Testing Full Pipeline ===\n")
        output_file = test_dir / "full_pipeline_story.md"
        
        cmd = [binary, "generate", "--chunked", "--genre", genre, "--model", model, 
               "--output", str(output_file), "--chapters", "1"]
        if args.verbose:
            cmd.append("--verbose")
        if args.debug:
            cmd.append("--debug")
        
        try:
            start_time = datetime.now()
            result = run_command(cmd, check=False)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            success = result.returncode == 0
            
            if success:
                print(f"✓ Full pipeline passed in {duration:.2f} seconds")
                if output_file.exists():
                    file_size = output_file.stat().st_size
                    print(f"  Generated story size: {file_size} bytes")
            else:
                print(f"✗ Full pipeline failed in {duration:.2f} seconds")
                print(f"  Exit code: {result.returncode}")
                if result.stderr:
                    print(f"  Error: {result.stderr.strip()}")
                if result.stdout and args.debug:
                    print(f"  Output: {result.stdout.strip()}")
            
            # Save the test result
            results["full_pipeline"] = {
                "success": success,
                "duration": duration,
                "returncode": result.returncode,
                "output_file": str(output_file) if args.save_artifacts else None,
                "stderr": result.stderr if result.stderr else None
            }
            
            # Clean up if we're not saving artifacts
            if not args.save_artifacts and output_file.exists():
                output_file.unlink()
                
        except Exception as e:
            print(f"Error testing full pipeline: {str(e)}")
            results["full_pipeline"] = {
                "success": False,
                "error": str(e)
            }
    
    # Save the test results
    results_file = test_dir / "test_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTest results saved to {results_file}\n")
    
    # Print summary
    print("=== Test Summary ===")
    
    if args.only in ["individual", "all"]:
        print("\nIndividual Steps:")
        for step, result in results["individual_steps"].items():
            status = "✓" if result.get("success", False) else "✗"
            duration = f"{result.get('duration', 0):.2f}s" if "duration" in result else "N/A"
            print(f"{status} {step}: {duration}")
    
    if args.only in ["sequence", "all"]:
        print("\nSequences:")
        for seq, result in results["sequences"].items():
            status = "✓" if result.get("success", False) else "✗"
            duration = f"{result.get('duration', 0):.2f}s" if "duration" in result else "N/A"
            print(f"{status} {seq}: {duration}")
    
    if args.only in ["all"]:
        print("\nFull Pipeline:")
        if results["full_pipeline"]:
            status = "✓" if results["full_pipeline"].get("success", False) else "✗"
            duration = f"{results['full_pipeline'].get('duration', 0):.2f}s" if "duration" in results["full_pipeline"] else "N/A"
            print(f"{status} generate: {duration}")
    
    # Determine overall success
    all_success = True
    
    if args.only in ["individual", "all"]:
        for result in results["individual_steps"].values():
            if not result.get("success", False):
                all_success = False
                break
    
    if all_success and args.only in ["sequence", "all"]:
        for result in results["sequences"].values():
            if not result.get("success", False):
                all_success = False
                break
    
    if all_success and args.only in ["all"]:
        if results["full_pipeline"] and not results["full_pipeline"].get("success", False):
            all_success = False
    
    print(f"\nOverall result: {'Success' if all_success else 'Failure'}")
    
    # Clean up test directory if it's empty (and we're not saving artifacts)
    if not args.save_artifacts:
        try:
            # Keep the results file
            files = list(test_dir.glob("*"))
            if len(files) == 1 and files[0].name == "test_results.json":
                # Don't delete directory with the results file
                pass
            elif len(files) == 0:
                test_dir.rmdir()
        except Exception:
            pass
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main()) 
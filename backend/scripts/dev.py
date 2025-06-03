#!/usr/bin/env python3
"""
Development utility scripts for GEO Insight backend.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

def run_command(command, check=True):
    """Run a shell command."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=check)
    return result.returncode == 0

def run_tests():
    """Run all tests."""
    print("Running tests...")
    return run_command("pytest")

def run_dev_server():
    """Run development server."""
    print("Starting development server...")
    run_command("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="GEO Insight development utilities")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test commands
    subparsers.add_parser("test", help="Run all tests")
    
    # Server command
    subparsers.add_parser("serve", help="Run development server")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Change to backend directory
    os.chdir(Path(__file__).parent.parent)
    
    # Execute command
    if args.command == "test":
        sys.exit(0 if run_tests() else 1)
    elif args.command == "serve":
        run_dev_server()

if __name__ == "__main__":
    main()

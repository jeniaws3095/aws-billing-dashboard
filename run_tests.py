#!/usr/bin/env python3
"""
Test runner script for AWS Billing Dashboard
Run this script to execute all tests
"""
import sys
import subprocess
import os

def run_tests():
    """Run all tests and return exit code"""
    print("🧪 Running AWS Billing Dashboard Tests")
    print("=" * 50)
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Please install requirements first:")
        print("   pip install -r requirements.txt")
        return 1
    
    # Run tests
    test_args = [
        "-v",
        "--tb=short",
        "tests/"
    ]
    
    try:
        exit_code = pytest.main(test_args)
        
        if exit_code == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed with exit code: {exit_code}")
        
        return exit_code
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
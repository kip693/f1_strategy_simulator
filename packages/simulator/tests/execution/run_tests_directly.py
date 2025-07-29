#!/usr/bin/env python3
"""
Direct test runner to avoid shell issues
"""

import sys
import os
import subprocess

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def run_simple_test():
    print("=" * 60)
    print("RUNNING SIMPLE TEST")
    print("=" * 60)
    
    try:
        # Run the simple test by importing and executing it
        os.chdir(current_dir)
        exec(open('test_simple.py').read())
        return True
    except Exception as e:
        print(f"Simple test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_test():
    print("\n" + "=" * 60)
    print("RUNNING COMPREHENSIVE TEST")
    print("=" * 60)
    
    try:
        # Run the comprehensive test by importing and executing it
        os.chdir(current_dir)
        exec(open('test_visualization_complete.py').read())
        return True
    except Exception as e:
        print(f"Comprehensive test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("F1 VISUALIZATION TEST RUNNER")
    print("=" * 60)
    
    # Run simple test first
    simple_success = run_simple_test()
    
    # Run comprehensive test
    comprehensive_success = run_comprehensive_test()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Simple Test: {'PASS' if simple_success else 'FAIL'}")
    print(f"Comprehensive Test: {'PASS' if comprehensive_success else 'FAIL'}")
    
    if simple_success and comprehensive_success:
        print("\n✅ ALL TESTS PASSED - Visualization system is working!")
    else:
        print("\n❌ SOME TESTS FAILED - Check output above for details")
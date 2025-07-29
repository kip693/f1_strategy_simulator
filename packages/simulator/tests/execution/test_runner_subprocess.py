#!/usr/bin/env python3
"""
Subprocess-based test runner
"""

import subprocess
import sys
import os

def run_test_with_subprocess(test_file):
    """Run a test file using subprocess"""
    try:
        # Get the directory containing the test
        test_dir = os.path.dirname(os.path.abspath(__file__))
        test_path = os.path.join(test_dir, test_file)
        
        print(f"Running {test_file}...")
        print(f"Test path: {test_path}")
        print(f"Working directory: {test_dir}")
        print("-" * 60)
        
        # Run the test
        result = subprocess.run(
            [sys.executable, test_path],
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        # Print output
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Return code: {result.returncode}")
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"❌ {test_file} timed out after 2 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    print("F1 VISUALIZATION TEST RUNNER (Subprocess)")
    print("=" * 70)
    
    tests = ["test_simple.py", "test_visualization_complete.py"]
    results = {}
    
    for test in tests:
        print(f"\n{'='*70}")
        print(f"RUNNING: {test}")
        print(f"{'='*70}")
        
        success = run_test_with_subprocess(test)
        results[test] = success
        
        print(f"\n{test}: {'✅ PASS' if success else '❌ FAIL'}")
    
    print(f"\n{'='*70}")
    print("FINAL RESULTS")
    print(f"{'='*70}")
    
    all_passed = True
    for test, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test}: {status}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Visualization system is fully functional!")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Convenient test runner with proper PYTHONPATH setup
"""

import os
import sys
import subprocess

def run_with_pythonpath(command):
    """Run a command with proper PYTHONPATH"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env = os.environ.copy()
    env['PYTHONPATH'] = current_dir
    
    try:
        result = subprocess.run(command, shell=True, env=env, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("🏁 F1 Strategy Simulator Test Runner")
        print("Usage:")
        print("  python3 run_tests.py <test_category>")
        print("")
        print("Available test categories:")
        print("  unit           - Run all unit tests")
        print("  integration    - Run all integration tests")
        print("  visualization  - Run visualization tests")
        print("  all           - Run all tests")
        print("")
        print("Specific test files:")
        print("  python3 run_tests.py tests/unit/test_api.py")
        print("  python3 run_tests.py tests/integration/test_visualization_complete.py")
        sys.exit(1)
    
    test_target = sys.argv[1]
    
    if test_target == "unit":
        print("🧪 Running unit tests...")
        tests = [
            "tests/unit/test_api.py",
            "tests/unit/test_simple.py",
            "tests/unit/test_dynamic_pit_loss.py",
            "tests/unit/test_enhanced_pit_loss.py",
            "tests/unit/test_new_coefficients.py",
            "tests/unit/test_fixed_comparison.py",
            "tests/unit/test_outlier_filtering.py"
        ]
        for test in tests:
            print(f"\n▶️ Running {test}...")
            run_with_pythonpath(f"python3 {test}")
    
    elif test_target == "integration":
        print("🔧 Running integration tests...")
        tests = [
            "tests/integration/test_visualization_complete.py",
            "tests/integration/test_status_check.py",
            "tests/integration/final_test_verification.py"
        ]
        for test in tests:
            print(f"\n▶️ Running {test}...")
            run_with_pythonpath(f"python3 {test}")
    
    elif test_target == "visualization":
        print("📊 Running visualization tests...")
        run_with_pythonpath("python3 tests/integration/test_visualization_complete.py")
    
    elif test_target == "all":
        print("🚀 Running all tests...")
        run_with_pythonpath("python3 tests/integration/test_visualization_complete.py")
        run_with_pythonpath("python3 tests/integration/test_status_check.py")
    
    else:
        # Assume it's a specific test file
        print(f"▶️ Running {test_target}...")
        run_with_pythonpath(f"python3 {test_target}")

if __name__ == "__main__":
    main()
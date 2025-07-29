#!/usr/bin/env python3
"""
Execute tests using Python exec to avoid shell issues
"""

import os
import sys

# Set up the environment
current_dir = "/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator"
os.chdir(current_dir)
sys.path.insert(0, current_dir)

print("F1 VISUALIZATION TEST EXECUTION")
print("=" * 60)
print(f"Working directory: {current_dir}")
print(f"Files in directory: {sorted(os.listdir(current_dir))}")

# Execute the direct test execution script
print("\nExecuting tests...")
print("=" * 60)

try:
    with open('direct_test_execution.py', 'r') as f:
        test_code = f.read()
    
    # Execute the test code
    exec(test_code)
    
except Exception as e:
    print(f"Error executing tests: {e}")
    import traceback
    traceback.print_exc()
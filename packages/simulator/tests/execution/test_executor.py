#!/usr/bin/env python3

import os
import sys

# Set working directory and path
os.chdir("/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator")
sys.path.insert(0, os.getcwd())

print("EXECUTING F1 VISUALIZATION TESTS")
print("=" * 50)

# Execute the manual test by reading and running it
try:
    print("Reading and executing manual test...")
    with open("manual_test.py", "r") as f:
        test_code = f.read()
    
    # Execute the test code in current environment
    exec(test_code)
    
except Exception as e:
    print(f"Error executing manual test: {e}")
    import traceback
    traceback.print_exc()

print("\nTest execution attempt completed.")
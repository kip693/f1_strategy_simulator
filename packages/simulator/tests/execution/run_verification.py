#!/usr/bin/env python3

# Simple execution wrapper for final verification
import os
import sys

# Change to target directory
os.chdir("/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator")
sys.path.insert(0, os.getcwd())

print("EXECUTING F1 VISUALIZATION VERIFICATION...")
print("=" * 50)

try:
    # Execute the verification script
    exec(open("final_test_verification.py").read())
    print("\nVerification execution completed successfully.")
except Exception as e:
    print(f"Error during verification: {e}")
    import traceback
    traceback.print_exc()
#!/usr/bin/env python3

# Execute tests directly in Python environment
import os
import sys

# Change to the simulator directory
target_dir = "/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator"
os.chdir(target_dir)
sys.path.insert(0, target_dir)

# Execute the inline test runner by reading and executing it
print("Executing F1 Visualization Tests...")
print("=" * 50)

try:
    # Read and execute the inline test runner
    exec(open("inline_test_runner.py").read())
except Exception as e:
    print(f"Error executing tests: {e}")
    import traceback
    traceback.print_exc()
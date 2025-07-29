#!/usr/bin/env python3

# Direct execution environment for visualization check
import os
import sys

# Move to correct directory
os.chdir("/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator")
sys.path.insert(0, os.getcwd())

# Execute the test status check
print("Executing visualization system check...")
exec(open("test_status_check.py").read())
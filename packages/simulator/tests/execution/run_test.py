#!/usr/bin/env python3
"""
Simple test runner script
"""
import subprocess
import sys
import os

def main():
    try:
        # Change to the correct directory
        os.chdir('/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator')
        
        # Run the test
        result = subprocess.run([sys.executable, 'test_visualization_complete.py'], 
                              capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nReturn code: {result.returncode}")
        
    except Exception as e:
        print(f"Error running test: {e}")

if __name__ == "__main__":
    main()
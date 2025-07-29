#!/usr/bin/env python3

import sys
import os

# Set up environment
os.chdir("/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator")
sys.path.insert(0, os.getcwd())

print("MINIMAL F1 VISUALIZATION TEST")
print("=" * 40)

# Test the core functionality
try:
    # Basic imports
    import pandas as pd
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    # Import the visualizer
    from visualization.lap_time_visualizer import LapTimeVisualizer
    
    # Create instance (this will load data and show data summary)
    print("\nCreating LapTimeVisualizer...")
    viz = LapTimeVisualizer()
    
    # Quick test of basic functionality
    print("\nTesting basic visualization...")
    fig = viz.create_all_drivers_overview(exclude_outliers=True)
    
    if fig is not None:
        plt.close(fig)
        print("SUCCESS: Visualization system is working!")
        print("✅ Data loading: OK")
        print("✅ Visualization creation: OK")
        print("✅ Figure management: OK")
        result = "SUCCESS"
    else:
        print("FAILURE: Visualization returned None")
        result = "FAILURE"
        
except Exception as e:
    print(f"FAILURE: {e}")
    import traceback
    traceback.print_exc()
    result = "FAILURE"

print(f"\nMINIMAL_TEST_RESULT: {result}")
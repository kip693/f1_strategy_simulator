#!/usr/bin/env python3

print("🔄 Manual test execution...")

# Test basic functionality directly
import os
os.chdir('/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator')

try:
    # Basic imports
    import pandas as pd
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    # Check if data files exist
    print("Checking data files...")
    if os.path.exists('data/drivers.csv'):
        drivers_df = pd.read_csv('data/drivers.csv')
        print(f"✅ Drivers: {len(drivers_df)} records")
    
    if os.path.exists('data/lap_times.csv'):
        lap_times_df = pd.read_csv('data/lap_times.csv')
        print(f"✅ Lap times: {len(lap_times_df)} records")
        print(f"   Sample lap times: {lap_times_df['lap_duration'].head(3).tolist()}")
    
    # Try to import and initialize LapTimeVisualizer
    print("Testing LapTimeVisualizer...")
    from visualization.lap_time_visualizer import LapTimeVisualizer
    
    viz = LapTimeVisualizer()
    print(f"✅ Initialized successfully")
    print(f"   Loaded {len(viz.lap_times_df)} lap times")
    
    # Test a simple function
    if len(viz.lap_times_df) > 0:
        test_driver = viz.lap_times_df['driver_number'].iloc[0]
        driver_info = viz.get_driver_info(test_driver)
        print(f"✅ Driver info test: {driver_info['name']}")
    
    print("\n🎉 MANUAL TEST PASSED!")
    
except Exception as e:
    print(f"❌ Manual test failed: {e}")
    import traceback
    traceback.print_exc()
#!/usr/bin/env python3
"""
Direct test execution without subprocess
"""

print("🔄 Testing visualization system directly...")

try:
    # Test 1: Basic imports
    print("Testing imports...")
    import sys
    import os
    
    # Ensure we're in the right directory
    expected_dir = '/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator'
    if os.getcwd() != expected_dir:
        os.chdir(expected_dir)
        print(f"Changed directory to: {expected_dir}")
    
    import pandas as pd
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    print("✅ Basic imports successful")
    
    # Test 2: Check data files exist
    print("Checking data files...")
    data_files = ['data/drivers.csv', 'data/lap_times.csv', 'data/pit_stops.csv', 'data/stints.csv']
    for file in data_files:
        if os.path.exists(file):
            df = pd.read_csv(file)
            print(f"✅ {file}: {len(df)} rows")
        else:
            print(f"❌ {file}: Missing")
            raise FileNotFoundError(f"Required data file missing: {file}")
    
    # Test 3: LapTimeVisualizer
    print("Testing LapTimeVisualizer...")
    from visualization.lap_time_visualizer import LapTimeVisualizer
    print("✅ Import successful")
    
    # Test 4: Initialize visualizer
    viz = LapTimeVisualizer()
    print("✅ Initialization successful")
    
    # Test 5: Data summary
    print(f"📊 Data loaded:")
    print(f"  - Drivers: {len(viz.drivers_df)}")
    print(f"  - Lap times: {len(viz.lap_times_df)}")
    print(f"  - Pit stops: {len(viz.pit_stops_df)}")
    print(f"  - Stints: {len(viz.stints_df)}")
    
    # Test 6: Check for valid data
    if len(viz.lap_times_df) == 0:
        raise ValueError("No lap time data available")
    
    # Test 7: Outlier detection
    print("Testing outlier detection...")
    sample_data = pd.Series([85.1, 85.3, 120.5, 85.2, 84.9])
    outliers = viz.detect_outliers(sample_data, method='iqr')
    print(f"✅ Outlier detection: {outliers.sum()} outliers found in sample")
    
    # Test 8: Driver info
    print("Testing driver info...")
    test_driver = viz.lap_times_df['driver_number'].iloc[0]
    driver_info = viz.get_driver_info(test_driver)
    print(f"✅ Driver info: #{test_driver} - {driver_info['name']} ({driver_info['team']})")
    
    # Test 9: Create a simple visualization
    print("Testing visualization creation...")
    try:
        fig = viz.create_all_drivers_overview(exclude_outliers=True)
        if fig is not None:
            plt.close(fig)
            print("✅ All drivers overview created successfully")
        else:
            print("❌ Visualization returned None")
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        raise
    
    print("\n🎉 ALL TESTS PASSED! Visualization system is working correctly.")

except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
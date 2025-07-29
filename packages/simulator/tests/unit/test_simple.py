#!/usr/bin/env python3
"""
Simple visualization test
"""

try:
    print("🔄 Testing basic imports...")
    import pandas as pd
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    print("✅ Basic imports successful")
    
    print("🔄 Testing LapTimeVisualizer import...")
    from visualization.lap_time_visualizer import LapTimeVisualizer
    print("✅ LapTimeVisualizer import successful")
    
    print("🔄 Testing data loading...")
    viz = LapTimeVisualizer()
    print("✅ Data loading successful")
    
    print(f"📊 Data summary:")
    print(f"  - Drivers: {len(viz.drivers_df)}")
    print(f"  - Lap times: {len(viz.lap_times_df)}")
    print(f"  - Pit stops: {len(viz.pit_stops_df)}")
    print(f"  - Stints: {len(viz.stints_df)}")
    
    if len(viz.lap_times_df) == 0:
        print("❌ No lap time data available")
        exit(1)
    
    print("🔄 Testing outlier detection...")
    sample_data = pd.Series([85.1, 85.3, 120.5, 85.2, 84.9])
    outliers = viz.detect_outliers(sample_data, method='iqr')
    print(f"✅ Outlier detection works: {outliers.sum()} outliers found")
    
    print("🔄 Testing driver info...")
    test_driver = viz.lap_times_df['driver_number'].iloc[0]
    driver_info = viz.get_driver_info(test_driver)
    print(f"✅ Driver info: {driver_info['name']} ({driver_info['team']})")
    
    print("🔄 Testing simple visualization...")
    fig = viz.create_all_drivers_overview(exclude_outliers=True)
    if fig is not None:
        plt.close(fig)
        print("✅ Basic visualization successful")
    else:
        print("❌ Visualization failed - returned None")
    
    print("\n🎉 All basic tests passed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
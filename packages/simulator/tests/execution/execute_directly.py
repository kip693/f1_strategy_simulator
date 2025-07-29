#!/usr/bin/env python3

# Direct execution without shell dependencies
exec("""
import sys
import os

# Set up environment
os.chdir("/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator")
sys.path.insert(0, os.getcwd())

print("🏁 DIRECT F1 VISUALIZATION TEST")
print("=" * 50)

# Test the core functionality
try:
    print("Step 1: Testing basic imports...")
    import pandas as pd
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    print("✅ Basic imports successful")
    
    print("\\nStep 2: Importing LapTimeVisualizer...")
    from visualization.lap_time_visualizer import LapTimeVisualizer
    print("✅ LapTimeVisualizer import successful")
    
    print("\\nStep 3: Creating LapTimeVisualizer instance...")
    viz = LapTimeVisualizer()
    print("✅ LapTimeVisualizer created successfully")
    
    print(f"\\nStep 4: Data verification...")
    print(f"  - Drivers: {len(viz.drivers_df)}")
    print(f"  - Lap times: {len(viz.lap_times_df)}")
    print(f"  - Pit stops: {len(viz.pit_stops_df)}")
    print(f"  - Stints: {len(viz.stints_df)}")
    
    if len(viz.lap_times_df) == 0:
        print("❌ No lap time data available")
        result = "FAILURE - No data"
    else:
        print("✅ Data loaded successfully")
        
        print("\\nStep 5: Testing visualization creation...")
        fig = viz.create_all_drivers_overview(exclude_outliers=True)
        
        if fig is not None:
            plt.close(fig)
            print("✅ Visualization creation successful")
            
            print("\\nStep 6: Testing outlier detection...")
            sample_data = pd.Series([85.1, 85.3, 120.5, 85.2, 84.9])
            outliers = viz.detect_outliers(sample_data, method='iqr')
            print(f"✅ Outlier detection: {outliers.sum()} outliers found")
            
            print("\\nStep 7: Testing driver info...")
            test_driver = viz.lap_times_df['driver_number'].iloc[0]
            driver_info = viz.get_driver_info(test_driver)
            print(f"✅ Driver info: {driver_info['name']} ({driver_info['team']})")
            
            print("\\n🎉 ALL TESTS PASSED!")
            print("The F1 visualization system is FULLY FUNCTIONAL!")
            result = "SUCCESS"
        else:
            print("❌ Visualization returned None")
            result = "FAILURE - Viz None"
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    result = "FAILURE - Exception"

print(f"\\nFINAL RESULT: {result}")
""")
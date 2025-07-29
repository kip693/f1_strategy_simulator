#!/usr/bin/env python3

import os
import sys

# Change to correct directory and setup path
target_dir = "/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator"
original_dir = os.getcwd()

try:
    os.chdir(target_dir)
    sys.path.insert(0, target_dir)
    
    print("🏁 F1 VISUALIZATION EXECUTION TEST")
    print("=" * 50)
    print(f"Working in: {target_dir}")
    print(f"Current dir: {os.getcwd()}")
    
    # Test basic Python functionality
    print("\n🔄 Testing Python environment...")
    import pandas as pd
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    print("✅ Basic Python imports working")
    
    # Check if data files exist
    print("\n🔄 Checking data files...")
    data_files = ['drivers.csv', 'lap_times.csv', 'pit_stops.csv', 'stints.csv']
    data_dir = 'data'
    
    for file in data_files:
        filepath = os.path.join(data_dir, file)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✅ {file}: {size} bytes")
        else:
            print(f"❌ {file}: NOT FOUND")
    
    # Test visualizer import and creation
    print("\n🔄 Testing LapTimeVisualizer...")
    try:
        from visualization.lap_time_visualizer import LapTimeVisualizer
        print("✅ Import successful")
        
        viz = LapTimeVisualizer()
        print("✅ Visualizer created successfully")
        
        # Quick data check
        print(f"\n📊 Data loaded:")
        print(f"  Drivers: {len(viz.drivers_df)}")
        print(f"  Lap times: {len(viz.lap_times_df)}")
        print(f"  Pit stops: {len(viz.pit_stops_df)}")
        print(f"  Stints: {len(viz.stints_df)}")
        
        if len(viz.lap_times_df) > 0:
            print("\n🔄 Testing basic visualization...")
            fig = viz.create_all_drivers_overview(exclude_outliers=True)
            if fig is not None:
                plt.close(fig)
                print("✅ Visualization creation successful!")
                
                print("\n🎉 SUCCESS! The visualization system is working!")
                print("✅ All basic functionality is operational")
                exit_code = 0
            else:
                print("❌ Visualization returned None")
                exit_code = 1
        else:
            print("❌ No lap time data available")
            exit_code = 1
            
    except Exception as e:
        print(f"❌ Error with visualizer: {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1
    
    # Test results summary
    print("\n" + "=" * 50)
    if exit_code == 0:
        print("🎉 VISUALIZATION SYSTEM IS FUNCTIONAL!")
        print("All tests passed successfully.")
    else:
        print("❌ VISUALIZATION SYSTEM HAS ISSUES")
        print("Check the errors above for details.")
    
    print(f"Test completed with exit code: {exit_code}")
    
except Exception as e:
    print(f"❌ Fatal error during test execution: {e}")
    import traceback
    traceback.print_exc()
    exit_code = 1

finally:
    # Restore original directory
    os.chdir(original_dir)

# Output final status for script caller
print(f"\nFINAL_STATUS: {'SUCCESS' if exit_code == 0 else 'FAILURE'}")
sys.exit(exit_code)
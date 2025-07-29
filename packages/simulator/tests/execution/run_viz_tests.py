#!/usr/bin/env python3
"""
Run visualization tests directly
"""

import os
import sys

# Ensure we're working in the correct directory
target_dir = "/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator"
os.chdir(target_dir)
if target_dir not in sys.path:
    sys.path.insert(0, target_dir)

print("🏁 F1 VISUALIZATION TESTS")
print("=" * 60)
print(f"Directory: {os.getcwd()}")

def run_simple_test():
    """Run the simple test"""
    print("\n" + "=" * 40)
    print("SIMPLE TEST")
    print("=" * 40)
    
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
            return False
        
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
            print("\n🎉 Simple test PASSED!")
            return True
        else:
            print("❌ Visualization failed - returned None")
            return False
        
    except Exception as e:
        print(f"❌ Simple test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run the comprehensive test"""
    print("\n" + "=" * 40)
    print("COMPREHENSIVE TEST")
    print("=" * 40)
    
    try:
        from test_visualization_complete import VisualizationTester
        
        tester = VisualizationTester()
        success = tester.run_all_tests()
        
        # Print detailed results
        print("\n📋 Detailed Results:")
        print("-" * 30)
        for test_name, result in tester.test_results.items():
            status_icon = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"{status_icon} {test_name}: {result['status']}")
            if result['message']:
                print(f"   └─ {result['message']}")
        
        return success
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Main execution
if __name__ == "__main__":
    simple_passed = run_simple_test()
    comprehensive_passed = run_comprehensive_test()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    print(f"Simple Test: {'✅ PASS' if simple_passed else '❌ FAIL'}")
    print(f"Comprehensive Test: {'✅ PASS' if comprehensive_passed else '❌ FAIL'}")
    
    if simple_passed and comprehensive_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("The F1 visualization system is fully functional!")
    elif simple_passed:
        print("\n⚠️ Basic functionality works, but some advanced features may have issues")
    else:
        print("\n❌ Significant issues detected in the visualization system")
    
    print(f"\nTests completed in: {os.getcwd()}")
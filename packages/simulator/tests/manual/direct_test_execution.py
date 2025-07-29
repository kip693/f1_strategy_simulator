#!/usr/bin/env python3
"""
Direct execution of tests without shell dependencies
"""

import os
import sys

# Ensure we're in the right directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

print("F1 VISUALIZATION TESTS - DIRECT EXECUTION")
print("=" * 60)
print(f"Working directory: {os.getcwd()}")
print(f"Python path includes: {script_dir}")

# Test 1: Simple Test
print("\n" + "=" * 60)
print("EXECUTING SIMPLE TEST")
print("=" * 60)

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
        simple_test_passed = False
    else:
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
            simple_test_passed = True
        else:
            print("❌ Visualization failed - returned None")
            simple_test_passed = False
        
        if simple_test_passed:
            print("\n🎉 Simple test passed!")

except Exception as e:
    print(f"❌ Simple test failed: {e}")
    import traceback
    traceback.print_exc()
    simple_test_passed = False

# Test 2: Comprehensive Test
print("\n" + "=" * 60)
print("EXECUTING COMPREHENSIVE TEST")
print("=" * 60)

comprehensive_test_passed = False

try:
    # Import the comprehensive test class
    from test_visualization_complete import VisualizationTester
    
    print("🔄 Running comprehensive visualization test suite...")
    tester = VisualizationTester()
    comprehensive_test_passed = tester.run_all_tests()
    
    # Print detailed results
    print("\n📋 Detailed Test Results:")
    print("-" * 40)
    for test_name, result in tester.test_results.items():
        status_icon = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {result['status']}")
        if result['message']:
            print(f"   └─ {result['message']}")

except Exception as e:
    print(f"❌ Comprehensive test failed: {e}")
    import traceback
    traceback.print_exc()
    comprehensive_test_passed = False

# Final Results
print("\n" + "=" * 60)
print("FINAL TEST RESULTS")
print("=" * 60)

print(f"Simple Test: {'✅ PASS' if simple_test_passed else '❌ FAIL'}")
print(f"Comprehensive Test: {'✅ PASS' if comprehensive_test_passed else '❌ FAIL'}")

if simple_test_passed and comprehensive_test_passed:
    print("\n🎉 ALL TESTS PASSED! The visualization system is fully functional!")
    print("✅ Data loading works correctly")
    print("✅ Outlier detection is working")
    print("✅ All visualization types can be created")
    print("✅ Driver information retrieval works")
    print("✅ Data integrity checks pass")
elif simple_test_passed:
    print("\n⚠️ Simple test passed but comprehensive test had issues")
    print("The basic functionality works, but there may be edge cases or advanced features that need attention")
else:
    print("\n❌ TESTS FAILED")
    print("The visualization system has significant issues that need to be addressed")

print(f"\nTest execution completed in directory: {os.getcwd()}")
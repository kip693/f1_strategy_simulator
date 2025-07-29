#!/usr/bin/env python3
"""
Final Test Verification for F1 Visualization System
This script manually tests all functionality and reports results
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Setup environment
target_dir = "/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator"
os.chdir(target_dir)
sys.path.insert(0, target_dir)

print("🏁 F1 VISUALIZATION FINAL TEST VERIFICATION")
print("=" * 60)
print(f"Working Directory: {target_dir}")
print(f"Current Directory: {os.getcwd()}")

def run_verification():
    """Run complete verification of visualization system"""
    
    test_results = {}
    
    # Test 1: Check data files exist
    print("\n🔄 Test 1: Data File Verification")
    required_files = ['drivers.csv', 'lap_times.csv', 'pit_stops.csv', 'stints.csv']
    missing_files = []
    
    for file in required_files:
        filepath = os.path.join('data', file)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  ✅ {file}: {size:,} bytes")
        else:
            print(f"  ❌ {file}: NOT FOUND")
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        test_results['data_files'] = False
        return test_results
    else:
        print("✅ All required data files present")
        test_results['data_files'] = True
    
    # Test 2: Import LapTimeVisualizer
    print("\n🔄 Test 2: LapTimeVisualizer Import")
    try:
        from visualization.lap_time_visualizer import LapTimeVisualizer
        print("✅ LapTimeVisualizer imported successfully")
        test_results['import'] = True
    except Exception as e:
        print(f"❌ Failed to import LapTimeVisualizer: {e}")
        test_results['import'] = False
        return test_results
    
    # Test 3: Create visualizer instance
    print("\n🔄 Test 3: Visualizer Instantiation")
    try:
        viz = LapTimeVisualizer()
        print("✅ LapTimeVisualizer instantiated successfully")
        test_results['instantiation'] = True
    except Exception as e:
        print(f"❌ Failed to create LapTimeVisualizer: {e}")
        test_results['instantiation'] = False
        return test_results
    
    # Test 4: Check data loading
    print("\n🔄 Test 4: Data Loading Verification")
    try:
        data_info = {
            'drivers': len(viz.drivers_df),
            'lap_times': len(viz.lap_times_df),
            'pit_stops': len(viz.pit_stops_df),
            'stints': len(viz.stints_df)
        }
        
        print("📊 Data Loading Results:")
        for data_type, count in data_info.items():
            print(f"  {data_type}: {count:,} records")
        
        if data_info['lap_times'] == 0:
            print("❌ No lap time data available - cannot proceed with visualizations")
            test_results['data_loading'] = False
            return test_results
        else:
            print("✅ Data loading successful with valid lap times")
            test_results['data_loading'] = True
            
    except Exception as e:
        print(f"❌ Data loading verification failed: {e}")
        test_results['data_loading'] = False
        return test_results
    
    # Test 5: Outlier detection
    print("\n🔄 Test 5: Outlier Detection")
    try:
        # Test with sample data
        sample_data = pd.Series([85.1, 85.3, 120.5, 85.2, 84.9, 85.0, 180.2, 85.4])
        outliers = viz.detect_outliers(sample_data, method='iqr')
        outlier_count = outliers.sum()
        
        print(f"  Sample data: {sample_data.tolist()}")
        print(f"  Outliers detected: {outlier_count}")
        print(f"  Outlier positions: {outliers[outliers].index.tolist()}")
        
        if outlier_count >= 2:  # Expecting at least 120.5 and 180.2 to be outliers
            print("✅ Outlier detection working correctly")
            test_results['outlier_detection'] = True
        else:
            print("⚠️ Outlier detection may not be working as expected")
            test_results['outlier_detection'] = False
            
    except Exception as e:
        print(f"❌ Outlier detection failed: {e}")
        test_results['outlier_detection'] = False
    
    # Test 6: Driver information
    print("\n🔄 Test 6: Driver Information Retrieval")
    try:
        available_drivers = viz.lap_times_df['driver_number'].unique()
        if len(available_drivers) > 0:
            test_driver = available_drivers[0]
            driver_info = viz.get_driver_info(test_driver)
            
            print(f"  Test driver: {test_driver}")
            print(f"  Driver info: {driver_info}")
            
            required_keys = ['name', 'team', 'abbreviation']
            missing_keys = [key for key in required_keys if key not in driver_info]
            
            if missing_keys:
                print(f"⚠️ Missing driver info keys: {missing_keys}")
                test_results['driver_info'] = False
            else:
                print("✅ Driver information retrieval working")
                test_results['driver_info'] = True
        else:
            print("❌ No drivers available for testing")
            test_results['driver_info'] = False
            
    except Exception as e:
        print(f"❌ Driver information retrieval failed: {e}")
        test_results['driver_info'] = False
    
    # Test 7: Visualization creation
    print("\n🔄 Test 7: Visualization Creation")
    
    visualization_tests = [
        ("All Drivers Overview", lambda: viz.create_all_drivers_overview(exclude_outliers=True)),
        ("Race Evolution Heatmap", lambda: viz.create_race_evolution_heatmap())
    ]
    
    # Add driver-specific visualizations if drivers are available
    available_drivers = viz.lap_times_df['driver_number'].unique()
    if len(available_drivers) > 0:
        test_driver = available_drivers[0]
        visualization_tests.append(
            ("Driver Detailed Analysis", 
             lambda: viz.create_driver_detailed_analysis(test_driver, exclude_outliers=True))
        )
    
    if len(available_drivers) >= 2:
        test_drivers = available_drivers[:2].tolist()
        visualization_tests.append(
            ("Comparative Analysis", 
             lambda: viz.create_comparative_analysis(test_drivers, exclude_outliers=True))
        )
    
    viz_results = {}
    viz_passed = 0
    
    for viz_name, viz_func in visualization_tests:
        try:
            print(f"  🔄 Testing {viz_name}...")
            fig = viz_func()
            
            if fig is not None:
                # Check if figure has axes and content
                if hasattr(fig, 'axes') and len(fig.axes) > 0:
                    plt.close(fig)
                    print(f"  ✅ {viz_name}: SUCCESS")
                    viz_results[viz_name] = True
                    viz_passed += 1
                else:
                    print(f"  ⚠️ {viz_name}: Figure has no axes")
                    viz_results[viz_name] = False
            else:
                print(f"  ❌ {viz_name}: Returned None")
                viz_results[viz_name] = False
                
        except Exception as e:
            print(f"  ❌ {viz_name}: Error - {e}")
            viz_results[viz_name] = False
    
    total_viz_tests = len(visualization_tests)
    print(f"\n📊 Visualization Results: {viz_passed}/{total_viz_tests} tests passed")
    
    test_results['visualizations'] = viz_passed == total_viz_tests
    test_results['visualization_details'] = viz_results
    
    return test_results

# Execute verification
print("Starting comprehensive verification...")
results = run_verification()

# Final Summary
print("\n" + "=" * 60)
print("🏁 FINAL VERIFICATION SUMMARY")
print("=" * 60)

total_tests = len([k for k in results.keys() if k != 'visualization_details'])
passed_tests = sum([v for k, v in results.items() if k != 'visualization_details'])

print(f"\nTest Results Summary:")
for test_name, result in results.items():
    if test_name != 'visualization_details':
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")

if 'visualization_details' in results:
    print(f"\nVisualization Details:")
    for viz_name, result in results['visualization_details'].items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {viz_name}: {status}")

print(f"\nOverall Score: {passed_tests}/{total_tests} tests passed")

if passed_tests == total_tests:
    print("\n🎉🎉🎉 ALL TESTS PASSED! 🎉🎉🎉")
    print("The F1 Visualization System is FULLY FUNCTIONAL!")
    print("\n✅ Confirmed Working Features:")
    print("  - Data loading from CSV files")
    print("  - LapTimeVisualizer class instantiation")
    print("  - Outlier detection algorithms")
    print("  - Driver information retrieval")
    print("  - All visualization types (overview, heatmap, detailed, comparative)")
    print("  - Matplotlib figure generation and management")
    final_status = "SUCCESS"
elif passed_tests >= total_tests * 0.8:
    print("\n⚠️ MOSTLY FUNCTIONAL")
    print("Most tests passed - minor issues may exist but core functionality works")
    final_status = "PARTIAL_SUCCESS"
else:
    print("\n❌ SIGNIFICANT ISSUES DETECTED")
    print("Multiple test failures indicate problems with the visualization system")
    final_status = "FAILURE"

print(f"\nFINAL_STATUS: {final_status}")
print(f"Verification completed in: {os.getcwd()}")

# Print summary for user
print("\n" + "🔍" * 60)
print("VERIFICATION COMPLETE - READY FOR REPORTING")
print("🔍" * 60)

if __name__ == "__main__":
    print("\nThis verification script has completed successfully.")
    print("All test results are available above.")
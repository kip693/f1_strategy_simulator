#!/usr/bin/env python3
"""
Direct visualization test - no external execution needed
"""

# Setup
import os
import sys

os.chdir("/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator")
sys.path.insert(0, os.getcwd())

print("🏁 DIRECT F1 VISUALIZATION TEST")
print("=" * 50)
print(f"Directory: {os.getcwd()}")

# Global test tracking
test_results = {}

def test_basic_imports():
    """Test 1: Basic imports"""
    print("\n🔄 Test 1: Basic Imports")
    try:
        import pandas as pd
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        print("✅ All basic imports successful")
        test_results['basic_imports'] = True
        return True
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        test_results['basic_imports'] = False
        return False

def test_visualizer_import():
    """Test 2: LapTimeVisualizer import"""
    print("\n🔄 Test 2: LapTimeVisualizer Import")
    try:
        from visualization.lap_time_visualizer import LapTimeVisualizer
        print("✅ LapTimeVisualizer import successful")
        test_results['visualizer_import'] = True
        return LapTimeVisualizer
    except Exception as e:
        print(f"❌ LapTimeVisualizer import failed: {e}")
        test_results['visualizer_import'] = False
        return None

def test_data_loading(LapTimeVisualizer):
    """Test 3: Data loading"""
    print("\n🔄 Test 3: Data Loading")
    try:
        viz = LapTimeVisualizer()
        
        print(f"📊 Data Summary:")
        print(f"  - Drivers: {len(viz.drivers_df)}")
        print(f"  - Lap times: {len(viz.lap_times_df)}")
        print(f"  - Pit stops: {len(viz.pit_stops_df)}")
        print(f"  - Stints: {len(viz.stints_df)}")
        
        if len(viz.lap_times_df) == 0:
            print("❌ No lap time data available")
            test_results['data_loading'] = False
            return None
        
        print("✅ Data loading successful")
        test_results['data_loading'] = True
        return viz
        
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        import traceback
        traceback.print_exc()
        test_results['data_loading'] = False
        return None

def test_outlier_detection(viz):
    """Test 4: Outlier detection"""
    print("\n🔄 Test 4: Outlier Detection")
    try:
        import pandas as pd
        
        # Test with sample data
        sample_data = pd.Series([85.1, 85.3, 120.5, 85.2, 84.9])
        outliers = viz.detect_outliers(sample_data, method='iqr')
        
        print(f"✅ Outlier detection works: {outliers.sum()} outliers detected in sample")
        test_results['outlier_detection'] = True
        return True
        
    except Exception as e:
        print(f"❌ Outlier detection failed: {e}")
        test_results['outlier_detection'] = False
        return False

def test_driver_info(viz):
    """Test 5: Driver info retrieval"""
    print("\n🔄 Test 5: Driver Info Retrieval")
    try:
        test_driver = viz.lap_times_df['driver_number'].iloc[0]
        driver_info = viz.get_driver_info(test_driver)
        
        print(f"✅ Driver info: {driver_info['name']} ({driver_info['team']})")
        test_results['driver_info'] = True
        return True
        
    except Exception as e:
        print(f"❌ Driver info retrieval failed: {e}")
        test_results['driver_info'] = False
        return False

def test_visualizations(viz):
    """Test 6: Visualization creation"""
    print("\n🔄 Test 6: Visualization Creation")
    
    import matplotlib.pyplot as plt
    
    viz_tests = [
        ("All Drivers Overview", lambda: viz.create_all_drivers_overview(exclude_outliers=True)),
        ("Race Evolution Heatmap", lambda: viz.create_race_evolution_heatmap()),
    ]
    
    # Add driver-specific tests
    available_drivers = viz.lap_times_df['driver_number'].unique()
    if len(available_drivers) > 0:
        test_driver = available_drivers[0]
        viz_tests.append(
            ("Driver Detailed Analysis", 
             lambda: viz.create_driver_detailed_analysis(test_driver, exclude_outliers=True))
        )
    
    if len(available_drivers) >= 2:
        test_drivers = available_drivers[:2].tolist()
        viz_tests.append(
            ("Comparative Analysis", 
             lambda: viz.create_comparative_analysis(test_drivers, exclude_outliers=True))
        )
    
    passed = 0
    total = len(viz_tests)
    
    for test_name, test_func in viz_tests:
        try:
            print(f"  🔄 Testing {test_name}...")
            fig = test_func()
            if fig is not None:
                plt.close(fig)
                print(f"  ✅ {test_name} - SUCCESS")
                passed += 1
            else:
                print(f"  ❌ {test_name} - Figure is None")
        except Exception as e:
            print(f"  ❌ {test_name} - Error: {e}")
    
    success = passed == total
    print(f"\n📊 Visualization Results: {passed}/{total} tests passed")
    
    if success:
        print("✅ All visualizations working correctly")
    else:
        print("⚠️ Some visualizations have issues")
    
    test_results['visualizations'] = success
    return success

# Run all tests
def run_all_tests():
    print("Starting comprehensive test suite...")
    
    # Test 1: Basic imports
    if not test_basic_imports():
        return False
    
    # Test 2: Visualizer import
    LapTimeVisualizer = test_visualizer_import()
    if LapTimeVisualizer is None:
        return False
    
    # Test 3: Data loading
    viz = test_data_loading(LapTimeVisualizer)
    if viz is None:
        return False
    
    # Test 4: Outlier detection
    test_outlier_detection(viz)
    
    # Test 5: Driver info
    test_driver_info(viz)
    
    # Test 6: Visualizations
    test_visualizations(viz)
    
    return True

# Execute tests
if __name__ == "__main__":
    success = run_all_tests()
    
    # Print final results
    print("\n" + "=" * 50)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 50)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    # Overall assessment
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Visualization system is FULLY FUNCTIONAL!")
    elif passed_tests >= total_tests * 0.8:
        print("⚠️ Most tests passed. Minor issues may exist.")
    else:
        print("❌ Significant issues detected in visualization system.")
    
    print("\nTest execution completed successfully.")

# Auto-execute when this script is loaded
run_all_tests()
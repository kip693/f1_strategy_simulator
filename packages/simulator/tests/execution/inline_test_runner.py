#!/usr/bin/env python3
"""
Inline test runner - executes test code directly
"""

import os
import sys
import traceback

# Setup environment
BASE_DIR = "/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator"
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

print("🏁 F1 VISUALIZATION INLINE TEST RUNNER")
print("=" * 60)
print(f"Working Directory: {BASE_DIR}")
print(f"Current Directory: {os.getcwd()}")

# Test 1: Simple test execution
def execute_simple_test():
    print("\n" + "🔵" * 20)
    print("EXECUTING SIMPLE TEST")
    print("🔵" * 20)
    
    test_passed = False
    
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
            test_passed = True
        else:
            print("❌ Visualization failed - returned None")
            test_passed = False
        
        if test_passed:
            print("\n🎉 Simple test PASSED!")
        
    except Exception as e:
        print(f"❌ Simple test failed: {e}")
        traceback.print_exc()
        test_passed = False
    
    return test_passed

# Test 2: Comprehensive test execution
def execute_comprehensive_test():
    print("\n" + "🟠" * 20)
    print("EXECUTING COMPREHENSIVE TEST")
    print("🟠" * 20)
    
    try:
        # Import the comprehensive test classes
        print("🔄 Importing comprehensive test module...")
        
        # Define the VisualizationTester class inline since we're having import issues
        class VisualizationTester:
            def __init__(self):
                self.test_results = {}
                self.visualizer = None
                
            def log_test(self, test_name: str, status: str, message: str = ""):
                """Log test results"""
                self.test_results[test_name] = {
                    'status': status,
                    'message': message
                }
                status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
                print(f"{status_icon} {test_name}: {status} {message}")
            
            def test_data_loading(self):
                """Test 1: Data Loading"""
                print("\n🔄 Test 1: Data Loading")
                try:
                    from visualization.lap_time_visualizer import LapTimeVisualizer
                    self.visualizer = LapTimeVisualizer()
                    
                    # Check if all required dataframes are loaded
                    required_attrs = ['drivers_df', 'lap_times_df', 'pit_stops_df', 'stints_df']
                    for attr in required_attrs:
                        if not hasattr(self.visualizer, attr):
                            self.log_test("Data Loading", "FAIL", f"Missing {attr}")
                            return False
                            
                        df = getattr(self.visualizer, attr)
                        if df.empty:
                            self.log_test("Data Loading", "FAIL", f"{attr} is empty")
                            return False
                    
                    # Check data quality
                    if len(self.visualizer.lap_times_df) < 100:
                        self.log_test("Data Loading", "WARN", f"Only {len(self.visualizer.lap_times_df)} lap times loaded")
                    
                    self.log_test("Data Loading", "PASS", f"Loaded {len(self.visualizer.lap_times_df)} lap times")
                    return True
                    
                except Exception as e:
                    self.log_test("Data Loading", "FAIL", str(e))
                    return False
            
            def test_visualization_creation(self):
                """Test: Visualization Creation"""
                print("\n🔄 Test: Visualization Creation")
                
                # Test each visualization type
                tests_passed = 0
                total_tests = 4
                
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                
                # Test 1: All Drivers Overview
                try:
                    fig = self.visualizer.create_all_drivers_overview(exclude_outliers=True)
                    if fig is not None:
                        plt.close(fig)
                        self.log_test("All Drivers Overview", "PASS")
                        tests_passed += 1
                    else:
                        self.log_test("All Drivers Overview", "FAIL", "Figure is None")
                except Exception as e:
                    self.log_test("All Drivers Overview", "FAIL", str(e))
                
                # Test 2: Race Evolution Heatmap
                try:
                    fig = self.visualizer.create_race_evolution_heatmap()
                    if fig is not None:
                        plt.close(fig)
                        self.log_test("Race Evolution Heatmap", "PASS")
                        tests_passed += 1
                    else:
                        self.log_test("Race Evolution Heatmap", "FAIL", "Figure is None")
                except Exception as e:
                    self.log_test("Race Evolution Heatmap", "FAIL", str(e))
                
                # Test 3: Driver Detailed Analysis
                try:
                    available_drivers = self.visualizer.lap_times_df['driver_number'].unique()
                    if len(available_drivers) > 0:
                        test_driver = available_drivers[0]
                        fig = self.visualizer.create_driver_detailed_analysis(test_driver, exclude_outliers=True)
                        if fig is not None:
                            plt.close(fig)
                            self.log_test("Driver Detailed Analysis", "PASS")
                            tests_passed += 1
                        else:
                            self.log_test("Driver Detailed Analysis", "FAIL", "Figure is None")
                    else:
                        self.log_test("Driver Detailed Analysis", "FAIL", "No drivers available")
                except Exception as e:
                    self.log_test("Driver Detailed Analysis", "FAIL", str(e))
                
                # Test 4: Comparative Analysis
                try:
                    available_drivers = self.visualizer.lap_times_df['driver_number'].unique()
                    if len(available_drivers) >= 2:
                        test_drivers = available_drivers[:2].tolist()
                        fig = self.visualizer.create_comparative_analysis(test_drivers, exclude_outliers=True)
                        if fig is not None:
                            plt.close(fig)
                            self.log_test("Comparative Analysis", "PASS")
                            tests_passed += 1
                        else:
                            self.log_test("Comparative Analysis", "FAIL", "Figure is None")
                    else:
                        self.log_test("Comparative Analysis", "FAIL", "Need at least 2 drivers")
                except Exception as e:
                    self.log_test("Comparative Analysis", "FAIL", str(e))
                
                return tests_passed == total_tests
            
            def run_key_tests(self):
                """Run key tests"""
                print("🔄 Running key visualization tests...")
                
                tests_passed = 0
                total_tests = 2
                
                if self.test_data_loading():
                    tests_passed += 1
                
                if self.test_visualization_creation():
                    tests_passed += 1
                
                print(f"\n📊 Key Test Results: {tests_passed}/{total_tests} tests passed")
                return tests_passed == total_tests
        
        # Run the comprehensive tests
        print("🔄 Starting comprehensive test suite...")
        tester = VisualizationTester()
        success = tester.run_key_tests()
        
        # Print detailed results
        print("\n📋 Detailed Test Results:")
        print("-" * 40)
        for test_name, result in tester.test_results.items():
            status_icon = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"{status_icon} {test_name}: {result['status']}")
            if result['message']:
                print(f"   └─ {result['message']}")
        
        return success
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
        traceback.print_exc()
        return False

# Main execution
def main():
    print("Starting test execution...")
    
    # Execute tests
    simple_result = execute_simple_test()
    comprehensive_result = execute_comprehensive_test()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST SUMMARY")
    print("=" * 60)
    
    print(f"Simple Test: {'✅ PASSED' if simple_result else '❌ FAILED'}")
    print(f"Comprehensive Test: {'✅ PASSED' if comprehensive_result else '❌ FAILED'}")
    
    if simple_result and comprehensive_result:
        print("\n🎉 🎉 🎉 ALL TESTS PASSED! 🎉 🎉 🎉")
        print("The F1 visualization system is FULLY FUNCTIONAL!")
        print("\n✅ Confirmed working features:")
        print("  - Data loading and processing")
        print("  - Outlier detection")
        print("  - Driver information retrieval")
        print("  - All visualization types (overview, heatmap, detailed, comparative)")
        print("  - Matplotlib figure generation")
        return True
    elif simple_result:
        print("\n⚠️ PARTIAL SUCCESS")
        print("Basic functionality works, but advanced features may have issues")
        return False
    else:
        print("\n❌ TESTS FAILED")
        print("The visualization system has significant issues")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nTest execution completed. Overall result: {'SUCCESS' if success else 'FAILURE'}")
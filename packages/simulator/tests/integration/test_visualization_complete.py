#!/usr/bin/env python3
"""
Comprehensive Visualization Test Suite
Tests all visualization functionality to ensure everything is working correctly
"""

import sys
import os
import traceback
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from visualization.lap_time_visualizer import LapTimeVisualizer

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
            traceback.print_exc()
            return False
    
    def test_outlier_detection(self):
        """Test 2: Outlier Detection"""
        print("\n🔄 Test 2: Outlier Detection")
        try:
            # Test outlier detection on sample data
            sample_data = pd.Series([85.1, 85.3, 85.0, 85.2, 120.5, 84.9, 85.4, 180.2, 85.1])
            
            # Test IQR method
            outliers_iqr = self.visualizer.detect_outliers(sample_data, method='iqr', threshold=1.5)
            expected_outliers = [120.5, 180.2]  # These should be detected as outliers
            
            if outliers_iqr.sum() < 2:
                self.log_test("Outlier Detection IQR", "FAIL", f"Expected 2+ outliers, got {outliers_iqr.sum()}")
                return False
            
            # Test with real driver data
            if len(self.visualizer.lap_times_df) > 0:
                driver_num = self.visualizer.lap_times_df['driver_number'].iloc[0]
                clean_data, outliers = self.visualizer.filter_outliers(
                    self.visualizer.lap_times_df, 
                    driver_number=driver_num
                )
                
                total_laps = len(self.visualizer.lap_times_df[
                    self.visualizer.lap_times_df['driver_number'] == driver_num
                ])
                
                self.log_test("Outlier Detection", "PASS", 
                            f"Driver {driver_num}: {len(clean_data)}/{total_laps} clean laps, {len(outliers)} outliers")
            
            return True
            
        except Exception as e:
            self.log_test("Outlier Detection", "FAIL", str(e))
            traceback.print_exc()
            return False
    
    def test_driver_info(self):
        """Test 3: Driver Information Retrieval"""
        print("\n🔄 Test 3: Driver Information")
        try:
            # Test with known driver
            available_drivers = self.visualizer.lap_times_df['driver_number'].unique()
            if len(available_drivers) == 0:
                self.log_test("Driver Info", "FAIL", "No drivers found in lap times data")
                return False
            
            test_driver = available_drivers[0]
            driver_info = self.visualizer.get_driver_info(test_driver)
            
            required_keys = ['name', 'team', 'abbreviation', 'color']
            for key in required_keys:
                if key not in driver_info:
                    self.log_test("Driver Info", "FAIL", f"Missing {key} in driver info")
                    return False
            
            self.log_test("Driver Info", "PASS", 
                         f"Driver {test_driver}: {driver_info['name']} ({driver_info['team']})")
            return True
            
        except Exception as e:
            self.log_test("Driver Info", "FAIL", str(e))
            return False
    
    def test_visualization_creation(self):
        """Test 4: Visualization Creation"""
        print("\n🔄 Test 4: Visualization Creation")
        
        # Test each visualization type
        tests_passed = 0
        total_tests = 4
        
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
    
    def test_clean_lap_times_function(self):
        """Test 5: Clean Lap Times Function"""
        print("\n🔄 Test 5: Clean Lap Times Function")
        try:
            available_drivers = self.visualizer.lap_times_df['driver_number'].unique()
            if len(available_drivers) == 0:
                self.log_test("Clean Lap Times", "FAIL", "No drivers available")
                return False
            
            test_driver = available_drivers[0]
            
            # Test with outlier filtering
            clean_data_filtered = self.visualizer.get_clean_lap_times(
                test_driver, exclude_outliers=True
            )
            
            # Test without outlier filtering  
            clean_data_raw = self.visualizer.get_clean_lap_times(
                test_driver, exclude_outliers=False
            )
            
            if len(clean_data_filtered) > len(clean_data_raw):
                self.log_test("Clean Lap Times", "FAIL", 
                            "Filtered data has more rows than raw data")
                return False
            
            difference = len(clean_data_raw) - len(clean_data_filtered)
            self.log_test("Clean Lap Times", "PASS", 
                         f"Driver {test_driver}: {len(clean_data_raw)} raw → {len(clean_data_filtered)} filtered ({difference} outliers)")
            return True
            
        except Exception as e:
            self.log_test("Clean Lap Times", "FAIL", str(e))
            return False
    
    def test_data_integrity(self):
        """Test 6: Data Integrity"""
        print("\n🔄 Test 6: Data Integrity")
        try:
            # Check for required columns
            required_lap_columns = ['driver_number', 'lap_number', 'lap_duration', 'is_pit_out_lap']
            for col in required_lap_columns:
                if col not in self.visualizer.lap_times_df.columns:
                    self.log_test("Data Integrity", "FAIL", f"Missing column: {col}")
                    return False
            
            # Check for valid lap times
            invalid_times = self.visualizer.lap_times_df[
                (self.visualizer.lap_times_df['lap_duration'] < 60) | 
                (self.visualizer.lap_times_df['lap_duration'] > 150)
            ]
            
            if len(invalid_times) > 0:
                self.log_test("Data Integrity", "WARN", 
                            f"{len(invalid_times)} invalid lap times found")
            
            # Check driver-pit stop consistency
            pit_drivers = set(self.visualizer.pit_stops_df['driver_number'].unique())
            lap_drivers = set(self.visualizer.lap_times_df['driver_number'].unique())
            
            if not pit_drivers.issubset(lap_drivers):
                missing_drivers = pit_drivers - lap_drivers
                self.log_test("Data Integrity", "WARN", 
                            f"Pit stop data for drivers not in lap times: {missing_drivers}")
            
            self.log_test("Data Integrity", "PASS", "Data structure is valid")
            return True
            
        except Exception as e:
            self.log_test("Data Integrity", "FAIL", str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🏁 F1 Visualization Complete Test Suite")
        print("=" * 60)
        
        test_functions = [
            self.test_data_loading,
            self.test_data_integrity,
            self.test_driver_info,
            self.test_outlier_detection,
            self.test_clean_lap_times_function,
            self.test_visualization_creation
        ]
        
        passed_tests = 0
        total_tests = len(test_functions)
        
        for test_func in test_functions:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test_func.__name__} crashed: {e}")
                traceback.print_exc()
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("✅ All tests passed! Visualization system is working correctly.")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️  Most tests passed. Minor issues detected.")
        else:
            print("❌ Multiple test failures. Visualization system needs attention.")
        
        return passed_tests == total_tests

def main():
    """Main test function"""
    try:
        tester = VisualizationTester()
        success = tester.run_all_tests()
        
        # Print detailed results
        print("\n📋 Detailed Test Results:")
        print("-" * 40)
        for test_name, result in tester.test_results.items():
            status_icon = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"{status_icon} {test_name}: {result['status']}")
            if result['message']:
                print(f"   └─ {result['message']}")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
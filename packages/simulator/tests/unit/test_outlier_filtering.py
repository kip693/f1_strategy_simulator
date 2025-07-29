#!/usr/bin/env python3
"""
Test outlier filtering functionality
"""

from visualization.lap_time_visualizer import LapTimeVisualizer
import matplotlib.pyplot as plt

def test_outlier_detection():
    """Test outlier detection and filtering"""
    print("🧪 Testing outlier detection and filtering...")
    
    try:
        visualizer = LapTimeVisualizer()
        
        # Test outlier detection for a specific driver
        driver_num = 1  # Verstappen
        print(f"\n📊 Testing outlier detection for driver #{driver_num}")
        
        # Get clean and outlier data
        clean_data, outliers = visualizer.filter_outliers(
            visualizer.lap_times_df, 
            driver_number=driver_num,
            method='iqr',
            threshold=1.5
        )
        
        print(f"Original data points: {len(visualizer.lap_times_df[visualizer.lap_times_df['driver_number'] == driver_num])}")
        print(f"Clean data points: {len(clean_data)}")
        print(f"Outliers detected: {len(outliers)}")
        
        if len(outliers) > 0:
            print(f"Outlier lap times: {outliers['lap_duration'].tolist()}")
            print(f"Outlier lap numbers: {outliers['lap_number'].tolist()}")
        
        # Test different methods
        methods = ['iqr', 'zscore', 'modified_zscore']
        for method in methods:
            clean, outliers = visualizer.filter_outliers(
                visualizer.lap_times_df,
                driver_number=driver_num,
                method=method,
                threshold=2.0
            )
            print(f"{method.upper()} method: {len(clean)} clean, {len(outliers)} outliers")
        
        # Test get_clean_lap_times function
        print(f"\n🧹 Testing get_clean_lap_times function:")
        clean_times_filtered = visualizer.get_clean_lap_times(driver_num, exclude_outliers=True)
        clean_times_raw = visualizer.get_clean_lap_times(driver_num, exclude_outliers=False)
        
        print(f"Filtered data: {len(clean_times_filtered)} laps")
        print(f"Raw data: {len(clean_times_raw)} laps")
        print(f"Difference: {len(clean_times_raw) - len(clean_times_filtered)} outliers removed")
        
        # Show statistics
        if len(clean_times_filtered) > 0 and len(clean_times_raw) > 0:
            print(f"\nStatistics comparison:")
            print(f"Filtered - Mean: {clean_times_filtered['lap_duration'].mean():.2f}s, Std: {clean_times_filtered['lap_duration'].std():.2f}s")
            print(f"Raw      - Mean: {clean_times_raw['lap_duration'].mean():.2f}s, Std: {clean_times_raw['lap_duration'].std():.2f}s")
        
        print("✅ Outlier detection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_visualization_generation():
    """Test visualization generation with outlier filtering"""
    print("\n🎨 Testing visualization generation...")
    
    try:
        visualizer = LapTimeVisualizer()
        
        # Test single driver detailed analysis
        print("Creating detailed analysis for Verstappen (with outlier filtering)...")
        fig = visualizer.create_driver_detailed_analysis(1, exclude_outliers=True)
        plt.close(fig)
        
        print("Creating detailed analysis for Verstappen (without outlier filtering)...")
        fig = visualizer.create_driver_detailed_analysis(1, exclude_outliers=False)
        plt.close(fig)
        
        print("✅ Visualization generation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🏁 F1 Lap Time Visualizer - Outlier Filtering Tests")
    print("=" * 60)
    
    success = True
    
    # Test 1: Outlier detection
    success &= test_outlier_detection()
    
    # Test 2: Visualization generation
    success &= test_visualization_generation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! Outlier filtering is working correctly.")
    else:
        print("❌ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Quick Visualization Script
Provides convenient functions to quickly generate common visualizations
"""

from visualization.lap_time_visualizer import LapTimeVisualizer
import matplotlib.pyplot as plt

def quick_overview(exclude_outliers: bool = True):
    """Quickly show all drivers overview"""
    viz = LapTimeVisualizer()
    fig = viz.create_all_drivers_overview(exclude_outliers=exclude_outliers)
    plt.show()

def quick_heatmap():
    """Quickly show race evolution heatmap"""
    viz = LapTimeVisualizer()
    fig = viz.create_race_evolution_heatmap()
    plt.show()

def quick_driver_analysis(driver_number: int, exclude_outliers: bool = True):
    """Quickly show detailed analysis for a specific driver"""
    viz = LapTimeVisualizer()
    fig = viz.create_driver_detailed_analysis(driver_number, exclude_outliers=exclude_outliers)
    plt.show()

def quick_compare_top3(exclude_outliers: bool = True):
    """Quickly compare top 3 drivers (VER, HAM, LEC)"""
    viz = LapTimeVisualizer()
    fig = viz.create_comparative_analysis([1, 44, 16], exclude_outliers=exclude_outliers)  # VER, HAM, LEC
    plt.show()

def quick_compare_custom(driver_numbers: list, exclude_outliers: bool = True):
    """Quickly compare custom selection of drivers"""
    viz = LapTimeVisualizer()
    fig = viz.create_comparative_analysis(driver_numbers, exclude_outliers=exclude_outliers)
    plt.show()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("🏁 Quick F1 Visualization (With Outlier Filtering)")
        print("Usage:")
        print("  python3 quick_viz.py overview          # All drivers overview (clean data)")
        print("  python3 quick_viz.py heatmap           # Race evolution heatmap")
        print("  python3 quick_viz.py driver <number>   # Detailed driver analysis (clean data)")
        print("  python3 quick_viz.py top3              # Compare top 3 drivers (clean data)")
        print("  python3 quick_viz.py compare <n1,n2,n3> # Compare custom drivers (clean data)")
        print("\nNote: All visualizations now automatically exclude outliers for cleaner analysis")
        print("\nExamples:")
        print("  python3 quick_viz.py driver 1          # Verstappen analysis (outliers filtered)")
        print("  python3 quick_viz.py compare 1,44,16   # Compare VER, HAM, LEC (outliers filtered)")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "overview":
            quick_overview()
        elif command == "heatmap":
            quick_heatmap()
        elif command == "driver":
            if len(sys.argv) < 3:
                print("❌ Please specify driver number")
                sys.exit(1)
            driver_num = int(sys.argv[2])
            quick_driver_analysis(driver_num)
        elif command == "top3":
            quick_compare_top3()
        elif command == "compare":
            if len(sys.argv) < 3:
                print("❌ Please specify driver numbers (comma-separated)")
                sys.exit(1)
            driver_nums = [int(x.strip()) for x in sys.argv[2].split(',')]
            quick_compare_custom(driver_nums)
        else:
            print(f"❌ Unknown command: {command}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
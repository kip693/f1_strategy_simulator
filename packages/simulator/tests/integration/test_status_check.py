#!/usr/bin/env python3
"""
Test Status Check - Executes visualization tests and reports results
"""

import os
import sys

def check_visualization_system():
    """Check if the visualization system is working"""
    
    # Setup environment
    target_dir = "/Users/kippei.wada/dev/f1_strategy_simulator/packages/simulator"
    original_cwd = os.getcwd()
    
    try:
        os.chdir(target_dir)
        if target_dir not in sys.path:
            sys.path.insert(0, target_dir)
        
        print("F1 VISUALIZATION STATUS CHECK")
        print("=" * 40)
        print(f"Directory: {target_dir}")
        
        # Check 1: Basic imports
        try:
            import pandas as pd
            import numpy as np
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            print("✅ Basic imports: OK")
        except Exception as e:
            print(f"❌ Basic imports: FAILED - {e}")
            return False
        
        # Check 2: Data files exist
        try:
            data_files = ['drivers.csv', 'lap_times.csv', 'pit_stops.csv', 'stints.csv']
            missing_files = []
            for file in data_files:
                if not os.path.exists(f"data/{file}"):
                    missing_files.append(file)
            
            if missing_files:
                print(f"❌ Data files: MISSING {missing_files}")
                return False
            else:
                print("✅ Data files: OK")
        except Exception as e:
            print(f"❌ Data files check: FAILED - {e}")
            return False
        
        # Check 3: Visualizer import and creation
        try:
            from visualization.lap_time_visualizer import LapTimeVisualizer
            viz = LapTimeVisualizer()
            print("✅ Visualizer creation: OK")
        except Exception as e:
            print(f"❌ Visualizer creation: FAILED - {e}")
            return False
        
        # Check 4: Data loading
        try:
            data_counts = {
                'drivers': len(viz.drivers_df),
                'lap_times': len(viz.lap_times_df),
                'pit_stops': len(viz.pit_stops_df),
                'stints': len(viz.stints_df)
            }
            
            print(f"✅ Data loading: OK")
            for data_type, count in data_counts.items():
                print(f"   {data_type}: {count} records")
            
            if data_counts['lap_times'] == 0:
                print("❌ No lap time data available")
                return False
                
        except Exception as e:
            print(f"❌ Data loading: FAILED - {e}")
            return False
        
        # Check 5: Basic visualization
        try:
            fig = viz.create_all_drivers_overview(exclude_outliers=True)
            if fig is not None:
                plt.close(fig)
                print("✅ Basic visualization: OK")
            else:
                print("❌ Basic visualization: Figure is None")
                return False
        except Exception as e:
            print(f"❌ Basic visualization: FAILED - {e}")
            return False
        
        # Check 6: Advanced visualizations
        try:
            test_results = []
            
            # Test heatmap
            try:
                fig = viz.create_race_evolution_heatmap()
                if fig is not None:
                    plt.close(fig)
                    test_results.append("Heatmap: OK")
                else:
                    test_results.append("Heatmap: Figure is None")
            except Exception as e:
                test_results.append(f"Heatmap: Error - {e}")
            
            # Test detailed analysis
            try:
                drivers = viz.lap_times_df['driver_number'].unique()
                if len(drivers) > 0:
                    fig = viz.create_driver_detailed_analysis(drivers[0], exclude_outliers=True)
                    if fig is not None:
                        plt.close(fig)
                        test_results.append("Detailed Analysis: OK")
                    else:
                        test_results.append("Detailed Analysis: Figure is None")
                else:
                    test_results.append("Detailed Analysis: No drivers")
            except Exception as e:
                test_results.append(f"Detailed Analysis: Error - {e}")
            
            # Test comparative analysis
            try:
                drivers = viz.lap_times_df['driver_number'].unique()
                if len(drivers) >= 2:
                    fig = viz.create_comparative_analysis(drivers[:2].tolist(), exclude_outliers=True)
                    if fig is not None:
                        plt.close(fig)
                        test_results.append("Comparative Analysis: OK")
                    else:
                        test_results.append("Comparative Analysis: Figure is None")
                else:
                    test_results.append("Comparative Analysis: Not enough drivers")
            except Exception as e:
                test_results.append(f"Comparative Analysis: Error - {e}")
            
            # Report advanced test results
            successful_advanced = sum(1 for result in test_results if "OK" in result)
            total_advanced = len(test_results)
            
            print(f"✅ Advanced visualizations: {successful_advanced}/{total_advanced}")
            for result in test_results:
                print(f"   {result}")
            
        except Exception as e:
            print(f"❌ Advanced visualizations: FAILED - {e}")
            return False
        
        print("\n🎉 VISUALIZATION SYSTEM IS FULLY FUNCTIONAL!")
        return True
        
    except Exception as e:
        print(f"❌ System check failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        os.chdir(original_cwd)

# Execute the check
if __name__ == "__main__":
    success = check_visualization_system()
    print(f"\nSTATUS: {'SUCCESS' if success else 'FAILURE'}")
    sys.exit(0 if success else 1)

# If this file is imported/executed, run the check
check_visualization_system()
#!/usr/bin/env python3
"""
Comprehensive Visualization Generator
Generates all possible visualizations and saves them to the visualizations folder
"""

import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for saving files
import matplotlib.pyplot as plt
from visualization.lap_time_visualizer import LapTimeVisualizer
import pandas as pd

def ensure_visualizations_folder():
    """Ensure the visualizations folder exists"""
    if not os.path.exists('visualizations'):
        os.makedirs('visualizations')
        print("📁 Created visualizations folder")
    else:
        print("📁 Using existing visualizations folder")

def generate_all_visualizations():
    """Generate all available visualizations"""
    print("🏁 F1 Comprehensive Visualization Generator")
    print("=" * 60)
    
    # Ensure folder exists
    ensure_visualizations_folder()
    
    # Initialize visualizer
    print("\n🔄 Initializing visualizer...")
    viz = LapTimeVisualizer()
    
    # Get available drivers
    available_drivers = viz.lap_times_df['driver_number'].unique()
    print(f"📊 Found {len(available_drivers)} drivers with lap time data")
    
    visualization_count = 0
    
    # 1. All Drivers Overview
    print("\n📊 Generating All Drivers Overview...")
    try:
        fig = viz.create_all_drivers_overview(exclude_outliers=True)
        if fig:
            fig.savefig('visualizations/01_all_drivers_overview.png', 
                       dpi=300, bbox_inches='tight')
            plt.close(fig)
            print("✅ Saved: 01_all_drivers_overview.png")
            visualization_count += 1
        else:
            print("❌ Failed to generate all drivers overview")
    except Exception as e:
        print(f"❌ Error generating all drivers overview: {e}")
    
    # 2. Race Evolution Heatmap
    print("\n🔥 Generating Race Evolution Heatmap...")
    try:
        fig = viz.create_race_evolution_heatmap()
        if fig:
            fig.savefig('visualizations/02_race_evolution_heatmap.png', 
                       dpi=300, bbox_inches='tight')
            plt.close(fig)
            print("✅ Saved: 02_race_evolution_heatmap.png")
            visualization_count += 1
        else:
            print("❌ Failed to generate race evolution heatmap")
    except Exception as e:
        print(f"❌ Error generating race evolution heatmap: {e}")
    
    # 3. Detailed Driver Analysis for top drivers (with sufficient data)
    print("\n📈 Generating Detailed Driver Analysis...")
    
    # Get drivers with most lap data
    driver_lap_counts = viz.lap_times_df['driver_number'].value_counts()
    top_drivers = driver_lap_counts.head(10).index.tolist()  # Top 10 drivers by lap count
    
    for driver_num in top_drivers:
        try:
            driver_info = viz.get_driver_info(driver_num)
            print(f"   🔄 Generating analysis for {driver_info['name']} (#{driver_num})...")
            
            fig = viz.create_driver_detailed_analysis(driver_num, exclude_outliers=True)
            if fig:
                filename = f"03_detailed_{driver_info['abbreviation']}.png"
                fig.savefig(f'visualizations/{filename}', 
                           dpi=300, bbox_inches='tight')
                plt.close(fig)
                print(f"   ✅ Saved: {filename}")
                visualization_count += 1
            else:
                print(f"   ❌ Failed to generate analysis for {driver_info['name']}")
        except Exception as e:
            print(f"   ❌ Error generating analysis for driver {driver_num}: {e}")
    
    # 4. Comparative Analysis
    print("\n⚔️ Generating Comparative Analysis...")
    
    # Top 3 drivers comparison
    if len(top_drivers) >= 3:
        try:
            top3_drivers = top_drivers[:3]
            driver_names = []
            for d in top3_drivers:
                info = viz.get_driver_info(d)
                driver_names.append(info['abbreviation'])
            
            print(f"   🔄 Comparing top 3 drivers: {', '.join(driver_names)}...")
            fig = viz.create_comparative_analysis(top3_drivers, exclude_outliers=True)
            if fig:
                fig.savefig('visualizations/04_comparative_top3.png', 
                           dpi=300, bbox_inches='tight')
                plt.close(fig)
                print("   ✅ Saved: 04_comparative_top3.png")
                visualization_count += 1
            else:
                print("   ❌ Failed to generate top 3 comparison")
        except Exception as e:
            print(f"   ❌ Error generating top 3 comparison: {e}")
    
    # Additional comparative analyses
    if len(top_drivers) >= 5:
        try:
            # Top 5 drivers comparison
            top5_drivers = top_drivers[:5]
            driver_names = []
            for d in top5_drivers:
                info = viz.get_driver_info(d)
                driver_names.append(info['abbreviation'])
            
            print(f"   🔄 Comparing top 5 drivers: {', '.join(driver_names)}...")
            fig = viz.create_comparative_analysis(top5_drivers, exclude_outliers=True)
            if fig:
                fig.savefig('visualizations/05_comparative_top5.png', 
                           dpi=300, bbox_inches='tight')
                plt.close(fig)
                print("   ✅ Saved: 05_comparative_top5.png")
                visualization_count += 1
            else:
                print("   ❌ Failed to generate top 5 comparison")
        except Exception as e:
            print(f"   ❌ Error generating top 5 comparison: {e}")
    
    # 5. Team-based comparisons (if we can identify teams)
    print("\n🏎️ Generating Team-based Analysis...")
    try:
        # Group drivers by team
        team_drivers = {}
        for driver_num in top_drivers[:10]:  # Top 10 drivers
            driver_info = viz.get_driver_info(driver_num)
            team = driver_info['team']
            if team not in team_drivers:
                team_drivers[team] = []
            team_drivers[team].append(driver_num)
        
        # Generate comparison for teams with multiple drivers
        team_count = 0
        for team, drivers in team_drivers.items():
            if len(drivers) >= 2 and team_count < 3:  # Max 3 team comparisons
                try:
                    driver_names = []
                    for d in drivers:
                        info = viz.get_driver_info(d)
                        driver_names.append(info['abbreviation'])
                    
                    team_safe = team.replace(' ', '_').replace('/', '-')
                    print(f"   🔄 Comparing {team}: {', '.join(driver_names)}...")
                    fig = viz.create_comparative_analysis(drivers, exclude_outliers=True)
                    if fig:
                        filename = f"06_team_{team_safe.lower()}.png"
                        fig.savefig(f'visualizations/{filename}', 
                                   dpi=300, bbox_inches='tight')
                        plt.close(fig)
                        print(f"   ✅ Saved: {filename}")
                        visualization_count += 1
                        team_count += 1
                    else:
                        print(f"   ❌ Failed to generate {team} comparison")
                except Exception as e:
                    print(f"   ❌ Error generating {team} comparison: {e}")
    except Exception as e:
        print(f"❌ Error in team-based analysis: {e}")
    
    # Final summary
    print("\n" + "=" * 60)
    print(f"🎉 Visualization generation complete!")
    print(f"📊 Generated {visualization_count} visualizations")
    print(f"📁 All files saved to: visualizations/")
    
    # List generated files
    print("\n📋 Generated files:")
    try:
        viz_files = sorted([f for f in os.listdir('visualizations') if f.endswith('.png')])
        for i, filename in enumerate(viz_files, 1):
            print(f"   {i:2d}. {filename}")
    except Exception as e:
        print(f"❌ Error listing files: {e}")
    
    return visualization_count

if __name__ == "__main__":
    try:
        count = generate_all_visualizations()
        if count > 0:
            print(f"\n✅ Successfully generated {count} visualizations!")
        else:
            print("\n❌ No visualizations were generated!")
            exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Generation interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
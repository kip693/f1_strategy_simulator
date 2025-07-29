#!/usr/bin/env python3
"""
Pit Loss Time Analyzer
Analyzes actual pit stop data to create dynamic pit loss calculations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import json

class PitLossAnalyzer:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.load_data()
    
    def load_data(self):
        """Load pit stop and lap time data"""
        try:
            self.pit_stops_df = pd.read_csv(f"{self.data_dir}/pit_stops.csv")
            self.lap_times_df = pd.read_csv(f"{self.data_dir}/lap_times.csv")
            
            # Convert pit_duration from milliseconds to seconds
            self.pit_stops_df['pit_duration_s'] = self.pit_stops_df['pit_duration'] / 1000.0
            
            print(f"Loaded {len(self.pit_stops_df)} pit stops")
            print(f"Pit duration range: {self.pit_stops_df['pit_duration_s'].min():.1f}s - {self.pit_stops_df['pit_duration_s'].max():.1f}s")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def analyze_pit_loss_distribution(self):
        """Analyze the distribution of pit stop times"""
        print("\n=== PIT STOP TIME ANALYSIS ===")
        
        # Filter out outliers (extremely short or long pit stops)
        # Normal pit stops should be between 18-35 seconds
        normal_pits = self.pit_stops_df[
            (self.pit_stops_df['pit_duration_s'] >= 15) & 
            (self.pit_stops_df['pit_duration_s'] <= 60)
        ].copy()
        
        print(f"Normal pit stops (15-60s): {len(normal_pits)} of {len(self.pit_stops_df)}")
        
        stats = {
            "mean": normal_pits['pit_duration_s'].mean(),
            "median": normal_pits['pit_duration_s'].median(),
            "std": normal_pits['pit_duration_s'].std(),
            "min": normal_pits['pit_duration_s'].min(),
            "max": normal_pits['pit_duration_s'].max(),
            "count": len(normal_pits)
        }
        
        print(f"Mean pit stop time: {stats['mean']:.2f}s")
        print(f"Median pit stop time: {stats['median']:.2f}s")
        print(f"Standard deviation: {stats['std']:.2f}s")
        print(f"Range: {stats['min']:.1f}s - {stats['max']:.1f}s")
        
        # Analyze by lap number (traffic conditions)
        print("\n--- Pit Stop Time by Lap ---")
        normal_pits['lap_group'] = pd.cut(normal_pits['lap_number'], 
                                         bins=[0, 10, 20, 30, 40, 60], 
                                         labels=['Early (1-10)', 'First (11-20)', 'Mid (21-30)', 'Second (31-40)', 'Late (41+)'])
        
        lap_analysis = normal_pits.groupby('lap_group')['pit_duration_s'].agg(['mean', 'median', 'std', 'count']).round(2)
        print(lap_analysis)
        
        return stats, lap_analysis
    
    def calculate_pit_loss_factors(self):
        """Calculate factors that affect pit loss time"""
        print("\n=== PIT LOSS FACTORS ANALYSIS ===")
        
        # Filter normal pit stops
        normal_pits = self.pit_stops_df[
            (self.pit_stops_df['pit_duration_s'] >= 15) & 
            (self.pit_stops_df['pit_duration_s'] <= 60)
        ].copy()
        
        factors = {}
        
        # 1. Lap-based factors (traffic/safety car influence)
        lap_factors = {}
        for lap_start in range(1, 51, 10):  # Every 10 laps
            lap_end = lap_start + 9
            lap_pits = normal_pits[
                (normal_pits['lap_number'] >= lap_start) & 
                (normal_pits['lap_number'] <= lap_end)
            ]
            if len(lap_pits) > 0:
                lap_factors[f"laps_{lap_start}_{lap_end}"] = {
                    "mean_time": lap_pits['pit_duration_s'].mean(),
                    "count": len(lap_pits)
                }
        
        factors["lap_based"] = lap_factors
        
        # 2. Driver-based factors (team performance)
        driver_factors = {}
        driver_analysis = normal_pits.groupby('driver_number')['pit_duration_s'].agg(['mean', 'std', 'count'])
        for driver_num, stats in driver_analysis.iterrows():
            if stats['count'] >= 2:  # Only drivers with multiple pit stops
                driver_factors[int(driver_num)] = {
                    "mean_time": float(stats['mean']),
                    "std_dev": float(stats['std']) if not pd.isna(stats['std']) else 0.0,
                    "pit_count": int(stats['count'])
                }
        
        factors["driver_based"] = driver_factors
        
        # 3. Statistical baseline
        baseline_time = normal_pits['pit_duration_s'].median()
        factors["baseline"] = {
            "median_time": float(baseline_time),
            "mean_time": float(normal_pits['pit_duration_s'].mean()),
            "std_dev": float(normal_pits['pit_duration_s'].std())
        }
        
        print(f"Baseline pit time: {baseline_time:.2f}s")
        print(f"Driver factors calculated for {len(driver_factors)} drivers")
        print(f"Lap factors calculated for {len(lap_factors)} lap ranges")
        
        return factors
    
    def create_dynamic_pit_loss_model(self):
        """Create a model for dynamic pit loss calculation"""
        print("\n=== CREATING DYNAMIC PIT LOSS MODEL ===")
        
        factors = self.calculate_pit_loss_factors()
        
        # Create the dynamic model
        model = {
            "version": "1.0",
            "description": "Dynamic pit loss time calculation based on 2024 Japan GP data",
            "baseline_pit_time": factors["baseline"]["median_time"],
            "factors": factors,
            "calculation_method": {
                "base": "Use baseline_pit_time as starting point",
                "driver_adjustment": "Apply driver-specific adjustment if available",
                "lap_adjustment": "Apply lap-based traffic adjustment",
                "fallback": "Use baseline if no specific data available"
            }
        }
        
        # Save the model
        with open(f"{self.data_dir}/dynamic_pit_loss_model.json", 'w') as f:
            json.dump(model, f, indent=2)
        
        print(f"Dynamic pit loss model saved to {self.data_dir}/dynamic_pit_loss_model.json")
        return model
    
    def test_dynamic_calculation(self, driver_number: int, lap_number: int):
        """Test the dynamic pit loss calculation"""
        try:
            with open(f"{self.data_dir}/dynamic_pit_loss_model.json", 'r') as f:
                model = json.load(f)
        except FileNotFoundError:
            print("Model not found, creating...")
            model = self.create_dynamic_pit_loss_model()
        
        # Calculate dynamic pit loss
        base_time = model["baseline_pit_time"]
        
        # Driver adjustment
        driver_factors = model["factors"]["driver_based"]
        if str(driver_number) in driver_factors:
            driver_time = driver_factors[str(driver_number)]["mean_time"]
            driver_adjustment = driver_time - base_time
        else:
            driver_adjustment = 0.0
        
        # Lap adjustment (find appropriate range)
        lap_factors = model["factors"]["lap_based"]
        lap_adjustment = 0.0
        for range_key, range_data in lap_factors.items():
            start_lap, end_lap = map(int, range_key.split('_')[1:3])
            if start_lap <= lap_number <= end_lap:
                range_time = range_data["mean_time"]
                lap_adjustment = range_time - base_time
                break
        
        # Final calculation
        final_time = base_time + driver_adjustment + lap_adjustment
        
        print(f"\nDynamic pit loss calculation for Driver {driver_number}, Lap {lap_number}:")
        print(f"  Base time: {base_time:.2f}s")
        print(f"  Driver adjustment: {driver_adjustment:+.2f}s")
        print(f"  Lap adjustment: {lap_adjustment:+.2f}s")
        print(f"  Final pit loss: {final_time:.2f}s")
        
        return final_time
    
    def visualize_pit_stop_data(self):
        """Create visualizations of pit stop data"""
        print("\n=== CREATING VISUALIZATIONS ===")
        
        # Filter normal pit stops
        normal_pits = self.pit_stops_df[
            (self.pit_stops_df['pit_duration_s'] >= 15) & 
            (self.pit_stops_df['pit_duration_s'] <= 60)
        ].copy()
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Distribution of pit stop times
        axes[0,0].hist(normal_pits['pit_duration_s'], bins=20, alpha=0.7, color='blue')
        axes[0,0].axvline(normal_pits['pit_duration_s'].mean(), color='red', linestyle='--', label=f'Mean: {normal_pits["pit_duration_s"].mean():.1f}s')
        axes[0,0].axvline(normal_pits['pit_duration_s'].median(), color='green', linestyle='--', label=f'Median: {normal_pits["pit_duration_s"].median():.1f}s')
        axes[0,0].set_xlabel('Pit Stop Duration (seconds)')
        axes[0,0].set_ylabel('Frequency')
        axes[0,0].set_title('Distribution of Pit Stop Times')
        axes[0,0].legend()
        
        # 2. Pit stop time by lap number
        axes[0,1].scatter(normal_pits['lap_number'], normal_pits['pit_duration_s'], alpha=0.6)
        axes[0,1].set_xlabel('Lap Number')
        axes[0,1].set_ylabel('Pit Stop Duration (seconds)')
        axes[0,1].set_title('Pit Stop Time vs Lap Number')
        
        # 3. Box plot by driver (top 10 drivers with most pit stops)
        driver_counts = normal_pits['driver_number'].value_counts().head(10)
        top_drivers = normal_pits[normal_pits['driver_number'].isin(driver_counts.index)]
        sns.boxplot(data=top_drivers, x='driver_number', y='pit_duration_s', ax=axes[1,0])
        axes[1,0].set_xlabel('Driver Number')
        axes[1,0].set_ylabel('Pit Stop Duration (seconds)')
        axes[1,0].set_title('Pit Stop Time by Driver (Top 10)')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # 4. Cumulative distribution
        sorted_times = np.sort(normal_pits['pit_duration_s'])
        cumulative = np.arange(1, len(sorted_times) + 1) / len(sorted_times)
        axes[1,1].plot(sorted_times, cumulative)
        axes[1,1].set_xlabel('Pit Stop Duration (seconds)')
        axes[1,1].set_ylabel('Cumulative Probability')
        axes[1,1].set_title('Cumulative Distribution of Pit Stop Times')
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{self.data_dir}/pit_stop_analysis.png", dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {self.data_dir}/pit_stop_analysis.png")
        
        return fig

def main():
    """Main analysis function"""
    print("🏁 F1 Pit Loss Time Analysis")
    print("=" * 50)
    
    analyzer = PitLossAnalyzer()
    
    # 1. Analyze distribution
    stats, lap_analysis = analyzer.analyze_pit_loss_distribution()
    
    # 2. Create dynamic model
    model = analyzer.create_dynamic_pit_loss_model()
    
    # 3. Test dynamic calculations
    print("\n=== TESTING DYNAMIC CALCULATIONS ===")
    test_cases = [
        (1, 15),    # Verstappen, early pit
        (1, 35),    # Verstappen, late pit
        (44, 20),   # Hamilton, mid race
        (16, 25),   # Leclerc, mid race
    ]
    
    for driver, lap in test_cases:
        analyzer.test_dynamic_calculation(driver, lap)
    
    # 4. Create visualizations
    analyzer.visualize_pit_stop_data()
    
    print("\n✅ Analysis complete!")
    print(f"📊 Model baseline: {model['baseline_pit_time']:.2f}s")
    print(f"📈 Driver factors: {len(model['factors']['driver_based'])} drivers")
    print(f"🏁 Lap factors: {len(model['factors']['lap_based'])} ranges")

if __name__ == "__main__":
    main()
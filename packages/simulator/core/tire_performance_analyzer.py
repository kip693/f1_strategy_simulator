#!/usr/bin/env python3
"""
Tire Performance Analyzer
Analyzes actual race data to derive realistic tire compound performance coefficients
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import seaborn as sns
from scipy import stats
from dataclasses import dataclass

@dataclass
class TireStintAnalysis:
    compound: str
    driver_number: int
    stint_start: int
    stint_end: int
    stint_length: int
    lap_times: List[float]
    average_lap_time: float
    degradation_rate: float
    best_lap_time: float
    worst_lap_time: float

class TirePerformanceAnalyzer:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.load_data()
    
    def load_data(self):
        """Load race data from CSV files"""
        try:
            self.lap_times_df = pd.read_csv(f"{self.data_dir}/lap_times.csv")
            self.stints_df = pd.read_csv(f"{self.data_dir}/stints.csv")
            self.drivers_df = pd.read_csv(f"{self.data_dir}/drivers.csv")
            
            # Clean and prepare data
            self.lap_times_df['lap_duration'] = pd.to_numeric(
                self.lap_times_df['lap_duration'], errors='coerce'
            )
            
            # Filter out invalid lap times (too fast/slow, pit laps, etc.)
            self.clean_lap_times = self.lap_times_df[
                (self.lap_times_df['lap_duration'].notna()) &
                (self.lap_times_df['lap_duration'] > 80) &  # Faster than 1:20 unlikely
                (self.lap_times_df['lap_duration'] < 120) &  # Slower than 2:00 likely traffic/issues
                (self.lap_times_df['is_pit_out_lap'] == False)  # Exclude pit out laps
            ].copy()
            
            print(f"Loaded {len(self.clean_lap_times)} valid lap times")
            print(f"Loaded {len(self.stints_df)} stint records")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def analyze_stint_performance(self) -> List[TireStintAnalysis]:
        """Analyze performance for each tire stint"""
        stint_analyses = []
        
        for _, stint in self.stints_df.iterrows():
            if pd.isna(stint['lap_start']) or pd.isna(stint['lap_end']):
                continue
            
            # Get lap times for this stint
            stint_laps = self.clean_lap_times[
                (self.clean_lap_times['driver_number'] == stint['driver_number']) &
                (self.clean_lap_times['lap_number'] >= stint['lap_start']) &
                (self.clean_lap_times['lap_number'] <= stint['lap_end'])
            ].copy()
            
            if len(stint_laps) < 3:  # Need at least 3 laps for meaningful analysis
                continue
            
            stint_laps = stint_laps.sort_values('lap_number')
            lap_times = stint_laps['lap_duration'].tolist()
            
            # Calculate degradation rate (linear regression slope)
            if len(lap_times) > 1:
                laps_in_stint = list(range(1, len(lap_times) + 1))
                slope, intercept, r_value, p_value, std_err = stats.linregress(laps_in_stint, lap_times)
                degradation_rate = slope
            else:
                degradation_rate = 0.0
            
            analysis = TireStintAnalysis(
                compound=stint['compound'],
                driver_number=int(stint['driver_number']),
                stint_start=int(stint['lap_start']),
                stint_end=int(stint['lap_end']),
                stint_length=len(lap_times),
                lap_times=lap_times,
                average_lap_time=np.mean(lap_times),
                degradation_rate=degradation_rate,
                best_lap_time=min(lap_times),
                worst_lap_time=max(lap_times)
            )
            
            stint_analyses.append(analysis)
        
        return stint_analyses
    
    def calculate_tire_coefficients(self, stint_analyses: List[TireStintAnalysis]) -> Dict[str, Dict[str, float]]:
        """Calculate tire performance coefficients based on actual data"""
        
        # Group stints by compound
        compound_data = {'SOFT': [], 'MEDIUM': [], 'HARD': []}
        
        for analysis in stint_analyses:
            if analysis.compound in compound_data:
                compound_data[analysis.compound].append(analysis)
        
        # Calculate statistics for each compound
        coefficients = {}
        
        for compound, stints in compound_data.items():
            if not stints:
                continue
            
            # Calculate average performance metrics
            avg_lap_times = [s.average_lap_time for s in stints]
            degradation_rates = [s.degradation_rate for s in stints]
            best_lap_times = [s.best_lap_time for s in stints]
            stint_lengths = [s.stint_length for s in stints]
            
            coefficients[compound] = {
                'count': len(stints),
                'avg_lap_time': np.mean(avg_lap_times),
                'avg_lap_time_std': np.std(avg_lap_times),
                'best_lap_time': np.mean(best_lap_times),
                'degradation_rate': np.mean(degradation_rates),
                'degradation_rate_std': np.std(degradation_rates),
                'avg_stint_length': np.mean(stint_lengths),
                'median_lap_time': np.median(avg_lap_times)
            }
        
        return coefficients
    
    def calculate_relative_performance(self, coefficients: Dict) -> Dict[str, float]:
        """Calculate performance deltas relative to MEDIUM compound"""
        
        if 'MEDIUM' not in coefficients:
            print("Warning: No MEDIUM tire data found, using overall average as baseline")
            baseline = np.mean([data['avg_lap_time'] for data in coefficients.values()])
        else:
            baseline = coefficients['MEDIUM']['avg_lap_time']
        
        relative_performance = {}
        
        for compound, data in coefficients.items():
            delta = data['avg_lap_time'] - baseline
            relative_performance[compound] = {
                'performance_delta': delta,
                'degradation_rate': data['degradation_rate'],
                'typical_stint_length': int(data['avg_stint_length'])
            }
        
        return relative_performance
    
    def print_analysis_report(self, coefficients: Dict, relative_performance: Dict):
        """Print detailed analysis report"""
        print("\n" + "="*60)
        print("TIRE PERFORMANCE ANALYSIS REPORT")
        print("="*60)
        
        print(f"\nData Source: 2024 Japan GP")
        print(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n📊 RAW DATA SUMMARY:")
        print("-" * 40)
        for compound, data in coefficients.items():
            print(f"{compound:6s}: {data['count']:2d} stints | "
                  f"Avg: {data['avg_lap_time']:6.2f}s | "
                  f"Best: {data['best_lap_time']:6.2f}s | "
                  f"Deg: {data['degradation_rate']:+6.3f}s/lap")
        
        print("\n🏁 RELATIVE PERFORMANCE (vs MEDIUM):")
        print("-" * 50)
        for compound, data in relative_performance.items():
            delta = data['performance_delta']
            sign = "+" if delta >= 0 else ""
            print(f"{compound:6s}: {sign}{delta:6.2f}s/lap | "
                  f"Degradation: {data['degradation_rate']:+6.3f}s/lap | "
                  f"Typical stint: {data['typical_stint_length']:2d} laps")
        
        print("\n🔧 RECOMMENDED SIMULATOR SETTINGS:")
        print("-" * 45)
        medium_baseline = relative_performance.get('MEDIUM', {'performance_delta': 0})['performance_delta']
        
        for compound, data in relative_performance.items():
            # Adjust deltas to make MEDIUM = 0.0
            adjusted_delta = data['performance_delta'] - medium_baseline
            print(f'{compound:6s}: TireCompound("{compound}", {adjusted_delta:6.2f}, '
                  f'{abs(data["degradation_rate"]):5.3f}, {data["typical_stint_length"]:2d})')
    
    def create_visualizations(self, stint_analyses: List[TireStintAnalysis], coefficients: Dict):
        """Create visualization plots"""
        try:
            # Set up the plotting style
            plt.style.use('default')
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('2024 Japan GP - Tire Performance Analysis', fontsize=16, fontweight='bold')
            
            # 1. Average lap time by compound
            compounds = list(coefficients.keys())
            avg_times = [coefficients[c]['avg_lap_time'] for c in compounds]
            colors = {'SOFT': '#ff1e1e', 'MEDIUM': '#ffd700', 'HARD': '#ffffff'}
            bar_colors = [colors.get(c, '#cccccc') for c in compounds]
            
            axes[0,0].bar(compounds, avg_times, color=bar_colors, edgecolor='black', alpha=0.8)
            axes[0,0].set_title('Average Lap Time by Compound')
            axes[0,0].set_ylabel('Lap Time (seconds)')
            axes[0,0].grid(True, alpha=0.3)
            
            # Add value labels on bars
            for i, (compound, time) in enumerate(zip(compounds, avg_times)):
                axes[0,0].text(i, time + 0.1, f'{time:.2f}s', ha='center', fontweight='bold')
            
            # 2. Degradation rate by compound
            deg_rates = [coefficients[c]['degradation_rate'] for c in compounds]
            axes[0,1].bar(compounds, deg_rates, color=bar_colors, edgecolor='black', alpha=0.8)
            axes[0,1].set_title('Tire Degradation Rate')
            axes[0,1].set_ylabel('Degradation (seconds/lap)')
            axes[0,1].grid(True, alpha=0.3)
            
            # Add value labels
            for i, (compound, rate) in enumerate(zip(compounds, deg_rates)):
                axes[0,1].text(i, rate + 0.001, f'{rate:+.3f}', ha='center', fontweight='bold')
            
            # 3. Stint length distribution
            for compound in compounds:
                compound_stints = [s for s in stint_analyses if s.compound == compound]
                stint_lengths = [s.stint_length for s in compound_stints]
                axes[1,0].hist(stint_lengths, alpha=0.6, label=compound, 
                              color=colors.get(compound, '#cccccc'), bins=range(1, 25))
            
            axes[1,0].set_title('Stint Length Distribution')
            axes[1,0].set_xlabel('Stint Length (laps)')
            axes[1,0].set_ylabel('Frequency')
            axes[1,0].legend()
            axes[1,0].grid(True, alpha=0.3)
            
            # 4. Lap time scatter plot
            for compound in compounds:
                compound_stints = [s for s in stint_analyses if s.compound == compound]
                for stint in compound_stints:
                    x = list(range(stint.stint_start, stint.stint_start + len(stint.lap_times)))
                    axes[1,1].scatter(x, stint.lap_times, alpha=0.6, s=20,
                                    color=colors.get(compound, '#cccccc'), label=compound if stint == compound_stints[0] else "")
            
            axes[1,1].set_title('Lap Times Throughout Race')
            axes[1,1].set_xlabel('Lap Number')
            axes[1,1].set_ylabel('Lap Time (seconds)')
            axes[1,1].legend()
            axes[1,1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f'{self.data_dir}/tire_performance_analysis.png', dpi=300, bbox_inches='tight')
            print(f"\n📈 Visualization saved to: {self.data_dir}/tire_performance_analysis.png")
            
        except Exception as e:
            print(f"Warning: Could not create visualizations: {e}")
    
    def export_coefficients(self, relative_performance: Dict, filename: str = None):
        """Export tire coefficients to JSON file"""
        if filename is None:
            filename = f"{self.data_dir}/tire_coefficients.json"
        
        import json
        
        export_data = {
            "generated_at": pd.Timestamp.now().isoformat(),
            "source": "2024 Japan GP Race Data",
            "tire_compounds": {}
        }
        
        # Adjust to make MEDIUM baseline = 0
        medium_baseline = relative_performance.get('MEDIUM', {'performance_delta': 0})['performance_delta']
        
        for compound, data in relative_performance.items():
            adjusted_delta = data['performance_delta'] - medium_baseline
            export_data["tire_compounds"][compound] = {
                "performance_delta": round(adjusted_delta, 3),
                "degradation_rate": round(abs(data['degradation_rate']), 4),
                "typical_stint_length": data['typical_stint_length']
            }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📁 Coefficients exported to: {filename}")
        return export_data

def main():
    """Main analysis function"""
    print("🏁 Starting Tire Performance Analysis...")
    
    analyzer = TirePerformanceAnalyzer()
    
    # Analyze stint performance
    print("🔍 Analyzing tire stint performance...")
    stint_analyses = analyzer.analyze_stint_performance()
    print(f"Analyzed {len(stint_analyses)} tire stints")
    
    # Calculate coefficients
    print("📊 Calculating tire coefficients...")
    coefficients = analyzer.calculate_tire_coefficients(stint_analyses)
    relative_performance = analyzer.calculate_relative_performance(coefficients)
    
    # Generate report
    analyzer.print_analysis_report(coefficients, relative_performance)
    
    # Create visualizations
    print("📈 Creating visualizations...")
    analyzer.create_visualizations(stint_analyses, coefficients)
    
    # Export coefficients
    print("💾 Exporting coefficients...")
    export_data = analyzer.export_coefficients(relative_performance)
    
    print("\n✅ Analysis complete!")
    return coefficients, relative_performance, export_data

if __name__ == "__main__":
    main()
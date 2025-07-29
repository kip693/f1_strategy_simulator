#!/usr/bin/env python3
"""
F1 Lap Time Visualizer
Creates comprehensive visualizations of all drivers' lap times with pit stops and tire compounds
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import json
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class LapTimeVisualizer:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.load_data()
        self.setup_styling()
    
    def load_data(self):
        """Load all necessary race data"""
        try:
            self.drivers_df = pd.read_csv(f"{self.data_dir}/drivers.csv")
            self.lap_times_df = pd.read_csv(f"{self.data_dir}/lap_times.csv")
            self.pit_stops_df = pd.read_csv(f"{self.data_dir}/pit_stops.csv")
            self.stints_df = pd.read_csv(f"{self.data_dir}/stints.csv")
            
            # Clean lap time data
            self.lap_times_df['lap_duration'] = pd.to_numeric(
                self.lap_times_df['lap_duration'], errors='coerce'
            )
            
            # Filter out invalid lap times (< 60s or > 150s for F1)
            self.lap_times_df = self.lap_times_df[
                (self.lap_times_df['lap_duration'] >= 60) & 
                (self.lap_times_df['lap_duration'] <= 150)
            ]
            
            print(f"✅ Loaded data:")
            print(f"  Drivers: {len(self.drivers_df)}")
            print(f"  Valid lap times: {len(self.lap_times_df)}")
            print(f"  Pit stops: {len(self.pit_stops_df)}")
            print(f"  Stints: {len(self.stints_df)}")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
    
    def detect_outliers(self, data: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
        """
        Detect outliers in lap time data
        
        Args:
            data: Lap time data
            method: Method to use ('iqr', 'zscore', 'modified_zscore')
            threshold: Threshold for outlier detection
            
        Returns:
            Boolean series indicating outliers
        """
        if len(data) < 3:
            return pd.Series([False] * len(data), index=data.index)
        
        if method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            return (data < lower_bound) | (data > upper_bound)
        
        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(data))
            return z_scores > threshold
        
        elif method == 'modified_zscore':
            median = data.median()
            mad = np.median(np.abs(data - median))
            modified_z_scores = 0.6745 * (data - median) / mad
            return np.abs(modified_z_scores) > threshold
        
        else:
            raise ValueError(f"Unknown outlier detection method: {method}")
    
    def filter_outliers(self, df: pd.DataFrame, driver_number: int = None, 
                       method: str = 'iqr', threshold: float = 1.5,
                       exclude_pit_laps: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Filter outliers from lap time data
        
        Args:
            df: Lap time dataframe
            driver_number: Specific driver to filter (None for all)
            method: Outlier detection method
            threshold: Outlier threshold
            exclude_pit_laps: Whether to exclude pit laps from analysis
            
        Returns:
            Tuple of (filtered_data, outliers_data)
        """
        if driver_number:
            df = df[df['driver_number'] == driver_number].copy()
        
        # Initially exclude obvious non-racing laps
        base_filter = (df['lap_duration'] >= 60) & (df['lap_duration'] <= 150)
        
        if exclude_pit_laps:
            base_filter = base_filter & (df['is_pit_out_lap'] == False)
        
        clean_data = df[base_filter].copy()
        
        if len(clean_data) == 0:
            return df.iloc[:0].copy(), df.iloc[:0].copy()
        
        # Detect outliers for each driver separately
        outlier_mask = pd.Series([False] * len(clean_data), index=clean_data.index)
        
        if driver_number:
            # Single driver analysis
            outliers = self.detect_outliers(clean_data['lap_duration'], method, threshold)
            outlier_mask = outliers
        else:
            # Multi-driver analysis - detect outliers per driver
            for driver_num in clean_data['driver_number'].unique():
                driver_mask = clean_data['driver_number'] == driver_num
                driver_data = clean_data[driver_mask]['lap_duration']
                
                if len(driver_data) >= 3:
                    driver_outliers = self.detect_outliers(driver_data, method, threshold)
                    outlier_mask.loc[driver_mask] = driver_outliers.values
        
        # Split into clean and outlier data
        filtered_data = clean_data[~outlier_mask].copy()
        outliers_data = clean_data[outlier_mask].copy()
        
        return filtered_data, outliers_data
    
    def get_clean_lap_times(self, driver_number: int = None, 
                           exclude_outliers: bool = True,
                           outlier_method: str = 'iqr',
                           outlier_threshold: float = 1.5) -> pd.DataFrame:
        """
        Get clean lap times with optional outlier removal
        
        Args:
            driver_number: Specific driver (None for all)
            exclude_outliers: Whether to remove outliers
            outlier_method: Method for outlier detection
            outlier_threshold: Threshold for outlier detection
            
        Returns:
            Clean lap time dataframe
        """
        if exclude_outliers:
            filtered_data, _ = self.filter_outliers(
                self.lap_times_df, driver_number, 
                outlier_method, outlier_threshold, 
                exclude_pit_laps=True
            )
            return filtered_data
        else:
            # Return basic filtered data (no outlier removal)
            base_filter = (
                (self.lap_times_df['lap_duration'] >= 60) & 
                (self.lap_times_df['lap_duration'] <= 150) &
                (self.lap_times_df['is_pit_out_lap'] == False)
            )
            
            if driver_number:
                base_filter = base_filter & (self.lap_times_df['driver_number'] == driver_number)
            
            return self.lap_times_df[base_filter].copy()

    def setup_styling(self):
        """Setup color schemes and styling"""
        # F1 team colors (2024 season)
        self.team_colors = {
            'Red Bull Racing': '#3671C6',
            'Ferrari': '#E80020', 
            'McLaren': '#FF8000',
            'Mercedes': '#27F4D2',
            'Aston Martin': '#229971',
            'Alpine': '#0093CC',
            'Williams': '#64C4FF',
            'RB': '#6692FF',
            'Kick Sauber': '#52E252',
            'Haas F1 Team': '#B6BABD',
            'Unknown': '#999999'
        }
        
        # Tire compound colors
        self.tire_colors = {
            'SOFT': '#FF0000',      # Red
            'MEDIUM': '#FFD700',    # Yellow/Gold
            'HARD': '#FFFFFF',      # White
            'INTERMEDIATE': '#00FF00',  # Green
            'WET': '#0000FF'        # Blue
        }
        
        # Setup matplotlib style
        plt.style.use('default')
        sns.set_palette("husl")
    
    def get_driver_info(self, driver_number: int) -> Dict:
        """Get driver information"""
        driver_data = self.drivers_df[self.drivers_df['driver_number'] == driver_number]
        if not driver_data.empty:
            driver = driver_data.iloc[0]
            return {
                'name': driver.get('full_name', driver.get('broadcast_name', f'Driver #{driver_number}')),
                'team': driver.get('team_name', 'Unknown'),
                'abbreviation': driver.get('name_acronym', f'D{driver_number}'),
                'color': self.team_colors.get(driver.get('team_name', 'Unknown'), '#999999')
            }
        return {
            'name': f'Driver #{driver_number}',
            'team': 'Unknown',
            'abbreviation': f'D{driver_number}',
            'color': '#999999'
        }
    
    def create_all_drivers_overview(self, save_path: str = None, exclude_outliers: bool = True) -> plt.Figure:
        """Create overview plot of all drivers' lap times with outlier filtering"""
        print("📊 Creating all drivers overview...")
        if exclude_outliers:
            print("   🧹 Filtering outliers using IQR method...")
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 16))
        
        # Get clean data
        clean_data = self.get_clean_lap_times(exclude_outliers=exclude_outliers)
        
        # Get all unique drivers with sufficient clean data
        driver_counts = clean_data['driver_number'].value_counts()
        active_drivers = driver_counts[driver_counts >= 8].index.tolist()
        
        outlier_counts = {}
        if exclude_outliers:
            # Count outliers for each driver
            for driver_num in active_drivers:
                _, outliers = self.filter_outliers(self.lap_times_df, driver_num)
                outlier_counts[driver_num] = len(outliers)
        
        print(f"Plotting {len(active_drivers)} drivers with sufficient clean data")
        if exclude_outliers:
            total_outliers = sum(outlier_counts.values())
            print(f"   🚫 Excluded {total_outliers} outlier laps")
        
        # Plot 1: Clean lap times only
        for driver_num in active_drivers:
            driver_clean_data = clean_data[clean_data['driver_number'] == driver_num].copy()
            driver_clean_data = driver_clean_data.sort_values('lap_number')
            
            driver_info = self.get_driver_info(driver_num)
            
            ax1.plot(
                driver_clean_data['lap_number'], 
                driver_clean_data['lap_duration'],
                color=driver_info['color'],
                alpha=0.8,
                linewidth=1.5,
                label=f"{driver_info['abbreviation']} ({driver_info['team']})"
            )
        
        ax1.set_xlabel('Lap Number')
        ax1.set_ylabel('Lap Time (seconds)')
        title_suffix = " (Outliers Excluded)" if exclude_outliers else ""
        ax1.set_title(f'2024 Japan GP - All Drivers Lap Times{title_suffix}', 
                     fontsize=16, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        
        # Plot 2: Average lap time comparison with outlier info
        avg_times = []
        driver_names = []
        colors = []
        outlier_info = []
        
        for driver_num in active_drivers:
            driver_clean_data = clean_data[clean_data['driver_number'] == driver_num]
            
            if len(driver_clean_data) > 5:  # Need sufficient data
                avg_time = driver_clean_data['lap_duration'].mean()
                driver_info = self.get_driver_info(driver_num)
                
                avg_times.append(avg_time)
                driver_names.append(driver_info['abbreviation'])
                colors.append(driver_info['color'])
                
                if exclude_outliers:
                    outlier_count = outlier_counts.get(driver_num, 0)
                    total_laps = len(self.lap_times_df[self.lap_times_df['driver_number'] == driver_num])
                    outlier_info.append(f"({outlier_count}/{total_laps})")
                else:
                    outlier_info.append("")
        
        # Sort by average time
        if exclude_outliers:
            sorted_data = sorted(zip(avg_times, driver_names, colors, outlier_info))
            avg_times, driver_names, colors, outlier_info = zip(*sorted_data)
        else:
            sorted_data = sorted(zip(avg_times, driver_names, colors))
            avg_times, driver_names, colors = zip(*sorted_data)
            outlier_info = [""] * len(avg_times)
        
        bars = ax2.barh(driver_names, avg_times, color=colors, alpha=0.8)
        ax2.set_xlabel('Average Lap Time (seconds)')
        title2_suffix = " (Clean Data Only)" if exclude_outliers else ""
        ax2.set_title(f'Average Lap Time Comparison{title2_suffix}', 
                     fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Add time labels on bars
        for i, (bar, time, info) in enumerate(zip(bars, avg_times, outlier_info)):
            width = bar.get_width()
            label = f'{time:.2f}s'
            if exclude_outliers and info:
                label += f' {info}'
            ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                    label, ha='left', va='center', fontsize=8)
        
        # Plot 3: Lap time distribution comparison
        if exclude_outliers:
            for driver_num in active_drivers[:8]:  # Top 8 drivers to avoid clutter
                driver_clean_data = clean_data[clean_data['driver_number'] == driver_num]
                
                if len(driver_clean_data) > 10:
                    driver_info = self.get_driver_info(driver_num)
                    ax3.hist(driver_clean_data['lap_duration'], bins=15, alpha=0.6, 
                           color=driver_info['color'], label=driver_info['abbreviation'],
                           density=True)
            
            ax3.set_xlabel('Lap Time (seconds)')
            ax3.set_ylabel('Density')
            ax3.set_title('Lap Time Distribution (Top 8 Drivers, Clean Data)', 
                         fontsize=14, fontweight='bold')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        else:
            # Show outlier detection example for one driver
            example_driver = active_drivers[0]
            all_data = self.lap_times_df[
                (self.lap_times_df['driver_number'] == example_driver) &
                (self.lap_times_df['lap_duration'] >= 60) & 
                (self.lap_times_df['lap_duration'] <= 150) &
                (self.lap_times_df['is_pit_out_lap'] == False)
            ]
            
            if len(all_data) > 0:
                driver_info = self.get_driver_info(example_driver)
                ax3.hist(all_data['lap_duration'], bins=20, alpha=0.7, 
                        color=driver_info['color'], edgecolor='black')
                ax3.set_xlabel('Lap Time (seconds)')
                ax3.set_ylabel('Frequency')
                ax3.set_title(f'Lap Time Distribution - {driver_info["name"]} (All Data)', 
                             fontsize=14, fontweight='bold')
                ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Saved overview plot to {save_path}")
        
        return fig
    
    def create_driver_detailed_analysis(self, driver_number: int, save_path: str = None, 
                                       exclude_outliers: bool = True) -> plt.Figure:
        """Create detailed analysis for a specific driver with outlier filtering"""
        driver_info = self.get_driver_info(driver_number)
        print(f"📈 Creating detailed analysis for {driver_info['name']}...")
        if exclude_outliers:
            print("   🧹 Filtering outliers using IQR method...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Get driver data (all laps for pit stop visualization)
        driver_laps_all = self.lap_times_df[self.lap_times_df['driver_number'] == driver_number].copy()
        driver_laps_all = driver_laps_all.sort_values('lap_number')
        
        # Get clean data for analysis
        driver_laps_clean = self.get_clean_lap_times(driver_number, exclude_outliers=exclude_outliers)
        driver_laps_clean = driver_laps_clean.sort_values('lap_number')
        
        # Get outliers for visualization
        if exclude_outliers:
            _, driver_outliers = self.filter_outliers(self.lap_times_df, driver_number)
            print(f"   🚫 Excluded {len(driver_outliers)} outlier laps")
        else:
            driver_outliers = pd.DataFrame()
        
        driver_pits = self.pit_stops_df[self.pit_stops_df['driver_number'] == driver_number]
        driver_stints = self.stints_df[self.stints_df['driver_number'] == driver_number]
        
        # Plot 1: Lap times with outlier identification
        ax1 = axes[0, 0]
        
        # Plot clean lap times
        ax1.plot(driver_laps_clean['lap_number'], driver_laps_clean['lap_duration'], 
                color=driver_info['color'], linewidth=2, alpha=0.8, label='Clean Data')
        ax1.scatter(driver_laps_clean['lap_number'], driver_laps_clean['lap_duration'], 
                   color=driver_info['color'], alpha=0.7, s=25)
        
        # Plot outliers if excluded
        if exclude_outliers and not driver_outliers.empty:
            ax1.scatter(driver_outliers['lap_number'], driver_outliers['lap_duration'], 
                       color='red', alpha=0.8, s=40, marker='x', linewidth=2,
                       label=f'Outliers ({len(driver_outliers)})')
        
        # Mark pit stops
        for _, pit in driver_pits.iterrows():
            lap_num = pit['lap_number']
            ax1.axvline(x=lap_num, color='orange', linestyle='--', alpha=0.7, linewidth=2)
            ax1.text(lap_num, ax1.get_ylim()[1] * 0.95, 'PIT', 
                    rotation=90, ha='center', va='top', fontsize=8, 
                    color='orange', fontweight='bold')
        
        ax1.set_xlabel('Lap Number')
        ax1.set_ylabel('Lap Time (seconds)')
        title_suffix = " (Outliers Marked)" if exclude_outliers else ""
        ax1.set_title(f'{driver_info["name"]} - Lap Times{title_suffix}', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        if exclude_outliers and not driver_outliers.empty:
            ax1.legend()
        
        # Plot 2: Tire compound analysis
        ax2 = axes[0, 1]
        
        if not driver_stints.empty:
            stint_compounds = []
            stint_times = []
            stint_lengths = []
            
            for _, stint in driver_stints.iterrows():
                start_lap = stint.get('lap_start', 0)
                end_lap = stint.get('lap_end', start_lap)
                compound = stint.get('compound', 'UNKNOWN')
                
                # Get clean lap times for this stint
                stint_laps = driver_laps_clean[
                    (driver_laps_clean['lap_number'] >= start_lap) & 
                    (driver_laps_clean['lap_number'] <= end_lap)
                ]
                
                if len(stint_laps) > 0:
                    avg_time = stint_laps['lap_duration'].mean()
                    stint_compounds.append(compound)
                    stint_times.append(avg_time)
                    stint_lengths.append(len(stint_laps))
            
            if stint_compounds:
                colors = [self.tire_colors.get(comp, '#999999') for comp in stint_compounds]
                bars = ax2.bar(range(len(stint_compounds)), stint_times, color=colors, alpha=0.8)
                
                ax2.set_xlabel('Stint Number')
                ax2.set_ylabel('Average Lap Time (seconds)')
                ax2.set_title('Performance by Tire Compound', fontweight='bold')
                ax2.set_xticks(range(len(stint_compounds)))
                ax2.set_xticklabels([f'S{i+1}\n{comp}' for i, comp in enumerate(stint_compounds)])
                ax2.grid(True, alpha=0.3, axis='y')
                
                # Add stint length labels
                for bar, length in zip(bars, stint_lengths):
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2, height + 0.1, 
                            f'{length} laps', ha='center', va='bottom', fontsize=8)
        
        # Plot 3: Lap time distribution (clean vs all)
        ax3 = axes[1, 0]
        
        if len(driver_laps_clean) > 0:
            # Plot clean data
            ax3.hist(driver_laps_clean['lap_duration'], bins=15, 
                    color=driver_info['color'], alpha=0.7, edgecolor='black',
                    label=f'Clean Data ({len(driver_laps_clean)} laps)')
            
            # Add statistics for clean data
            mean_clean = driver_laps_clean['lap_duration'].mean()
            median_clean = driver_laps_clean['lap_duration'].median()
            std_clean = driver_laps_clean['lap_duration'].std()
            
            ax3.axvline(mean_clean, color='red', linestyle='--', linewidth=2,
                       label=f'Mean: {mean_clean:.2f}s')
            ax3.axvline(median_clean, color='orange', linestyle='--', linewidth=2,
                       label=f'Median: {median_clean:.2f}s')
            
            # Show outliers if any
            if exclude_outliers and not driver_outliers.empty:
                # Add outliers as separate histogram
                ax3.hist(driver_outliers['lap_duration'], bins=10, 
                        color='red', alpha=0.3, edgecolor='red',
                        label=f'Outliers ({len(driver_outliers)} laps)')
            
            ax3.set_xlabel('Lap Time (seconds)')
            ax3.set_ylabel('Frequency')
            title_dist = "Lap Time Distribution (Clean Data)" if exclude_outliers else "Lap Time Distribution"
            ax3.set_title(title_dist, fontweight='bold')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # Add text box with statistics
            stats_text = f'σ = {std_clean:.2f}s\nRange: {driver_laps_clean["lap_duration"].min():.1f}s - {driver_laps_clean["lap_duration"].max():.1f}s'
            ax3.text(0.02, 0.98, stats_text, transform=ax3.transAxes, 
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # Plot 4: Tire degradation analysis
        ax4 = axes[1, 1]
        
        if not driver_stints.empty:
            for stint_idx, stint in driver_stints.iterrows():
                start_lap = stint.get('lap_start', 0)
                end_lap = stint.get('lap_end', start_lap)
                compound = stint.get('compound', 'UNKNOWN')
                
                stint_laps = driver_laps_clean[
                    (driver_laps_clean['lap_number'] >= start_lap) & 
                    (driver_laps_clean['lap_number'] <= end_lap)
                ]
                
                if len(stint_laps) > 3:  # Need enough data points
                    # Calculate laps on tire
                    stint_laps = stint_laps.copy()
                    stint_laps['laps_on_tire'] = stint_laps['lap_number'] - start_lap + 1
                    
                    color = self.tire_colors.get(compound, '#999999')
                    ax4.scatter(stint_laps['laps_on_tire'], stint_laps['lap_duration'], 
                              color=color, alpha=0.7, label=f'Stint {stint_idx+1} ({compound})')
                    
                    # Fit trend line
                    if len(stint_laps) > 1:
                        z = np.polyfit(stint_laps['laps_on_tire'], stint_laps['lap_duration'], 1)
                        p = np.poly1d(z)
                        ax4.plot(stint_laps['laps_on_tire'], p(stint_laps['laps_on_tire']), 
                                color=color, linestyle='--', alpha=0.8)
        
        ax4.set_xlabel('Laps on Tire')
        ax4.set_ylabel('Lap Time (seconds)')
        ax4.set_title('Tire Degradation Analysis', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle(f'{driver_info["name"]} ({driver_info["team"]}) - Detailed Analysis', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Saved detailed analysis to {save_path}")
        
        return fig
    
    def create_race_evolution_heatmap(self, save_path: str = None) -> plt.Figure:
        """Create a heatmap showing race evolution for all drivers"""
        print("🔥 Creating race evolution heatmap...")
        
        # Prepare data matrix
        drivers = self.lap_times_df['driver_number'].unique()
        max_lap = self.lap_times_df['lap_number'].max()
        
        # Create matrix: drivers x laps
        time_matrix = np.full((len(drivers), max_lap), np.nan)
        driver_names = []
        
        for i, driver_num in enumerate(sorted(drivers)):
            driver_info = self.get_driver_info(driver_num)
            driver_names.append(f"{driver_info['abbreviation']}")
            
            driver_data = self.lap_times_df[self.lap_times_df['driver_number'] == driver_num]
            for _, lap in driver_data.iterrows():
                lap_num = int(lap['lap_number']) - 1  # 0-indexed
                if 0 <= lap_num < max_lap:
                    time_matrix[i, lap_num] = lap['lap_duration']
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(20, 12))
        
        # Use a colormap that highlights differences
        im = ax.imshow(time_matrix, cmap='viridis', aspect='auto', interpolation='nearest')
        
        # Set ticks and labels
        ax.set_xticks(range(0, max_lap, 5))
        ax.set_xticklabels(range(1, max_lap + 1, 5))
        ax.set_yticks(range(len(driver_names)))
        ax.set_yticklabels(driver_names)
        
        ax.set_xlabel('Lap Number')
        ax.set_ylabel('Driver')
        ax.set_title('Race Evolution Heatmap - Lap Times (seconds)', fontsize=16, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Lap Time (seconds)')
        
        # Mark pit stops
        for _, pit in self.pit_stops_df.iterrows():
            driver_idx = list(sorted(drivers)).index(pit['driver_number'])
            lap_idx = pit['lap_number'] - 1
            if 0 <= lap_idx < max_lap:
                ax.scatter(lap_idx, driver_idx, c='red', s=50, marker='s', alpha=0.8)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Saved heatmap to {save_path}")
        
        return fig
    
    def create_comparative_analysis(self, driver_numbers: List[int], save_path: str = None, 
                                  exclude_outliers: bool = True) -> plt.Figure:
        """Create comparative analysis for selected drivers"""
        print(f"⚔️  Creating comparative analysis for {len(driver_numbers)} drivers...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Plot 1: Direct lap time comparison
        ax1 = axes[0, 0]
        
        for driver_num in driver_numbers:
            driver_data = self.get_clean_lap_times(driver_num, exclude_outliers=exclude_outliers)
            driver_data = driver_data.sort_values('lap_number')
            driver_info = self.get_driver_info(driver_num)
            
            ax1.plot(driver_data['lap_number'], driver_data['lap_duration'],
                    color=driver_info['color'], linewidth=2, alpha=0.8,
                    label=f"{driver_info['name']} ({driver_info['abbreviation']})")
        
        ax1.set_xlabel('Lap Number')
        ax1.set_ylabel('Lap Time (seconds)')
        ax1.set_title('Direct Lap Time Comparison', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Performance statistics
        ax2 = axes[0, 1]
        
        stats_data = []
        for driver_num in driver_numbers:
            driver_laps = self.get_clean_lap_times(driver_num, exclude_outliers=exclude_outliers)
            if len(driver_laps) > 0:
                driver_info = self.get_driver_info(driver_num)
                stats_data.append({
                    'driver': driver_info['abbreviation'],
                    'mean': driver_laps['lap_duration'].mean(),
                    'median': driver_laps['lap_duration'].median(),
                    'min': driver_laps['lap_duration'].min(),
                    'std': driver_laps['lap_duration'].std(),
                    'color': driver_info['color']
                })
        
        if stats_data:
            drivers = [d['driver'] for d in stats_data]
            means = [d['mean'] for d in stats_data]
            colors = [d['color'] for d in stats_data]
            
            bars = ax2.bar(drivers, means, color=colors, alpha=0.8)
            ax2.set_ylabel('Average Lap Time (seconds)')
            ax2.set_title('Performance Statistics', fontweight='bold')
            ax2.grid(True, alpha=0.3, axis='y')
            
            # Add value labels
            for bar, mean in zip(bars, means):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2, height + 0.05,
                        f'{mean:.2f}s', ha='center', va='bottom', fontsize=9)
        
        # Plot 3: Stint analysis
        ax3 = axes[1, 0]
        
        stint_data = []
        for driver_num in driver_numbers:
            driver_stints = self.stints_df[self.stints_df['driver_number'] == driver_num]
            driver_info = self.get_driver_info(driver_num)
            
            for _, stint in driver_stints.iterrows():
                start_lap = stint.get('lap_start', 0)
                end_lap = stint.get('lap_end', start_lap)
                compound = stint.get('compound', 'UNKNOWN')
                
                driver_clean_data = self.get_clean_lap_times(driver_num, exclude_outliers=exclude_outliers)
                stint_laps = driver_clean_data[
                    (driver_clean_data['lap_number'] >= start_lap) &
                    (driver_clean_data['lap_number'] <= end_lap)
                ]
                
                if len(stint_laps) > 0:
                    stint_data.append({
                        'driver': driver_info['abbreviation'],
                        'compound': compound,
                        'avg_time': stint_laps['lap_duration'].mean(),
                        'length': len(stint_laps),
                        'color': driver_info['color']
                    })
        
        if stint_data:
            compounds = list(set([d['compound'] for d in stint_data]))
            x_pos = np.arange(len(compounds))
            width = 0.8 / len(driver_numbers)
            
            for i, driver_num in enumerate(driver_numbers):
                driver_info = self.get_driver_info(driver_num)
                driver_stint_data = [d for d in stint_data if d['driver'] == driver_info['abbreviation']]
                
                times = []
                for compound in compounds:
                    compound_data = [d for d in driver_stint_data if d['compound'] == compound]
                    if compound_data:
                        times.append(compound_data[0]['avg_time'])
                    else:
                        times.append(0)
                
                ax3.bar(x_pos + i * width, times, width, label=driver_info['abbreviation'],
                       color=driver_info['color'], alpha=0.8)
            
            ax3.set_xlabel('Tire Compound')
            ax3.set_ylabel('Average Lap Time (seconds)')
            ax3.set_title('Performance by Tire Compound', fontweight='bold')
            ax3.set_xticks(x_pos + width * (len(driver_numbers) - 1) / 2)
            ax3.set_xticklabels(compounds)
            ax3.legend()
            ax3.grid(True, alpha=0.3, axis='y')
        
        # Plot 4: Gap analysis (relative to fastest)
        ax4 = axes[1, 1]
        
        # Find fastest driver for each lap using clean data
        for driver_num in driver_numbers:
            driver_data = self.get_clean_lap_times(driver_num, exclude_outliers=exclude_outliers)
            driver_data = driver_data.sort_values('lap_number')
            driver_info = self.get_driver_info(driver_num)
            
            gaps = []
            laps = []
            
            for _, lap in driver_data.iterrows():
                lap_num = lap['lap_number']
                lap_time = lap['lap_duration']
                
                # Find fastest time for this lap from clean data
                all_clean_data = self.get_clean_lap_times(exclude_outliers=exclude_outliers)
                all_lap_times = all_clean_data[all_clean_data['lap_number'] == lap_num]
                if len(all_lap_times) > 0:
                    fastest_time = all_lap_times['lap_duration'].min()
                    gap = lap_time - fastest_time
                    gaps.append(gap)
                    laps.append(lap_num)
            
            if gaps and laps:
                ax4.plot(laps, gaps, color=driver_info['color'], linewidth=2, alpha=0.8,
                        label=f"{driver_info['abbreviation']}")
        
        ax4.set_xlabel('Lap Number')
        ax4.set_ylabel('Gap to Fastest (seconds)')
        ax4.set_title('Gap Analysis (Relative to Fastest Each Lap)', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        plt.suptitle('Comparative Driver Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Saved comparative analysis to {save_path}")
        
        return fig
    
    def generate_all_visualizations(self, output_dir: str = "visualizations", 
                                  exclude_outliers: bool = True):
        """Generate all visualization types with outlier filtering"""
        import os
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        suffix = "_clean" if exclude_outliers else "_raw"
        print(f"🎨 Generating all visualizations in {output_dir}/ {'(with outlier filtering)' if exclude_outliers else '(raw data)'}")
        
        # 1. All drivers overview
        fig1 = self.create_all_drivers_overview(
            f"{output_dir}/01_all_drivers_overview{suffix}.png", 
            exclude_outliers=exclude_outliers
        )
        plt.close(fig1)
        
        # 2. Race evolution heatmap (using clean data)
        fig2 = self.create_race_evolution_heatmap(
            f"{output_dir}/02_race_evolution_heatmap{suffix}.png"
        )
        plt.close(fig2)
        
        # 3. Detailed analysis for top drivers
        top_drivers = [1, 44, 16, 55, 4]  # Verstappen, Hamilton, Leclerc, Sainz, Norris
        for driver_num in top_drivers:
            try:
                driver_info = self.get_driver_info(driver_num)
                safe_name = driver_info['abbreviation'].replace(' ', '_')
                fig = self.create_driver_detailed_analysis(
                    driver_num, 
                    f"{output_dir}/03_detailed_{safe_name}{suffix}.png",
                    exclude_outliers=exclude_outliers
                )
                plt.close(fig)
            except Exception as e:
                print(f"⚠️  Skipped driver {driver_num}: {e}")
        
        # 4. Comparative analysis
        fig4 = self.create_comparative_analysis(
            top_drivers[:3], 
            f"{output_dir}/04_comparative_top3{suffix}.png",
            exclude_outliers=exclude_outliers
        )
        plt.close(fig4)
        
        print(f"✅ All {'clean' if exclude_outliers else 'raw'} visualizations generated successfully!")
    
    def show_interactive_menu(self):
        """Show interactive menu for visualization selection"""
        while True:
            print("\n" + "="*50)
            print("🏁 F1 Lap Time Visualizer - Interactive Menu")
            print("="*50)
            print("1. All Drivers Overview")
            print("2. Race Evolution Heatmap") 
            print("3. Detailed Driver Analysis")
            print("4. Comparative Analysis")
            print("5. Generate All Visualizations")
            print("6. List Available Drivers")
            print("0. Exit")
            
            choice = input("\nSelect option (0-6): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                fig = self.create_all_drivers_overview()
                plt.show()
            elif choice == '2':
                fig = self.create_race_evolution_heatmap()
                plt.show()
            elif choice == '3':
                self.list_drivers()
                try:
                    driver_num = int(input("Enter driver number: "))
                    fig = self.create_driver_detailed_analysis(driver_num)
                    plt.show()
                except ValueError:
                    print("❌ Invalid driver number")
            elif choice == '4':
                self.list_drivers()
                try:
                    driver_nums_str = input("Enter driver numbers (comma-separated): ")
                    driver_nums = [int(x.strip()) for x in driver_nums_str.split(',')]
                    fig = self.create_comparative_analysis(driver_nums)
                    plt.show()
                except ValueError:
                    print("❌ Invalid driver numbers")
            elif choice == '5':
                self.generate_all_visualizations()
            elif choice == '6':
                self.list_drivers()
            else:
                print("❌ Invalid option")
    
    def list_drivers(self):
        """List all available drivers"""
        print("\n📋 Available Drivers:")
        print("="*40)
        
        # Get drivers with lap time data
        driver_counts = self.lap_times_df['driver_number'].value_counts()
        
        for driver_num in sorted(driver_counts.index):
            driver_info = self.get_driver_info(driver_num)
            lap_count = driver_counts[driver_num]
            print(f"{driver_num:2d}. {driver_info['name']:25} ({driver_info['team']:15}) - {lap_count:2d} laps")

def main():
    """Main function"""
    print("🏁 F1 Lap Time Visualizer")
    print("=" * 50)
    
    try:
        visualizer = LapTimeVisualizer()
        
        # Check if running interactively
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == '--generate-all':
            visualizer.generate_all_visualizations()
        else:
            visualizer.show_interactive_menu()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
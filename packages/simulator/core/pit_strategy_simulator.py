#!/usr/bin/env python3
"""
F1 Pit Strategy Simulator
Simulates alternative pit strategies based on real race data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from dataclasses import dataclass
from copy import deepcopy
from .dynamic_pit_loss_calculator import DynamicPitLossCalculator

@dataclass
class TireCompound:
    name: str
    performance_delta: float  # seconds per lap vs medium compound
    degradation_rate: float   # additional seconds per lap due to wear
    max_stint_length: int     # typical maximum stint length

@dataclass
class PitStop:
    lap: int
    tire_compound: str
    pit_loss: float = 22.0  # typical pit stop time loss in seconds

@dataclass
class DriverStrategy:
    driver_number: int
    pit_stops: List[PitStop]

class F1StrategySimulator:
    def __init__(self, data_dir: str = "data", use_dynamic_pit_loss: bool = True):
        self.data_dir = data_dir
        self.use_dynamic_pit_loss = use_dynamic_pit_loss
        self.load_tire_coefficients()
        self.load_race_data()
        
        # Initialize dynamic pit loss calculator
        if self.use_dynamic_pit_loss:
            try:
                self.pit_loss_calculator = DynamicPitLossCalculator(data_dir)
                print("✅ Dynamic pit loss calculator loaded")
            except Exception as e:
                print(f"⚠️  Failed to load dynamic pit loss calculator: {e}")
                print("   Falling back to static pit loss times")
                self.use_dynamic_pit_loss = False
                self.pit_loss_calculator = None
        else:
            self.pit_loss_calculator = None
    
    def load_tire_coefficients(self):
        """Load data-driven tire coefficients from analysis"""
        try:
            with open(f"{self.data_dir}/tire_coefficients.json", 'r') as f:
                coeffs_data = json.load(f)
            
            tire_data = coeffs_data["tire_compounds"]
            
            self.tire_compounds = {
                "SOFT": TireCompound(
                    "SOFT", 
                    tire_data["SOFT"]["performance_delta"],
                    tire_data["SOFT"]["degradation_rate"], 
                    tire_data["SOFT"]["typical_stint_length"]
                ),
                "MEDIUM": TireCompound(
                    "MEDIUM", 
                    tire_data["MEDIUM"]["performance_delta"],
                    tire_data["MEDIUM"]["degradation_rate"], 
                    tire_data["MEDIUM"]["typical_stint_length"]
                ),
                "HARD": TireCompound(
                    "HARD", 
                    tire_data["HARD"]["performance_delta"],
                    tire_data["HARD"]["degradation_rate"], 
                    tire_data["HARD"]["typical_stint_length"]
                )
            }
            
            print(f"✅ Loaded data-driven tire coefficients from {coeffs_data['source']}")
            for compound, tire in self.tire_compounds.items():
                print(f"   {compound}: {tire.performance_delta:+.3f}s/lap, degradation: {tire.degradation_rate:.3f}s/lap")
            
        except FileNotFoundError:
            print("⚠️  Tire coefficients file not found, using fallback values")
            self.tire_compounds = {
                "SOFT": TireCompound("SOFT", -0.6, 0.08, 25),
                "MEDIUM": TireCompound("MEDIUM", 0.0, 0.05, 35), 
                "HARD": TireCompound("HARD", 0.5, 0.03, 45)
            }
        except Exception as e:
            print(f"⚠️  Error loading tire coefficients: {e}, using fallback values")
            self.tire_compounds = {
                "SOFT": TireCompound("SOFT", -0.6, 0.08, 25),
                "MEDIUM": TireCompound("MEDIUM", 0.0, 0.05, 35), 
                "HARD": TireCompound("HARD", 0.5, 0.03, 45)
            }
    
    def load_race_data(self):
        """Load all race data from CSV files"""
        try:
            self.drivers_df = pd.read_csv(f"{self.data_dir}/drivers.csv")
            self.lap_times_df = pd.read_csv(f"{self.data_dir}/lap_times.csv")
            self.pit_stops_df = pd.read_csv(f"{self.data_dir}/pit_stops.csv")
            self.stints_df = pd.read_csv(f"{self.data_dir}/stints.csv")
            self.positions_df = pd.read_csv(f"{self.data_dir}/positions.csv")
            
            # Convert lap_duration to numeric (handle missing values)
            self.lap_times_df['lap_duration'] = pd.to_numeric(
                self.lap_times_df['lap_duration'], errors='coerce'
            )
            
            print(f"Loaded data for {len(self.drivers_df)} drivers")
            print(f"Race length: {self.lap_times_df['lap_number'].max()} laps")
            
        except Exception as e:
            print(f"Error loading race data: {e}")
            raise
    
    def get_baseline_lap_times(self, driver_number: int) -> Dict[int, float]:
        """Get baseline lap times for a driver (excluding pit laps)"""
        driver_laps = self.lap_times_df[
            (self.lap_times_df['driver_number'] == driver_number) &
            (self.lap_times_df['is_pit_out_lap'] == False) &
            (self.lap_times_df['lap_duration'].notna())
        ].copy()
        
        baseline_times = {}
        for _, lap in driver_laps.iterrows():
            baseline_times[int(lap['lap_number'])] = float(lap['lap_duration'])
        
        return baseline_times
    
    def get_actual_strategy(self, driver_number: int) -> List[PitStop]:
        """Extract actual pit strategy from race data"""
        driver_pits = self.pit_stops_df[
            self.pit_stops_df['driver_number'] == driver_number
        ].copy()
        
        # Get stint data for tire compounds
        driver_stints = self.stints_df[
            (self.stints_df['driver_number'] == driver_number) &
            (self.stints_df['lap_start'].notna())
        ].copy()
        
        pit_stops = []
        for _, pit in driver_pits.iterrows():
            # Find corresponding stint for tire compound
            stint = driver_stints[
                driver_stints['lap_start'] <= pit['lap_number']
            ].tail(1)
            
            compound = stint['compound'].iloc[0] if not stint.empty else "MEDIUM"
            pit_stops.append(PitStop(
                lap=int(pit['lap_number']),
                tire_compound=compound,
                pit_loss=pit['pit_duration'] / 1000.0 if 'pit_duration' in pit else 22.0
            ))
        
        return sorted(pit_stops, key=lambda x: x.lap)
    
    def calculate_tire_performance(self, compound: str, stint_lap: int, total_laps_on_tire: int) -> float:
        """Calculate tire performance delta based on compound and wear"""
        if compound not in self.tire_compounds:
            compound = "MEDIUM"  # default fallback
        
        tire = self.tire_compounds[compound]
        
        # Base performance delta
        performance = tire.performance_delta
        
        # Add degradation based on laps on tire
        degradation = tire.degradation_rate * total_laps_on_tire
        
        return performance + degradation
    
    def calculate_dynamic_pit_loss(self, driver_number: int, lap_number: int, 
                                  conditions: Optional[Dict] = None) -> float:
        """Calculate dynamic pit loss time"""
        if self.use_dynamic_pit_loss and self.pit_loss_calculator:
            try:
                pit_loss, _ = self.pit_loss_calculator.calculate_pit_loss(
                    driver_number, lap_number, conditions
                )
                return pit_loss
            except Exception as e:
                print(f"⚠️  Dynamic pit loss calculation failed: {e}, using default")
                return 22.0
        else:
            return 22.0
    
    def simulate_strategy(self, driver_number: int, new_strategy: List[PitStop]) -> Dict:
        """Simulate a new pit strategy for a driver"""
        baseline_times = self.get_baseline_lap_times(driver_number)
        race_length = max(baseline_times.keys()) if baseline_times else 53
        
        # Initialize simulation
        simulated_times = {}
        current_tire = "MEDIUM"  # Starting tire (assumption)
        laps_on_tire = 0
        total_time = 0.0
        
        pit_laps = {pit.lap for pit in new_strategy}
        pit_dict = {pit.lap: pit for pit in new_strategy}
        
        for lap in range(1, race_length + 1):
            # Check if this is a pit lap
            if lap in pit_laps:
                pit_stop = pit_dict[lap]
                # Calculate dynamic pit loss time
                if self.use_dynamic_pit_loss:
                    dynamic_pit_loss = self.calculate_dynamic_pit_loss(driver_number, lap)
                    total_time += dynamic_pit_loss
                else:
                    total_time += pit_stop.pit_loss
                # Change tire
                current_tire = pit_stop.tire_compound
                laps_on_tire = 0
            
            # Get baseline lap time
            if lap in baseline_times:
                base_time = baseline_times[lap]
            else:
                # Estimate missing lap time based on average
                avg_time = np.mean(list(baseline_times.values())) if baseline_times else 90.0
                base_time = avg_time
            
            # Apply tire performance delta
            tire_delta = self.calculate_tire_performance(current_tire, lap, laps_on_tire)
            simulated_time = base_time + tire_delta
            
            simulated_times[lap] = simulated_time
            total_time += simulated_time
            laps_on_tire += 1
        
        return {
            "driver_number": driver_number,
            "strategy": new_strategy,
            "lap_times": simulated_times,
            "total_time": total_time,
            "simulated": True
        }
    
    def compare_strategies(self, driver_number: int, alternative_strategy: List[PitStop]) -> Dict:
        """Compare alternative strategy with actual race result"""
        # Get actual strategy and simulate it
        actual_strategy = self.get_actual_strategy(driver_number)
        
        # Handle pit loss times based on dynamic calculation setting
        if self.use_dynamic_pit_loss:
            # Use dynamic pit loss calculation for both strategies
            normalized_actual = actual_strategy
            normalized_alternative = alternative_strategy
        else:
            # Normalize pit loss times for fair comparison
            # Use standard 22.0s pit loss for both strategies to avoid data inconsistencies
            normalized_actual = []
            for pit in actual_strategy:
                normalized_actual.append(PitStop(
                    lap=pit.lap,
                    tire_compound=pit.tire_compound,
                    pit_loss=22.0  # Use standard pit loss time
                ))
            
            normalized_alternative = []
            for pit in alternative_strategy:
                normalized_alternative.append(PitStop(
                    lap=pit.lap,
                    tire_compound=pit.tire_compound,
                    pit_loss=22.0  # Use standard pit loss time
                ))
        
        actual_simulation = self.simulate_strategy(driver_number, normalized_actual)
        alt_simulation = self.simulate_strategy(driver_number, normalized_alternative)
        
        # Calculate time difference
        time_diff = alt_simulation["total_time"] - actual_simulation["total_time"]
        
        # Calculate stint-by-stint comparison
        stint_comparison = self.calculate_stint_comparison(
            driver_number, normalized_actual, normalized_alternative,
            actual_simulation["lap_times"], alt_simulation["lap_times"]
        )

        return {
            "driver_number": driver_number,
            "actual_strategy": actual_strategy,
            "alternative_strategy": alternative_strategy,
            "actual_total_time": actual_simulation["total_time"],
            "alternative_total_time": alt_simulation["total_time"],
            "time_difference": time_diff,
            "improvement": time_diff < 0,
            "actual_lap_times": actual_simulation["lap_times"],
            "alternative_lap_times": alt_simulation["lap_times"],
            "stint_comparison": stint_comparison
        }
    
    def calculate_stint_comparison(self, driver_number: int, actual_strategy: List[PitStop], 
                                 alternative_strategy: List[PitStop], 
                                 actual_lap_times: Dict[int, float], 
                                 alt_lap_times: Dict[int, float]) -> List[Dict]:
        """Calculate stint-by-stint performance comparison"""
        
        def create_stints(strategy: List[PitStop], race_length: int = 53) -> List[Dict]:
            stints = []
            
            # Add initial stint (before first pit stop)
            if strategy:
                first_pit = min(pit.lap for pit in strategy)
                if first_pit > 1:
                    stints.append({
                        "stint_number": 1,
                        "start_lap": 1,
                        "end_lap": first_pit - 1,
                        "tire_compound": "MEDIUM",  # Starting tire assumption
                        "stint_length": first_pit - 1
                    })
            
            # Add stints between pit stops
            sorted_pits = sorted(strategy, key=lambda x: x.lap)
            for i, pit in enumerate(sorted_pits):
                start_lap = pit.lap
                
                if i < len(sorted_pits) - 1:
                    # Not the last pit stop
                    end_lap = sorted_pits[i + 1].lap - 1
                else:
                    # Last pit stop - goes to end of race
                    end_lap = race_length
                
                stints.append({
                    "stint_number": i + 2,  # +2 because we might have initial stint
                    "start_lap": start_lap,
                    "end_lap": end_lap,
                    "tire_compound": pit.tire_compound,
                    "stint_length": end_lap - start_lap + 1
                })
            
            # Handle case with no pit stops
            if not strategy:
                stints.append({
                    "stint_number": 1,
                    "start_lap": 1,
                    "end_lap": race_length,
                    "tire_compound": "MEDIUM",
                    "stint_length": race_length
                })
            
            return stints
        
        def calculate_stint_time(stint: Dict, lap_times: Dict[int, float]) -> float:
            total_time = 0.0
            for lap in range(stint["start_lap"], stint["end_lap"] + 1):
                if lap in lap_times:
                    total_time += lap_times[lap]
            return total_time
        
        # Create stints for both strategies
        actual_stints = create_stints(actual_strategy)
        alt_stints = create_stints(alternative_strategy)
        
        # Compare stints
        comparison = []
        max_stints = max(len(actual_stints), len(alt_stints))
        
        for i in range(max_stints):
            actual_stint = actual_stints[i] if i < len(actual_stints) else None
            alt_stint = alt_stints[i] if i < len(alt_stints) else None
            
            stint_data = {
                "stint_number": i + 1,
                "actual_stint": actual_stint,
                "alternative_stint": alt_stint,
                "actual_time": 0.0,
                "alternative_time": 0.0,
                "time_difference": 0.0
            }
            
            if actual_stint:
                stint_data["actual_time"] = calculate_stint_time(actual_stint, actual_lap_times)
            
            if alt_stint:
                stint_data["alternative_time"] = calculate_stint_time(alt_stint, alt_lap_times)
            
            stint_data["time_difference"] = stint_data["alternative_time"] - stint_data["actual_time"]
            
            comparison.append(stint_data)
        
        return comparison
    
    def analyze_field_impact(self, strategies: Dict[int, List[PitStop]]) -> Dict:
        """Analyze how multiple strategy changes affect the field"""
        results = {}
        
        for driver_number, strategy in strategies.items():
            if driver_number in self.drivers_df['driver_number'].values:
                results[driver_number] = self.compare_strategies(driver_number, strategy)
        
        # Sort by final time to get predicted finishing order
        sorted_results = sorted(
            results.items(), 
            key=lambda x: x[1]["alternative_total_time"]
        )
        
        # Add predicted positions
        for i, (driver_num, result) in enumerate(sorted_results):
            results[driver_num]["predicted_position"] = i + 1
        
        return results

def demo_simulation():
    """Demo simulation with example strategies"""
    simulator = F1StrategySimulator()
    
    # Example: What if Verstappen (driver 1) had pitted on lap 15 and 35 instead?
    verstappen_alt_strategy = [
        PitStop(lap=15, tire_compound="SOFT"),
        PitStop(lap=35, tire_compound="MEDIUM")
    ]
    
    print("=== F1 STRATEGY SIMULATION DEMO ===")
    print("\nAnalyzing alternative strategy for Verstappen...")
    
    comparison = simulator.compare_strategies(1, verstappen_alt_strategy)
    
    print(f"\nActual strategy:")
    for pit in comparison["actual_strategy"]:
        print(f"  Lap {pit.lap}: {pit.tire_compound}")
    
    print(f"\nAlternative strategy:")
    for pit in comparison["alternative_strategy"]:
        print(f"  Lap {pit.lap}: {pit.tire_compound}")
    
    print(f"\nResults:")
    print(f"  Actual total time: {comparison['actual_total_time']:.1f}s")
    print(f"  Alternative total time: {comparison['alternative_total_time']:.1f}s")
    print(f"  Time difference: {comparison['time_difference']:.1f}s")
    
    if comparison["improvement"]:
        print(f"  ✅ Alternative strategy is {abs(comparison['time_difference']):.1f}s faster!")
    else:
        print(f"  ❌ Alternative strategy is {comparison['time_difference']:.1f}s slower")
    
    return comparison

if __name__ == "__main__":
    try:
        result = demo_simulation()
    except Exception as e:
        print(f"Error running simulation: {e}")
        import traceback
        traceback.print_exc()
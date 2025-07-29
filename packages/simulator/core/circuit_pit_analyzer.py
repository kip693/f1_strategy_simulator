#!/usr/bin/env python3
"""
Circuit-Specific Pit Loss Analyzer
Analyzes circuit characteristics and calculates realistic pit times based on track layout
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class CircuitCharacteristics:
    name: str
    pit_lane_length: float  # meters
    pit_speed_limit: int    # km/h
    pit_entry_complexity: float  # 1.0 = simple, 2.0 = complex
    pit_exit_complexity: float   # 1.0 = simple, 2.0 = complex
    track_position_loss: float   # seconds lost due to track position
    
class CircuitPitAnalyzer:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.load_data()
        self.define_circuit_characteristics()
    
    def load_data(self):
        """Load race data for analysis"""
        try:
            self.lap_times_df = pd.read_csv(f"{self.data_dir}/lap_times.csv")
            self.pit_stops_df = pd.read_csv(f"{self.data_dir}/pit_stops.csv")
            self.sessions_df = pd.read_csv(f"{self.data_dir}/sessions.csv")
            print(f"Loaded race data: {len(self.lap_times_df)} lap times, {len(self.pit_stops_df)} pit stops")
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def define_circuit_characteristics(self):
        """Define characteristics for various F1 circuits"""
        self.circuits = {
            "suzuka": CircuitCharacteristics(
                name="Suzuka International Racing Course",
                pit_lane_length=310,     # meters
                pit_speed_limit=80,      # km/h (typical for Suzuka)
                pit_entry_complexity=1.3,  # Moderate complexity after 130R
                pit_exit_complexity=1.1,   # Relatively simple exit
                track_position_loss=18.0   # seconds lost for full pit lane traverse
            ),
            "monaco": CircuitCharacteristics(
                name="Circuit de Monaco",
                pit_lane_length=350,
                pit_speed_limit=60,
                pit_entry_complexity=1.8,  # Very tight entry
                pit_exit_complexity=2.0,   # Complex exit onto main straight
                track_position_loss=22.5
            ),
            "silverstone": CircuitCharacteristics(
                name="Silverstone Circuit",
                pit_lane_length=415,
                pit_speed_limit=80,
                pit_entry_complexity=1.0,  # Simple entry
                pit_exit_complexity=1.2,   # Moderate exit
                track_position_loss=19.5
            ),
            "monza": CircuitCharacteristics(
                name="Autodromo Nazionale Monza",
                pit_lane_length=385,
                pit_speed_limit=80,
                pit_entry_complexity=1.1,  # Simple layout
                pit_exit_complexity=1.0,   # Very simple exit
                track_position_loss=16.5   # One of the shortest pit losses
            ),
            "spa": CircuitCharacteristics(
                name="Circuit de Spa-Francorchamps",
                pit_lane_length=425,
                pit_speed_limit=80,
                pit_entry_complexity=1.2,
                pit_exit_complexity=1.4,   # Uphill exit can be tricky
                track_position_loss=21.0
            )
        }
        
        # Default to Suzuka for current analysis
        self.current_circuit = self.circuits["suzuka"]
        print(f"Circuit: {self.current_circuit.name}")
        print(f"  Pit lane length: {self.current_circuit.pit_lane_length}m")
        print(f"  Speed limit: {self.current_circuit.pit_speed_limit}km/h")
        print(f"  Track position loss: {self.current_circuit.track_position_loss}s")
    
    def calculate_theoretical_pit_time(self, circuit: CircuitCharacteristics) -> Dict:
        """Calculate theoretical minimum pit time based on circuit characteristics"""
        
        # Convert speed limit to m/s
        speed_limit_ms = (circuit.pit_speed_limit * 1000) / 3600
        
        # Basic time to traverse pit lane at speed limit
        traverse_time = circuit.pit_lane_length / speed_limit_ms
        
        # Add time for pit entry/exit complexity
        entry_penalty = (circuit.pit_entry_complexity - 1.0) * 2.0  # 2s per complexity unit
        exit_penalty = (circuit.pit_exit_complexity - 1.0) * 2.0
        
        # Actual pit stop work time (tire change, etc.)
        pit_work_time = 2.3  # Modern F1 pit stop work time
        
        # Total time calculation
        total_time = traverse_time + entry_penalty + exit_penalty + pit_work_time
        
        return {
            "traverse_time": traverse_time,
            "entry_penalty": entry_penalty,
            "exit_penalty": exit_penalty,
            "pit_work_time": pit_work_time,
            "total_pit_lane_time": total_time,
            "track_position_loss": circuit.track_position_loss,
            "total_pit_loss": total_time + circuit.track_position_loss
        }
    
    def analyze_actual_pit_times(self):
        """Analyze actual pit times from race data"""
        print("\n=== ANALYZING ACTUAL PIT TIMES ===")
        
        # Analyze lap times around pit stops to estimate real pit loss
        pit_loss_estimates = []
        
        for _, pit_stop in self.pit_stops_df.iterrows():
            driver = pit_stop['driver_number']
            pit_lap = pit_stop['lap_number']
            
            # Get lap times before, during, and after pit stop
            driver_laps = self.lap_times_df[
                (self.lap_times_df['driver_number'] == driver) &
                (self.lap_times_df['lap_number'].between(pit_lap - 2, pit_lap + 2)) &
                (self.lap_times_df['lap_duration'].notna())
            ].sort_values('lap_number')
            
            if len(driver_laps) >= 3:
                # Find reference lap time (non-pit laps)
                ref_laps = driver_laps[driver_laps['lap_number'] != pit_lap]
                if len(ref_laps) > 0:
                    avg_lap_time = ref_laps['lap_duration'].mean()
                    
                    # Find pit lap time
                    pit_lap_data = driver_laps[driver_laps['lap_number'] == pit_lap]
                    if not pit_lap_data.empty:
                        pit_lap_time = pit_lap_data['lap_duration'].iloc[0]
                        estimated_pit_loss = pit_lap_time - avg_lap_time
                        
                        # Only include reasonable estimates (10-40 seconds)
                        if 10 <= estimated_pit_loss <= 40:
                            pit_loss_estimates.append({
                                'driver_number': driver,
                                'lap_number': pit_lap,
                                'pit_loss': estimated_pit_loss,
                                'pit_lap_time': pit_lap_time,
                                'avg_lap_time': avg_lap_time
                            })
        
        if pit_loss_estimates:
            pit_loss_df = pd.DataFrame(pit_loss_estimates)
            
            print(f"Analyzed {len(pit_loss_df)} pit stops with valid data")
            print(f"Average pit loss: {pit_loss_df['pit_loss'].mean():.2f}s")
            print(f"Median pit loss: {pit_loss_df['pit_loss'].median():.2f}s")
            print(f"Standard deviation: {pit_loss_df['pit_loss'].std():.2f}s")
            print(f"Range: {pit_loss_df['pit_loss'].min():.1f}s - {pit_loss_df['pit_loss'].max():.1f}s")
            
            # Analyze by driver (team differences)
            driver_analysis = pit_loss_df.groupby('driver_number')['pit_loss'].agg(['mean', 'count']).round(2)
            driver_analysis = driver_analysis[driver_analysis['count'] >= 2]  # Drivers with multiple stops
            
            print(f"\nPit loss by driver (drivers with 2+ stops):")
            print("Driver | Avg Loss | Count")
            print("-------|----------|------")
            for driver, stats in driver_analysis.iterrows():
                print(f"   {driver:2d}  |  {stats['mean']:6.1f}s |   {stats['count']:2.0f}")
            
            return pit_loss_df, driver_analysis
        else:
            print("No valid pit loss data found")
            return None, None
    
    def create_enhanced_pit_loss_model(self):
        """Create enhanced pit loss model incorporating circuit characteristics"""
        print("\n=== CREATING ENHANCED PIT LOSS MODEL ===")
        
        # Analyze actual data
        pit_data, driver_stats = self.analyze_actual_pit_times()
        
        # Calculate theoretical times for different circuits
        circuit_calculations = {}
        for circuit_name, circuit in self.circuits.items():
            circuit_calculations[circuit_name] = self.calculate_theoretical_pit_time(circuit)
        
        # Create enhanced model
        model = {
            "version": "3.0",
            "description": "Enhanced dynamic pit loss with circuit characteristics and actual data analysis",
            
            # Circuit-specific data
            "circuits": {
                name: {
                    "name": circuit.name,
                    "pit_lane_length": circuit.pit_lane_length,
                    "pit_speed_limit": circuit.pit_speed_limit,
                    "pit_entry_complexity": circuit.pit_entry_complexity,
                    "pit_exit_complexity": circuit.pit_exit_complexity,
                    "track_position_loss": circuit.track_position_loss,
                    "theoretical_calculation": circuit_calculations[name]
                }
                for name, circuit in self.circuits.items()
            },
            
            # Current circuit (Suzuka for Japan GP)
            "current_circuit": "suzuka",
            
            # Data-driven baseline from actual analysis
            "data_analysis": {},
            
            # Base pit loss for compatibility
            "base_pit_loss": 35.0,  # Suzuka theoretical baseline
            
            # Lap-based factors (traffic and race conditions)
            "lap_factors": {
                "early_race": {
                    "laps": [1, 15],
                    "factor": 1.1,   # Slightly higher due to formation and early traffic
                    "description": "Early race with formation and initial traffic"
                },
                "mid_race": {
                    "laps": [16, 35],
                    "factor": 1.0,   # Normal conditions
                    "description": "Normal racing conditions"
                },
                "late_race": {
                    "laps": [36, 60],
                    "factor": 0.95,  # Less traffic, more desperate pit stops
                    "description": "Late race with reduced traffic"
                }
            },
            
            # Enhanced team factors based on actual performance
            "team_factors": {
                "top_teams": {
                    "drivers": [1, 11, 16, 55, 44, 63],  # Red Bull, Ferrari, Mercedes
                    "factor": 0.88,  # Faster than baseline
                    "description": "Elite pit crews with fastest equipment"
                },
                "midfield_teams": {
                    "drivers": [4, 81, 14, 18, 10, 27],  # McLaren, Alpine, etc.
                    "factor": 1.0,   # Baseline
                    "description": "Standard F1 pit crews"
                },
                "back_teams": {
                    "drivers": [77, 20, 24, 22, 2, 31],  # Smaller teams
                    "factor": 1.12,  # Slower than baseline
                    "description": "Developing teams with limited resources"
                }
            },
            
            # Situational factors
            "situation_factors": {
                "safety_car": {
                    "factor": 1.2,
                    "description": "Pit lane congestion during safety car"
                },
                "rain": {
                    "factor": 1.15,
                    "description": "Slower operations in wet conditions"
                },
                "damaged_car": {
                    "factor": 1.25,
                    "description": "Additional time for damage assessment"
                }
            },
            
            # Random variation (realistic spread)
            "random_variation": {
                "std_dev": 1.0,
                "min_factor": 0.9,
                "max_factor": 1.15,
                "description": "Natural variation in pit stop execution"
            },
            
            # Circuit-specific adjustments
            "circuit_factors": {
                "pit_lane_traffic": {
                    "low": 0.95,      # Clean pit lane
                    "medium": 1.0,    # Normal traffic
                    "high": 1.15      # Congested pit lane
                },
                "weather_impact": {
                    "dry": 1.0,
                    "damp": 1.08,
                    "wet": 1.18       # Slower operations in wet
                }
            }
        }
        
        # Add actual data analysis if available
        if pit_data is not None:
            model["data_analysis"] = {
                "sample_size": len(pit_data),
                "mean_pit_loss": float(pit_data['pit_loss'].mean()),
                "median_pit_loss": float(pit_data['pit_loss'].median()),
                "std_deviation": float(pit_data['pit_loss'].std()),
                "min_pit_loss": float(pit_data['pit_loss'].min()),
                "max_pit_loss": float(pit_data['pit_loss'].max())
            }
            
            # Update baseline to match circuit data
            suzuka_theoretical = circuit_calculations["suzuka"]["total_pit_loss"]
            actual_median = pit_data['pit_loss'].median()
            
            # Calibrate theoretical model to actual data
            calibration_factor = actual_median / suzuka_theoretical if suzuka_theoretical > 0 else 1.0
            model["calibration_factor"] = float(calibration_factor)
            
            print(f"Theoretical Suzuka pit loss: {suzuka_theoretical:.1f}s")
            print(f"Actual median pit loss: {actual_median:.1f}s")
            print(f"Calibration factor: {calibration_factor:.3f}")
        
        # Save enhanced model
        with open(f"{self.data_dir}/enhanced_pit_loss_model.json", 'w') as f:
            json.dump(model, f, indent=2)
        
        print(f"Enhanced pit loss model saved to {self.data_dir}/enhanced_pit_loss_model.json")
        return model
    
    def compare_circuits(self):
        """Compare pit loss characteristics across different circuits"""
        print("\n=== CIRCUIT COMPARISON ===")
        
        print("Circuit               | Pit Lane | Speed | Entry | Exit  | Position | Total")
        print("                      | Length   | Limit | Cmplx | Cmplx | Loss     | Loss ")
        print("----------------------|----------|-------|-------|-------|----------|-------")
        
        for name, circuit in self.circuits.items():
            calc = self.calculate_theoretical_pit_time(circuit)
            print(f"{circuit.name:20} | {circuit.pit_lane_length:6.0f}m | {circuit.pit_speed_limit:4d}kmh | {circuit.pit_entry_complexity:5.1f} | {circuit.pit_exit_complexity:5.1f} | {circuit.track_position_loss:6.1f}s | {calc['total_pit_loss']:5.1f}s")
    
    def analyze_traffic_patterns(self):
        """Analyze pit lane traffic patterns throughout the race"""
        print("\n=== PIT LANE TRAFFIC ANALYSIS ===")
        
        # Group pit stops by lap to identify busy periods
        pit_traffic = self.pit_stops_df.groupby('lap_number').size().reset_index(name='pit_count')
        pit_traffic = pit_traffic[pit_traffic['lap_number'] > 5]  # Exclude formation lap issues
        
        if len(pit_traffic) > 0:
            print(f"Total pit stops analyzed: {pit_traffic['pit_count'].sum()}")
            print(f"Average pit stops per lap: {pit_traffic['pit_count'].mean():.1f}")
            print(f"Maximum pit stops in one lap: {pit_traffic['pit_count'].max()}")
            
            # Identify busy pit windows
            busy_laps = pit_traffic[pit_traffic['pit_count'] >= 3]
            if len(busy_laps) > 0:
                print(f"\nBusy pit laps (3+ cars):")
                for _, lap_data in busy_laps.iterrows():
                    print(f"  Lap {lap_data['lap_number']:2d}: {lap_data['pit_count']} cars")
            
            return pit_traffic
        
        return None

def main():
    """Main analysis function"""
    print("🏁 Circuit-Specific Pit Loss Analysis")
    print("=" * 60)
    
    analyzer = CircuitPitAnalyzer()
    
    # 1. Analyze actual pit times
    pit_data, driver_stats = analyzer.analyze_actual_pit_times()
    
    # 2. Compare circuit characteristics
    analyzer.compare_circuits()
    
    # 3. Analyze traffic patterns
    analyzer.analyze_traffic_patterns()
    
    # 4. Create enhanced model
    model = analyzer.create_enhanced_pit_loss_model()
    
    print(f"\n✅ Enhanced circuit-aware pit loss model created!")
    print(f"📊 Current circuit: {model['circuits']['suzuka']['name']}")
    print(f"🏎️  Theoretical pit loss: {model['circuits']['suzuka']['theoretical_calculation']['total_pit_loss']:.1f}s")
    
    if 'data_analysis' in model and model['data_analysis']:
        print(f"📈 Actual median pit loss: {model['data_analysis']['median_pit_loss']:.1f}s")
        print(f"🔧 Calibration factor: {model.get('calibration_factor', 1.0):.3f}")

if __name__ == "__main__":
    main()
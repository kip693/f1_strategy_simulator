#!/usr/bin/env python3
"""
F1 Strategy Analyzer
Advanced analysis tools for pit strategy optimization
"""

import pandas as pd
import numpy as np
from .pit_strategy_simulator import F1StrategySimulator, PitStop, DriverStrategy
# import matplotlib.pyplot as plt
# import seaborn as sns
from typing import Dict, List, Tuple
import json

class StrategyAnalyzer:
    def __init__(self, data_dir: str = "data"):
        self.simulator = F1StrategySimulator(data_dir)
    
    def find_optimal_windows(self, driver_number: int, max_stops: int = 2) -> List[Dict]:
        """Find optimal pit windows for a driver"""
        race_length = max(self.simulator.get_baseline_lap_times(driver_number).keys())
        optimal_strategies = []
        
        # Try different pit strategies
        if max_stops == 1:
            # Single stop strategies
            for pit_lap in range(10, race_length - 5):
                for compound in ["SOFT", "MEDIUM", "HARD"]:
                    strategy = [PitStop(lap=pit_lap, tire_compound=compound)]
                    result = self.simulator.compare_strategies(driver_number, strategy)
                    
                    optimal_strategies.append({
                        "strategy": strategy,
                        "total_time": result["alternative_total_time"],
                        "improvement": result["time_difference"]
                    })
        
        elif max_stops == 2:
            # Two stop strategies
            for first_pit in range(8, 25):
                for second_pit in range(first_pit + 10, race_length - 5):
                    for first_compound in ["SOFT", "MEDIUM"]:
                        for second_compound in ["SOFT", "MEDIUM", "HARD"]:
                            strategy = [
                                PitStop(lap=first_pit, tire_compound=first_compound),
                                PitStop(lap=second_pit, tire_compound=second_compound)
                            ]
                            result = self.simulator.compare_strategies(driver_number, strategy)
                            
                            optimal_strategies.append({
                                "strategy": strategy,
                                "total_time": result["alternative_total_time"],
                                "improvement": result["time_difference"]
                            })
        
        # Sort by improvement (most negative = best improvement)
        optimal_strategies.sort(key=lambda x: x["improvement"])
        
        return optimal_strategies[:10]  # Return top 10
    
    def analyze_tire_degradation(self, driver_number: int) -> Dict:
        """Analyze tire degradation patterns from actual race data"""
        driver_laps = self.simulator.lap_times_df[
            (self.simulator.lap_times_df['driver_number'] == driver_number) &
            (self.simulator.lap_times_df['lap_duration'].notna()) &
            (self.simulator.lap_times_df['is_pit_out_lap'] == False)
        ].copy()
        
        # Get stint information
        stints = self.simulator.stints_df[
            (self.simulator.stints_df['driver_number'] == driver_number) &
            (self.simulator.stints_df['lap_start'].notna())
        ].copy()
        
        degradation_data = []
        
        for _, stint in stints.iterrows():
            stint_laps = driver_laps[
                (driver_laps['lap_number'] >= stint['lap_start']) &
                (driver_laps['lap_number'] <= stint['lap_end'])
            ].copy()
            
            if len(stint_laps) > 3:  # Need enough data points
                # Calculate degradation trend
                stint_laps['stint_lap'] = stint_laps['lap_number'] - stint['lap_start'] + 1
                
                # Simple linear regression for degradation rate
                x = stint_laps['stint_lap'].values
                y = stint_laps['lap_duration'].values
                
                if len(x) > 1:
                    slope = np.polyfit(x, y, 1)[0]
                    
                    degradation_data.append({
                        "compound": stint['compound'],
                        "stint_length": len(stint_laps),
                        "degradation_rate": slope,
                        "average_lap_time": y.mean(),
                        "stint_start": int(stint['lap_start'])
                    })
        
        return {
            "driver_number": driver_number,
            "stints": degradation_data,
            "avg_degradation_by_compound": self._group_degradation_by_compound(degradation_data)
        }
    
    def _group_degradation_by_compound(self, degradation_data: List[Dict]) -> Dict:
        """Group degradation data by tire compound"""
        compounds = {}
        
        for stint in degradation_data:
            compound = stint["compound"]
            if compound not in compounds:
                compounds[compound] = {
                    "degradation_rates": [],
                    "average_lap_times": [],
                    "stint_lengths": []
                }
            
            compounds[compound]["degradation_rates"].append(stint["degradation_rate"])
            compounds[compound]["average_lap_times"].append(stint["average_lap_time"])
            compounds[compound]["stint_lengths"].append(stint["stint_length"])
        
        # Calculate averages and remove lists
        for compound in compounds:
            compounds[compound]["avg_degradation"] = float(np.mean(compounds[compound]["degradation_rates"]))
            compounds[compound]["avg_lap_time"] = float(np.mean(compounds[compound]["average_lap_times"]))
            compounds[compound]["avg_stint_length"] = float(np.mean(compounds[compound]["stint_lengths"]))
            # Remove the lists as they're not needed in API response
            del compounds[compound]["degradation_rates"]
            del compounds[compound]["average_lap_times"] 
            del compounds[compound]["stint_lengths"]
        
        return compounds
    
    def compare_multiple_strategies(self, scenarios: Dict[str, Dict[int, List[PitStop]]]) -> Dict:
        """Compare multiple strategy scenarios"""
        results = {}
        
        for scenario_name, strategies in scenarios.items():
            print(f"Analyzing scenario: {scenario_name}")
            scenario_results = self.simulator.analyze_field_impact(strategies)
            
            # Calculate scenario statistics
            improvements = [r["time_difference"] for r in scenario_results.values()]
            total_improvement = sum(improvements)
            
            results[scenario_name] = {
                "driver_results": scenario_results,
                "total_time_saved": -total_improvement,  # negative improvement = time saved
                "drivers_improved": sum(1 for imp in improvements if imp < 0),
                "average_improvement": np.mean(improvements)
            }
        
        return results
    
    def export_results(self, results: Dict, filename: str = "strategy_analysis.json"):
        """Export analysis results to JSON"""
        # Convert complex objects to serializable format
        serializable_results = {}
        
        for key, value in results.items():
            if isinstance(value, dict):
                serializable_results[key] = self._make_serializable(value)
            else:
                serializable_results[key] = value
        
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        print(f"Results exported to {filename}")
    
    def _make_serializable(self, obj):
        """Convert objects to JSON serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__)
        else:
            return obj

def demo_analysis():
    """Demo analysis with multiple scenarios"""
    analyzer = StrategyAnalyzer()
    
    print("=== F1 STRATEGY ANALYSIS DEMO ===")
    
    # Analyze top 3 drivers
    top_drivers = [1, 16, 4]  # Verstappen, Leclerc, Norris (example)
    
    print("\n1. Finding optimal strategies for top drivers...")
    
    for driver in top_drivers:
        print(f"\nDriver {driver} optimal strategies:")
        optimal = analyzer.find_optimal_windows(driver, max_stops=2)
        
        for i, strategy in enumerate(optimal[:3]):
            print(f"  Option {i+1}: ", end="")
            for pit in strategy["strategy"]:
                print(f"Lap {pit.lap}({pit.tire_compound}) ", end="")
            print(f"-> {strategy['improvement']:.1f}s improvement")
    
    print("\n2. Analyzing tire degradation...")
    
    for driver in top_drivers[:2]:  # Just first 2 for demo
        degradation = analyzer.analyze_tire_degradation(driver)
        print(f"\nDriver {driver} tire degradation:")
        
        for compound, data in degradation["avg_degradation_by_compound"].items():
            print(f"  {compound}: {data['avg_degradation']:.3f}s/lap degradation")
    
    print("\n3. Comparing scenario: Earlier pit stops")
    
    # Create a scenario where everyone pits 2 laps earlier
    early_pit_scenario = {}
    for driver in top_drivers:
        actual_strategy = analyzer.simulator.get_actual_strategy(driver)
        early_strategy = []
        for pit in actual_strategy:
            early_strategy.append(PitStop(
                lap=max(1, pit.lap - 2),  # 2 laps earlier, but not before lap 1
                tire_compound=pit.tire_compound
            ))
        early_pit_scenario[driver] = early_strategy
    
    scenarios = {
        "original": {driver: analyzer.simulator.get_actual_strategy(driver) for driver in top_drivers},
        "early_pits": early_pit_scenario
    }
    
    comparison = analyzer.compare_multiple_strategies(scenarios)
    
    print(f"\nScenario comparison:")
    for scenario, results in comparison.items():
        print(f"  {scenario}: {results['drivers_improved']} drivers improved, "
              f"avg improvement: {results['average_improvement']:.1f}s")
    
    # Export results
    analyzer.export_results(comparison, "demo_strategy_analysis.json")
    
    return comparison

if __name__ == "__main__":
    try:
        results = demo_analysis()
    except Exception as e:
        print(f"Error running analysis: {e}")
        import traceback
        traceback.print_exc()
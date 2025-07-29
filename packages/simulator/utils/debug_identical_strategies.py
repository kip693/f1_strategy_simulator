#!/usr/bin/env python3
"""
Debug script to identify why identical strategies show time differences
"""

from core.pit_strategy_simulator import F1StrategySimulator

def debug_identical_strategies():
    """Debug the 64.4s difference issue"""
    print("🔍 Debugging identical strategy time difference...")
    
    simulator = F1StrategySimulator()
    
    # Get Verstappen's actual strategy
    actual_strategy = simulator.get_actual_strategy(1)
    
    print("\n📊 Verstappen's Actual Strategy:")
    total_pit_loss_actual = 0
    for i, pit in enumerate(actual_strategy):
        print(f"  {i+1}. Lap {pit.lap}: {pit.tire_compound} (pit_loss: {pit.pit_loss:.1f}s)")
        total_pit_loss_actual += pit.pit_loss
    
    print(f"\nTotal actual pit loss time: {total_pit_loss_actual:.1f}s")
    
    # Create identical alternative strategy but with default pit loss
    alternative_strategy = []
    for pit in actual_strategy:
        alternative_strategy.append(type(pit)(
            lap=pit.lap,
            tire_compound=pit.tire_compound
            # pit_loss will be default 22.0s
        ))
    
    print("\n📊 Alternative Strategy (identical but default pit_loss):")
    total_pit_loss_alt = 0
    for i, pit in enumerate(alternative_strategy):
        print(f"  {i+1}. Lap {pit.lap}: {pit.tire_compound} (pit_loss: {pit.pit_loss:.1f}s)")
        total_pit_loss_alt += pit.pit_loss
    
    print(f"\nTotal alternative pit loss time: {total_pit_loss_alt:.1f}s")
    print(f"Pit loss difference: {total_pit_loss_alt - total_pit_loss_actual:.1f}s")
    
    # Run comparison
    result = simulator.compare_strategies(1, alternative_strategy)
    
    print(f"\n🏁 Simulation Results:")
    print(f"  Actual total time: {result['actual_total_time']:.1f}s")
    print(f"  Alternative total time: {result['alternative_total_time']:.1f}s")
    print(f"  Time difference: {result['time_difference']:.1f}s")
    
    # Detailed analysis
    print(f"\n🔍 Detailed Analysis:")
    print(f"  Expected difference (pit loss only): {total_pit_loss_alt - total_pit_loss_actual:.1f}s")
    print(f"  Actual difference: {result['time_difference']:.1f}s")
    print(f"  Unexplained difference: {result['time_difference'] - (total_pit_loss_alt - total_pit_loss_actual):.1f}s")
    
    return result

def debug_baseline_lap_times():
    """Debug how baseline lap times are being used"""
    print("\n" + "="*60)
    print("🔍 Debugging baseline lap time usage...")
    
    simulator = F1StrategySimulator()
    baseline_times = simulator.get_baseline_lap_times(1)
    
    print(f"\nBaseline lap times for Verstappen:")
    print(f"  Total laps with data: {len(baseline_times)}")
    print(f"  Lap range: {min(baseline_times.keys())} - {max(baseline_times.keys())}")
    print(f"  Average lap time: {sum(baseline_times.values()) / len(baseline_times):.2f}s")
    
    # Check for missing laps
    all_laps = set(range(1, 54))  # Assuming 53 lap race
    missing_laps = all_laps - set(baseline_times.keys())
    
    print(f"  Missing laps: {sorted(missing_laps)}")
    
    if missing_laps:
        avg_time = sum(baseline_times.values()) / len(baseline_times)
        print(f"  Missing laps will use average: {avg_time:.2f}s")
        print(f"  Total time added for missing laps: {len(missing_laps) * avg_time:.1f}s")
    
    return baseline_times

def debug_pit_stop_data():
    """Debug the actual pit stop data from CSV"""
    print("\n" + "="*60)
    print("🔍 Debugging pit stop data from CSV...")
    
    simulator = F1StrategySimulator()
    
    # Look at raw pit stop data for Verstappen
    driver_pits = simulator.pit_stops_df[
        simulator.pit_stops_df['driver_number'] == 1
    ].copy()
    
    print(f"\nVerstappen's pit stops from CSV:")
    for _, pit in driver_pits.iterrows():
        pit_duration_ms = pit.get('pit_duration', 'N/A')
        pit_duration_s = pit_duration_ms / 1000.0 if pit_duration_ms != 'N/A' else 'N/A'
        print(f"  Lap {pit['lap_number']}: {pit_duration_s}s ({pit_duration_ms}ms)")
    
    return driver_pits

if __name__ == "__main__":
    debug_identical_strategies()
    debug_baseline_lap_times()
    debug_pit_stop_data()
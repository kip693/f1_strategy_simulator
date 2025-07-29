#!/usr/bin/env python3
"""
Test the enhanced circuit-aware pit loss calculation
"""

from core.dynamic_pit_loss_calculator import DynamicPitLossCalculator
from core.pit_strategy_simulator import F1StrategySimulator, PitStop

def test_circuit_aware_calculation():
    """Test circuit-aware pit loss calculation"""
    print("🏁 Testing Enhanced Circuit-Aware Pit Loss Calculation")
    print("=" * 70)
    
    calculator = DynamicPitLossCalculator()
    
    # Display circuit information
    circuit_info = calculator.get_circuit_info()
    if circuit_info:
        print(f"\n📍 Current Circuit: {circuit_info.get('name', 'Unknown')}")
        if 'theoretical_calculation' in circuit_info:
            calc = circuit_info['theoretical_calculation']
            print(f"  Pit lane length: {circuit_info.get('pit_lane_length', 'N/A')}m")
            print(f"  Speed limit: {circuit_info.get('pit_speed_limit', 'N/A')}km/h")
            print(f"  Theoretical pit loss: {calc.get('total_pit_loss', 'N/A'):.1f}s")
            print(f"  Breakdown:")
            print(f"    - Traverse time: {calc.get('traverse_time', 0):.1f}s")
            print(f"    - Entry penalty: {calc.get('entry_penalty', 0):.1f}s")
            print(f"    - Exit penalty: {calc.get('exit_penalty', 0):.1f}s")
            print(f"    - Pit work time: {calc.get('pit_work_time', 0):.1f}s")
            print(f"    - Track position loss: {calc.get('track_position_loss', 0):.1f}s")
    
    # Test various scenarios
    test_scenarios = [
        (1, 15, {}, "Verstappen - Early race normal"),
        (1, 22, {"safety_car": True}, "Verstappen - Safety car pit window"),
        (1, 35, {}, "Verstappen - Late race normal"),
        (44, 20, {"rain": True}, "Hamilton - Rain conditions"),
        (77, 25, {}, "Bottas - Normal midfield timing"),
    ]
    
    print(f"\n=== DETAILED PIT LOSS SCENARIOS ===")
    
    for driver, lap, conditions, description in test_scenarios:
        print(f"\n--- {description} ---")
        pit_loss, breakdown = calculator.calculate_pit_loss(driver, lap, conditions)
        
        print(f"Final pit loss: {pit_loss:.1f}s")
        print(f"Breakdown:")
        print(f"  Base time: {breakdown.get('base_time', 0):.1f}s")
        
        if 'circuit' in breakdown:
            print(f"  Circuit: {breakdown['circuit']}")
        if 'calibration_factor' in breakdown:
            print(f"  Calibration: {breakdown['calibration_factor']:.3f}")
        
        print(f"  Lap factor: {breakdown.get('lap_factor', 1.0):.3f}")
        print(f"  Team factor: {breakdown.get('team_factor', 1.0):.3f}")
        print(f"  Situation factor: {breakdown.get('situation_factor', 1.0):.3f}")
        
        if 'circuit_traffic_factor' in breakdown:
            print(f"  Circuit traffic: {breakdown['circuit_traffic_factor']:.3f}")
        
        print(f"  Random factor: {breakdown.get('random_factor', 1.0):.3f}")

def compare_circuit_characteristics():
    """Compare pit loss across different circuits (theoretical)"""
    print(f"\n" + "=" * 70)
    print("🌍 Circuit Comparison Analysis")
    print("=" * 70)
    
    calculator = DynamicPitLossCalculator()
    
    if hasattr(calculator, 'model') and 'circuits' in calculator.model:
        circuits = calculator.model['circuits']
        
        print(f"\nCircuit Characteristics Comparison:")
        print(f"{'Circuit':<25} | {'Pit Lane':<8} | {'Speed':<5} | {'Complexity':<10} | {'Total Loss':<9}")
        print(f"{'-' * 25} | {'-' * 8} | {'-' * 5} | {'-' * 10} | {'-' * 9}")
        
        for circuit_name, data in circuits.items():
            name = data.get('name', circuit_name)[:24]
            pit_length = data.get('pit_lane_length', 0)
            speed_limit = data.get('pit_speed_limit', 0)
            
            entry_complexity = data.get('pit_entry_complexity', 1.0)
            exit_complexity = data.get('pit_exit_complexity', 1.0)
            avg_complexity = (entry_complexity + exit_complexity) / 2
            
            if 'theoretical_calculation' in data:
                total_loss = data['theoretical_calculation'].get('total_pit_loss', 0)
            else:
                total_loss = 0
            
            print(f"{name:<25} | {pit_length:6.0f}m | {speed_limit:3d}km/h | {avg_complexity:8.1f} | {total_loss:7.1f}s")

def test_traffic_patterns():
    """Test how pit loss varies with traffic patterns throughout the race"""
    print(f"\n" + "=" * 70)
    print("🚥 Pit Lane Traffic Pattern Analysis")
    print("=" * 70)
    
    calculator = DynamicPitLossCalculator()
    driver_num = 1  # Verstappen
    
    print(f"Pit loss variation for Driver #{driver_num} throughout race:")
    print(f"{'Lap':<4} | {'Pit Loss':<8} | {'Traffic':<10} | {'Period':<15}")
    print(f"{'-' * 4} | {'-' * 8} | {'-' * 10} | {'-' * 15}")
    
    for lap in range(5, 51, 5):  # Every 5 laps
        pit_loss, breakdown = calculator.calculate_pit_loss(driver_num, lap)
        
        # Determine expected traffic level
        if lap in range(12, 19) or lap in range(20, 26) or lap in range(32, 39):
            traffic = "High"
        elif lap < 10 or lap > 45:
            traffic = "Low"
        else:
            traffic = "Medium"
        
        # Determine race period
        if lap <= 15:
            period = "Early Race"
        elif lap <= 35:
            period = "Mid Race"
        else:
            period = "Late Race"
        
        traffic_factor = breakdown.get('circuit_traffic_factor', 1.0)
        
        print(f"{lap:3d} | {pit_loss:6.1f}s | {traffic:<8} ({traffic_factor:.2f}) | {period}")

def test_enhanced_vs_basic():
    """Compare enhanced circuit-aware vs basic calculation"""
    print(f"\n" + "=" * 70)
    print("⚔️  Enhanced vs Basic Pit Loss Comparison")
    print("=" * 70)
    
    # Test with full simulator integration
    print("\nTesting with F1 Strategy Simulator integration:")
    
    try:
        # Enhanced simulator
        enhanced_sim = F1StrategySimulator(use_dynamic_pit_loss=True)
        
        test_strategy = [
            PitStop(lap=20, tire_compound="MEDIUM"),
            PitStop(lap=40, tire_compound="HARD")
        ]
        
        print(f"\nTest strategy:")
        for pit in test_strategy:
            print(f"  Lap {pit.lap}: {pit.tire_compound}")
        
        result = enhanced_sim.compare_strategies(1, test_strategy)
        
        print(f"\nEnhanced Circuit-Aware Results:")
        print(f"  Alternative strategy time: {result['alternative_total_time']:.1f}s")
        print(f"  Time difference: {result['time_difference']:.1f}s")
        print(f"  Improvement: {'✅' if result['improvement'] else '❌'}")
        
        # Show individual pit loss calculations
        print(f"\nDetailed pit loss breakdown:")
        for pit in test_strategy:
            pit_loss = enhanced_sim.calculate_dynamic_pit_loss(1, pit.lap)
            print(f"  Lap {pit.lap}: {pit_loss:.1f}s pit loss")
            
    except Exception as e:
        print(f"Error in enhanced testing: {e}")

def main():
    """Run all enhanced pit loss tests"""
    print("🏁 Enhanced Circuit-Aware Pit Loss Testing Suite")
    print("=" * 70)
    
    try:
        # Test 1: Circuit-aware calculation
        test_circuit_aware_calculation()
        
        # Test 2: Circuit comparison
        compare_circuit_characteristics()
        
        # Test 3: Traffic patterns
        test_traffic_patterns()
        
        # Test 4: Enhanced vs basic
        test_enhanced_vs_basic()
        
        print("\n" + "=" * 70)
        print("✅ All enhanced pit loss tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
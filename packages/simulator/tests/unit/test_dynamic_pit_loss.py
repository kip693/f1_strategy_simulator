#!/usr/bin/env python3
"""
Test the dynamic pit loss implementation in the F1 Strategy Simulator
"""

from core.pit_strategy_simulator import F1StrategySimulator, PitStop

def test_dynamic_vs_static_comparison():
    """Compare dynamic vs static pit loss calculations"""
    print("🧪 Testing Dynamic vs Static Pit Loss Calculations")
    print("=" * 60)
    
    # Test with static pit loss
    print("\n--- Static Pit Loss Simulator ---")
    static_simulator = F1StrategySimulator(use_dynamic_pit_loss=False)
    
    # Test with dynamic pit loss
    print("\n--- Dynamic Pit Loss Simulator ---")
    dynamic_simulator = F1StrategySimulator(use_dynamic_pit_loss=True)
    
    # Test strategy for Verstappen
    test_strategy = [
        PitStop(lap=15, tire_compound="SOFT"),
        PitStop(lap=35, tire_compound="MEDIUM")
    ]
    
    print(f"\nTesting strategy for Verstappen (Driver #1):")
    for pit in test_strategy:
        print(f"  Lap {pit.lap}: {pit.tire_compound}")
    
    # Static comparison
    print(f"\n🔧 STATIC PIT LOSS RESULTS:")
    static_result = static_simulator.compare_strategies(1, test_strategy)
    print(f"  Actual time: {static_result['actual_total_time']:.1f}s")
    print(f"  Alternative time: {static_result['alternative_total_time']:.1f}s")
    print(f"  Time difference: {static_result['time_difference']:.1f}s")
    print(f"  Improvement: {static_result['improvement']}")
    
    # Dynamic comparison
    print(f"\n⚡ DYNAMIC PIT LOSS RESULTS:")
    dynamic_result = dynamic_simulator.compare_strategies(1, test_strategy)
    print(f"  Actual time: {dynamic_result['actual_total_time']:.1f}s")
    print(f"  Alternative time: {dynamic_result['alternative_total_time']:.1f}s")
    print(f"  Time difference: {dynamic_result['time_difference']:.1f}s")
    print(f"  Improvement: {dynamic_result['improvement']}")
    
    # Compare the differences
    time_diff_change = dynamic_result['time_difference'] - static_result['time_difference']
    print(f"\n📊 COMPARISON:")
    print(f"  Time difference change: {time_diff_change:+.1f}s")
    print(f"  Strategy evaluation changed: {static_result['improvement'] != dynamic_result['improvement']}")
    
    return static_result, dynamic_result

def test_different_drivers():
    """Test dynamic pit loss with different drivers (different team factors)"""
    print("\n" + "=" * 60)
    print("🏁 Testing Different Drivers with Dynamic Pit Loss")
    print("=" * 60)
    
    simulator = F1StrategySimulator(use_dynamic_pit_loss=True)
    
    # Test drivers from different teams
    test_drivers = [
        (1, "Verstappen (Red Bull - Top Team)"),
        (44, "Hamilton (Mercedes - Top Team)"),
        (4, "Norris (McLaren - Midfield)"),
        (77, "Bottas (Alfa Romeo - Back Team)")
    ]
    
    test_strategy = [
        PitStop(lap=20, tire_compound="MEDIUM"),
        PitStop(lap=40, tire_compound="HARD")
    ]
    
    for driver_num, driver_desc in test_drivers:
        print(f"\n--- {driver_desc} ---")
        try:
            result = simulator.compare_strategies(driver_num, test_strategy)
            print(f"  Time difference: {result['time_difference']:.1f}s")
            print(f"  Improvement: {'✅' if result['improvement'] else '❌'}")
            
            # Show dynamic pit loss for specific laps
            early_pit_loss = simulator.calculate_dynamic_pit_loss(driver_num, 20)
            late_pit_loss = simulator.calculate_dynamic_pit_loss(driver_num, 40)
            print(f"  Dynamic pit loss - Lap 20: {early_pit_loss:.1f}s")
            print(f"  Dynamic pit loss - Lap 40: {late_pit_loss:.1f}s")
            
        except Exception as e:
            print(f"  Error: {e}")

def test_pit_loss_conditions():
    """Test pit loss under different race conditions"""
    print("\n" + "=" * 60)
    print("🌧️  Testing Pit Loss Under Different Conditions")
    print("=" * 60)
    
    simulator = F1StrategySimulator(use_dynamic_pit_loss=True)
    
    driver_num = 1  # Verstappen
    lap_num = 25
    
    conditions_list = [
        ({}, "Normal conditions"),
        ({"safety_car": True}, "Safety car period"),
        ({"rain": True}, "Wet conditions"),
        ({"damaged_car": True}, "Damaged car")
    ]
    
    print(f"Driver #{driver_num} pit stop on lap {lap_num}:")
    
    for conditions, description in conditions_list:
        pit_loss = simulator.calculate_dynamic_pit_loss(driver_num, lap_num, conditions)
        print(f"  {description:20}: {pit_loss:5.1f}s")

def test_lap_progression():
    """Test how pit loss changes throughout the race"""
    print("\n" + "=" * 60)
    print("📈 Testing Pit Loss Progression Throughout Race")
    print("=" * 60)
    
    simulator = F1StrategySimulator(use_dynamic_pit_loss=True)
    
    driver_num = 1  # Verstappen
    test_laps = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    
    print(f"Dynamic pit loss for Driver #{driver_num} throughout race:")
    print("Lap | Pit Loss | Period")
    print("----|----------|--------")
    
    for lap in test_laps:
        pit_loss = simulator.calculate_dynamic_pit_loss(driver_num, lap)
        
        # Determine race period
        if lap <= 15:
            period = "Early (High Traffic)"
        elif lap <= 35:
            period = "Mid (Normal)"
        else:
            period = "Late (Low Traffic)"
        
        print(f"{lap:3d} | {pit_loss:8.1f}s | {period}")

def main():
    """Run all dynamic pit loss tests"""
    print("🏁 F1 Dynamic Pit Loss Testing Suite")
    print("=" * 60)
    
    try:
        # Test 1: Static vs Dynamic comparison
        test_dynamic_vs_static_comparison()
        
        # Test 2: Different drivers
        test_different_drivers()
        
        # Test 3: Different conditions
        test_pit_loss_conditions()
        
        # Test 4: Lap progression
        test_lap_progression()
        
        print("\n" + "=" * 60)
        print("✅ All dynamic pit loss tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
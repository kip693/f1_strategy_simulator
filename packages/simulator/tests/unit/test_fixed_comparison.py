#!/usr/bin/env python3
"""
Test the fixed strategy comparison
"""

from core.pit_strategy_simulator import F1StrategySimulator, PitStop

def test_fixed_comparison():
    """Test that identical strategies now show 0 difference"""
    print("🧪 Testing fixed strategy comparison...")
    
    simulator = F1StrategySimulator()
    
    # Get Verstappen's actual strategy
    actual_strategy = simulator.get_actual_strategy(1)
    
    # Create identical alternative strategy
    identical_strategy = []
    for pit in actual_strategy:
        identical_strategy.append(PitStop(
            lap=pit.lap,
            tire_compound=pit.tire_compound
            # pit_loss will be default 22.0s (same as normalized comparison)
        ))
    
    print("\n📊 Testing identical strategies:")
    print("Actual strategy:")
    for pit in actual_strategy:
        print(f"  Lap {pit.lap}: {pit.tire_compound}")
    
    print("Alternative strategy (identical):")
    for pit in identical_strategy:
        print(f"  Lap {pit.lap}: {pit.tire_compound}")
    
    # Run comparison
    result = simulator.compare_strategies(1, identical_strategy)
    
    print(f"\n🏁 Results:")
    print(f"  Time difference: {result['time_difference']:.1f}s")
    print(f"  Improvement: {result['improvement']}")
    
    if abs(result['time_difference']) < 0.1:
        print("  ✅ SUCCESS: Identical strategies show ~0 difference!")
    else:
        print(f"  ❌ ISSUE: Still showing {result['time_difference']:.1f}s difference")
    
    return result

def test_different_strategies():
    """Test with actually different strategies"""
    print("\n" + "="*50)
    print("🧪 Testing with different strategies...")
    
    simulator = F1StrategySimulator()
    
    # Test a genuinely different strategy
    different_strategy = [
        PitStop(lap=15, tire_compound="SOFT"),
        PitStop(lap=35, tire_compound="MEDIUM")
    ]
    
    print("\n📊 Testing different strategies:")
    actual_strategy = simulator.get_actual_strategy(1)
    print("Actual strategy:")
    for pit in actual_strategy:
        print(f"  Lap {pit.lap}: {pit.tire_compound}")
    
    print("Alternative strategy (different):")
    for pit in different_strategy:
        print(f"  Lap {pit.lap}: {pit.tire_compound}")
    
    result = simulator.compare_strategies(1, different_strategy)
    
    print(f"\n🏁 Results:")
    print(f"  Time difference: {result['time_difference']:.1f}s")
    print(f"  Improvement: {result['improvement']}")
    
    return result

if __name__ == "__main__":
    test_fixed_comparison()
    test_different_strategies()
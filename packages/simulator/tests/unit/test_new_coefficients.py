#!/usr/bin/env python3
"""
Test script to validate the new tire coefficients
"""

from core.pit_strategy_simulator import F1StrategySimulator, PitStop

def test_new_coefficients():
    """Test the simulator with new tire coefficients"""
    print("🏁 Testing F1 Strategy Simulator with new tire coefficients...")
    
    # Initialize simulator (will load new coefficients)
    simulator = F1StrategySimulator()
    
    print("\n📊 Current tire compound settings:")
    for compound, tire in simulator.tire_compounds.items():
        print(f"  {compound:6s}: {tire.performance_delta:+6.2f}s/lap | "
              f"degradation: {tire.degradation_rate:6.3f}s/lap | "
              f"max stint: {tire.max_stint_length:2d} laps")
    
    # Test Verstappen alternative strategy
    print("\n🧪 Testing Verstappen alternative strategy...")
    alternative_strategy = [
        PitStop(lap=15, tire_compound="SOFT"),
        PitStop(lap=35, tire_compound="MEDIUM")
    ]
    
    try:
        result = simulator.compare_strategies(1, alternative_strategy)
        
        print(f"\nActual strategy:")
        for pit in result["actual_strategy"]:
            print(f"  Lap {pit.lap}: {pit.tire_compound}")
        
        print(f"\nAlternative strategy:")
        for pit in result["alternative_strategy"]:
            print(f"  Lap {pit.lap}: {pit.tire_compound}")
        
        print(f"\nResults:")
        print(f"  Actual total time: {result['actual_total_time']:.1f}s")
        print(f"  Alternative total time: {result['alternative_total_time']:.1f}s")
        print(f"  Time difference: {result['time_difference']:.1f}s")
        
        if result["improvement"]:
            print(f"  ✅ Alternative strategy is {abs(result['time_difference']):.1f}s faster!")
        else:
            print(f"  ❌ Alternative strategy is {result['time_difference']:.1f}s slower")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in simulation: {e}")
        return None

def compare_old_vs_new():
    """Compare results with old vs new tire coefficients"""
    print("\n" + "="*60)
    print("COMPARISON: OLD vs NEW TIRE COEFFICIENTS")
    print("="*60)
    
    print("\n📊 OLD COEFFICIENTS (original simulation):")
    print("  SOFT  : -0.600s/lap | degradation: 0.080s/lap | max stint: 25 laps")
    print("  MEDIUM:  0.000s/lap | degradation: 0.050s/lap | max stint: 35 laps") 
    print("  HARD  : +0.500s/lap | degradation: 0.030s/lap | max stint: 45 laps")
    
    print("\n📊 NEW COEFFICIENTS (data-driven):")
    try:
        simulator = F1StrategySimulator()
        for compound, tire in simulator.tire_compounds.items():
            print(f"  {compound:6s}: {tire.performance_delta:+6.3f}s/lap | "
                  f"degradation: {tire.degradation_rate:6.3f}s/lap | "
                  f"max stint: {tire.max_stint_length:2d} laps")
    except Exception as e:
        print(f"  Error loading new coefficients: {e}")
    
    print("\n🔍 KEY INSIGHTS:")
    print("  • SOFT tires are actually SLOWER (+1.007s/lap) than MEDIUM!")
    print("  • SOFT tires degrade much faster (0.424s/lap vs 0.148s/lap)")
    print("  • HARD tires are essentially equal to MEDIUM (+0.030s/lap)")
    print("  • HARD/MEDIUM degradation rates are very similar")
    print("  • Real stint lengths are much shorter than theoretical max")
    
    print("\n💡 WHY ALTERNATIVES ARE SLOWER:")
    print("  1. SOFT tires provide no speed advantage in race conditions")
    print("  2. SOFT degradation is 3x higher than expected")
    print("  3. Most alternative strategies use more SOFT compound")
    print("  4. Real race conditions favor tire conservation over outright pace")

if __name__ == "__main__":
    test_new_coefficients()
    compare_old_vs_new()
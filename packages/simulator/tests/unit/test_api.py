#!/usr/bin/env python3
"""
Test script for F1 Strategy Simulator API
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test API health check"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_race_info():
    """Test race info endpoint"""
    print("\nTesting race info...")
    response = requests.get(f"{BASE_URL}/race-info")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Race: {data['race_name']}")
        print(f"Total laps: {data['total_laps']}")
        print(f"Drivers: {len(data['drivers'])}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200

def test_get_drivers():
    """Test get drivers endpoint"""
    print("\nTesting get drivers...")
    response = requests.get(f"{BASE_URL}/drivers")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        drivers = response.json()
        print(f"Found {len(drivers)} drivers:")
        for driver in drivers[:5]:  # Show first 5
            print(f"  {driver['driver_number']}: {driver['name']} ({driver['team']})")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200

def test_actual_strategy():
    """Test actual strategy endpoint"""
    print("\nTesting actual strategy for Verstappen (driver 1)...")
    response = requests.get(f"{BASE_URL}/actual-strategy/1")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        strategy = response.json()
        print("Actual strategy:")
        for pit in strategy:
            print(f"  Lap {pit['lap']}: {pit['tire_compound']}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200

def test_simulate_strategy():
    """Test strategy simulation"""
    print("\nTesting strategy simulation...")
    
    # Alternative strategy for Verstappen
    payload = {
        "driver_number": 1,
        "pit_stops": [
            {"lap": 15, "tire_compound": "SOFT"},
            {"lap": 35, "tire_compound": "MEDIUM"}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/simulate-strategy", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Driver: {result['driver_name']}")
        print(f"Time difference: {result['time_difference']:.1f}s")
        print(f"Improvement: {result['improvement']}")
        print("Alternative strategy:")
        for pit in result['alternative_strategy']:
            print(f"  Lap {pit['lap']}: {pit['tire_compound']}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200

def test_optimal_strategy():
    """Test optimal strategy finder"""
    print("\nTesting optimal strategy finder...")
    response = requests.get(f"{BASE_URL}/optimal-strategy/1?max_stops=2&top_n=3")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Driver: {result['driver_name']}")
        print("Top optimal strategies:")
        for strategy in result['optimal_strategies']:
            print(f"  Rank {strategy['rank']}: {strategy['improvement']:.1f}s improvement")
            for pit in strategy['strategy']:
                print(f"    Lap {pit['lap']}: {pit['tire_compound']}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200

def test_tire_degradation():
    """Test tire degradation analysis"""
    print("\nTesting tire degradation analysis...")
    response = requests.get(f"{BASE_URL}/tire-degradation/1")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Driver: {result['driver_name']}")
        print("Degradation by compound:")
        for compound, data in result['avg_degradation_by_compound'].items():
            print(f"  {compound}: {data['avg_degradation']:.3f}s/lap")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200

def test_field_analysis():
    """Test field-wide strategy analysis"""
    print("\nTesting field analysis...")
    
    # Test with multiple drivers
    payload = {
        "strategies": {
            1: [{"lap": 18, "tire_compound": "SOFT"}, {"lap": 36, "tire_compound": "MEDIUM"}],
            16: [{"lap": 20, "tire_compound": "SOFT"}, {"lap": 38, "tire_compound": "HARD"}]
        }
    }
    
    response = requests.post(f"{BASE_URL}/field-analysis", json=payload)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Drivers improved: {result['drivers_improved']}")
        print(f"Average improvement: {result['average_improvement']:.1f}s")
        print("Driver results:")
        for driver_num, data in result['driver_results'].items():
            print(f"  Driver {driver_num}: {data['time_difference']:.1f}s, Position: {data['predicted_position']}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200

def run_all_tests():
    """Run all API tests"""
    print("=== F1 Strategy Simulator API Tests ===")
    
    tests = [
        test_health_check,
        test_race_info,
        test_get_drivers,
        test_actual_strategy,
        test_simulate_strategy,
        test_optimal_strategy,
        test_tire_degradation,
        test_field_analysis
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED")
            else:
                print("❌ FAILED")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n=== TEST SUMMARY ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    return passed == total

if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to API server.")
        print("Make sure the server is running with: python3 api.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
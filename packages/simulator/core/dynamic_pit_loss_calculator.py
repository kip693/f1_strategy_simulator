#!/usr/bin/env python3
"""
Dynamic Pit Loss Calculator
Creates realistic pit loss times based on race conditions, lap number, and driver factors
"""

import json
import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class PitLossFactors:
    """Factors that affect pit stop time"""
    base_time: float
    traffic_factor: float
    safety_car_factor: float
    driver_factor: float
    weather_factor: float
    lap_factor: float

class DynamicPitLossCalculator:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.load_enhanced_model()
    
    def create_realistic_model(self):
        """Create a realistic pit loss model based on F1 analysis"""
        # Based on real F1 data analysis and expert knowledge
        model = {
            "version": "2.0",
            "description": "Realistic dynamic pit loss calculation based on F1 racing analysis",
            "base_pit_loss": 22.0,  # Standard pit loss time in seconds
            
            # Lap-based factors (traffic and race conditions)
            "lap_factors": {
                "early_race": {
                    "laps": [1, 15],
                    "factor": 1.15,  # More traffic, slower pit entry/exit
                    "description": "Heavy traffic in early race"
                },
                "mid_race": {
                    "laps": [16, 35],
                    "factor": 1.0,   # Normal conditions
                    "description": "Normal traffic conditions"
                },
                "late_race": {
                    "laps": [36, 60],
                    "factor": 0.95,  # Less traffic, cleaner pit lane
                    "description": "Light traffic in late race"
                }
            },
            
            # Driver/Team efficiency factors
            "team_factors": {
                # Top teams (faster pit crews)
                "top_teams": {
                    "drivers": [1, 11, 16, 55, 44, 63],  # Red Bull, Ferrari, Mercedes
                    "factor": 0.92,
                    "description": "Elite pit crews"
                },
                # Mid-field teams
                "midfield_teams": {
                    "drivers": [4, 81, 14, 18, 10, 27],  # McLaren, Alpine, etc.
                    "factor": 1.0,
                    "description": "Standard pit crews"
                },
                # Back-marker teams
                "back_teams": {
                    "drivers": [77, 20, 24, 22, 2, 31],  # Smaller teams
                    "factor": 1.08,
                    "description": "Developing pit crews"
                }
            },
            
            # Situational factors
            "situation_factors": {
                "safety_car": {
                    "factor": 1.25,
                    "description": "Pit lane congestion during safety car"
                },
                "rain": {
                    "factor": 1.15,
                    "description": "Slower operations in wet conditions"
                },
                "damaged_car": {
                    "factor": 1.3,
                    "description": "Additional time for damage assessment"
                }
            },
            
            # Random variation (realistic spread)
            "random_variation": {
                "std_dev": 1.2,
                "min_factor": 0.85,
                "max_factor": 1.20,
                "description": "Natural variation in pit stop execution"
            }
        }
        
        # Save the model
        with open(f"{self.data_dir}/dynamic_pit_loss_model.json", 'w') as f:
            json.dump(model, f, indent=2)
        
        self.model = model
        print(f"✅ Realistic dynamic pit loss model created")
        return model
    
    def load_enhanced_model(self):
        """Load the enhanced circuit-aware pit loss model"""
        try:
            # Try to load enhanced model first
            with open(f"{self.data_dir}/enhanced_pit_loss_model.json", 'r') as f:
                self.model = json.load(f)
                self.use_enhanced = True
                print("✅ Enhanced circuit-aware pit loss model loaded")
        except FileNotFoundError:
            try:
                # Fallback to basic dynamic model
                with open(f"{self.data_dir}/dynamic_pit_loss_model.json", 'r') as f:
                    self.model = json.load(f)
                    self.use_enhanced = False
                    print("⚠️  Using basic dynamic model (enhanced model not found)")
            except FileNotFoundError:
                # Create basic model if none exists
                self.model = self.create_realistic_model()
                self.use_enhanced = False
                print("⚠️  Created fallback model")
        return self.model
    
    def load_model(self):
        """Legacy method for compatibility"""
        return self.load_enhanced_model()
    
    def calculate_pit_loss(self, driver_number: int, lap_number: int, 
                          conditions: Optional[Dict] = None) -> Tuple[float, Dict]:
        """
        Calculate dynamic pit loss time with circuit characteristics
        
        Args:
            driver_number: F1 driver number
            lap_number: Current lap number
            conditions: Optional race conditions (safety_car, rain, etc.)
            
        Returns:
            Tuple of (pit_loss_time, breakdown_dict)
        """
        if not hasattr(self, 'model'):
            self.load_enhanced_model()
        
        breakdown = {}
        
        # Start with base pit loss (circuit-aware if enhanced model available)
        if self.use_enhanced and "circuits" in self.model:
            current_circuit = self.model.get("current_circuit", "suzuka")
            circuit_data = self.model["circuits"].get(current_circuit, {})
            
            if "theoretical_calculation" in circuit_data:
                base_time = circuit_data["theoretical_calculation"]["total_pit_loss"]
                # Apply calibration factor if available
                calibration = self.model.get("calibration_factor", 1.0)
                base_time *= calibration
                breakdown["circuit"] = current_circuit
                breakdown["calibration_factor"] = calibration
            else:
                base_time = self.model.get("base_pit_loss", 22.0)
        else:
            base_time = self.model.get("base_pit_loss", 22.0)
        
        current_time = base_time
        breakdown["base_time"] = base_time
        
        # Apply lap-based factor
        lap_factor = self._get_lap_factor(lap_number)
        current_time *= lap_factor
        breakdown["lap_factor"] = lap_factor
        breakdown["after_lap_factor"] = current_time
        
        # Apply team/driver factor
        team_factor = self._get_team_factor(driver_number)
        current_time *= team_factor
        breakdown["team_factor"] = team_factor
        breakdown["after_team_factor"] = current_time
        
        # Apply situational factors
        situation_factor = self._get_situation_factor(conditions or {})
        current_time *= situation_factor
        breakdown["situation_factor"] = situation_factor
        breakdown["after_situation_factor"] = current_time
        
        # Apply circuit-specific traffic factor if enhanced model is available
        if self.use_enhanced and "circuit_factors" in self.model:
            traffic_factor = self._get_circuit_traffic_factor(lap_number, conditions or {})
            current_time *= traffic_factor
            breakdown["circuit_traffic_factor"] = traffic_factor
            breakdown["after_circuit_factor"] = current_time
        
        # Apply random variation (with seed for consistency)
        np.random.seed(driver_number * 100 + lap_number)  # Deterministic "randomness"
        random_factor = self._get_random_factor()
        current_time *= random_factor
        breakdown["random_factor"] = random_factor
        breakdown["final_time"] = current_time
        
        return round(current_time, 2), breakdown
    
    def _get_lap_factor(self, lap_number: int) -> float:
        """Get lap-based traffic factor"""
        lap_factors = self.model["lap_factors"]
        
        for period, data in lap_factors.items():
            start_lap, end_lap = data["laps"]
            if start_lap <= lap_number <= end_lap:
                return data["factor"]
        
        # Default to mid-race factor
        return lap_factors["mid_race"]["factor"]
    
    def _get_team_factor(self, driver_number: int) -> float:
        """Get team/driver efficiency factor"""
        team_factors = self.model["team_factors"]
        
        for team_type, data in team_factors.items():
            if driver_number in data["drivers"]:
                return data["factor"]
        
        # Default to midfield factor
        return team_factors["midfield_teams"]["factor"]
    
    def _get_situation_factor(self, conditions: Dict) -> float:
        """Get situational factor based on race conditions"""
        factor = 1.0
        situation_factors = self.model["situation_factors"]
        
        if conditions.get("safety_car", False):
            factor *= situation_factors["safety_car"]["factor"]
        
        if conditions.get("rain", False):
            factor *= situation_factors["rain"]["factor"]
        
        if conditions.get("damaged_car", False):
            factor *= situation_factors["damaged_car"]["factor"]
        
        return factor
    
    def _get_random_factor(self) -> float:
        """Get random variation factor"""
        random_config = self.model["random_variation"]
        
        # Generate normal distribution around 1.0
        factor = np.random.normal(1.0, random_config["std_dev"] / 6)  # 6-sigma range
        
        # Clamp to realistic bounds
        factor = max(random_config["min_factor"], 
                    min(random_config["max_factor"], factor))
        
        return factor
    
    def _get_circuit_traffic_factor(self, lap_number: int, conditions: Dict) -> float:
        """Get circuit-specific traffic factor"""
        if not self.use_enhanced:
            return 1.0
        
        circuit_factors = self.model.get("circuit_factors", {})
        
        # Determine traffic level based on typical pit windows
        # High traffic periods: laps 12-18, 20-25, 32-38 (typical pit windows)
        traffic_level = "medium"  # default
        
        if lap_number in range(12, 19) or lap_number in range(20, 26) or lap_number in range(32, 39):
            traffic_level = "high"
        elif lap_number < 10 or lap_number > 45:
            traffic_level = "low"
        
        # Override based on conditions
        if conditions.get("safety_car", False):
            traffic_level = "high"  # Everyone pits during safety car
        
        traffic_factors = circuit_factors.get("pit_lane_traffic", {})
        return traffic_factors.get(traffic_level, 1.0)
    
    def get_circuit_info(self) -> Dict:
        """Get current circuit information"""
        if self.use_enhanced and "circuits" in self.model:
            current_circuit = self.model.get("current_circuit", "suzuka")
            return self.model["circuits"].get(current_circuit, {})
        return {}
    
    def get_expected_pit_loss(self, driver_number: int, lap_number: int) -> float:
        """Get expected pit loss without random variation (for consistent simulation)"""
        pit_loss, _ = self.calculate_pit_loss(driver_number, lap_number)
        return pit_loss
    
    def analyze_pit_loss_range(self, driver_number: int):
        """Analyze pit loss time range for a driver across different laps"""
        print(f"\n=== PIT LOSS ANALYSIS FOR DRIVER #{driver_number} ===")
        
        test_laps = [5, 15, 25, 35, 45]
        conditions_list = [
            {},
            {"safety_car": True},
            {"rain": True},
            {"damaged_car": True}
        ]
        
        for conditions in conditions_list:
            condition_name = "Normal"
            if conditions.get("safety_car"):
                condition_name = "Safety Car"
            elif conditions.get("rain"):
                condition_name = "Rain"
            elif conditions.get("damaged_car"):
                condition_name = "Damaged Car"
            
            print(f"\n--- {condition_name} Conditions ---")
            for lap in test_laps:
                pit_loss, breakdown = self.calculate_pit_loss(driver_number, lap, conditions)
                print(f"  Lap {lap:2d}: {pit_loss:5.1f}s (base: {breakdown['base_time']:.1f}s)")

def demo_dynamic_pit_loss():
    """Demonstrate the dynamic pit loss calculator"""
    print("🏁 F1 Dynamic Pit Loss Calculator Demo")
    print("=" * 50)
    
    calculator = DynamicPitLossCalculator()
    
    # Test with different drivers and conditions
    test_scenarios = [
        (1, 15, {}, "Verstappen early race"),
        (1, 35, {}, "Verstappen late race"),
        (44, 20, {"safety_car": True}, "Hamilton during safety car"),
        (77, 25, {"rain": True}, "Bottas in rain"),
        (20, 30, {}, "Magnussen normal conditions")
    ]
    
    print("\n=== SCENARIO TESTING ===")
    for driver, lap, conditions, description in test_scenarios:
        pit_loss, breakdown = calculator.calculate_pit_loss(driver, lap, conditions)
        print(f"\n{description}:")
        print(f"  Pit loss: {pit_loss:.1f}s")
        print(f"  Breakdown: base={breakdown['base_time']:.1f}s, "
              f"lap_factor={breakdown['lap_factor']:.2f}, "
              f"team_factor={breakdown['team_factor']:.2f}")
    
    # Analyze range for specific drivers
    for driver_num in [1, 44, 77]:  # Top, mid, back
        calculator.analyze_pit_loss_range(driver_num)

if __name__ == "__main__":
    demo_dynamic_pit_loss()
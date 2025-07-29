#!/usr/bin/env python3
"""
Pydantic models for F1 Strategy Simulator API
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Union
from enum import Enum

class TireCompound(str, Enum):
    SOFT = "SOFT"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class PitStopRequest(BaseModel):
    lap: int = Field(..., ge=1, le=100, description="Lap number for pit stop")
    tire_compound: TireCompound = Field(..., description="Tire compound to change to")
    pit_loss: Optional[float] = Field(22.0, ge=15.0, le=40.0, description="Pit stop time loss in seconds")

class DriverStrategyRequest(BaseModel):
    driver_number: int = Field(..., ge=1, le=99, description="Driver number")
    pit_stops: List[PitStopRequest] = Field(..., description="List of pit stops")
    
    @validator('pit_stops')
    def validate_pit_stops(cls, v):
        if len(v) > 4:
            raise ValueError("Maximum 4 pit stops allowed")
        
        # Check that pit stops are in chronological order
        laps = [pit.lap for pit in v]
        if laps != sorted(laps):
            raise ValueError("Pit stops must be in chronological order")
        
        # Check minimum gap between pit stops
        for i in range(1, len(laps)):
            if laps[i] - laps[i-1] < 3:
                raise ValueError("Minimum 3 laps between pit stops")
        
        return v

class MultiDriverStrategyRequest(BaseModel):
    strategies: Dict[int, List[PitStopRequest]] = Field(..., description="Driver strategies by driver number")

class PitStopResponse(BaseModel):
    lap: int
    tire_compound: str
    pit_loss: float

class StintData(BaseModel):
    stint_number: int
    start_lap: int
    end_lap: int
    tire_compound: str
    stint_length: int

class StintComparisonData(BaseModel):
    stint_number: int
    actual_stint: Optional[StintData]
    alternative_stint: Optional[StintData]
    actual_time: float
    alternative_time: float
    time_difference: float

class StrategyComparisonResponse(BaseModel):
    driver_number: int
    driver_name: Optional[str]
    actual_strategy: List[PitStopResponse]
    alternative_strategy: List[PitStopResponse]
    actual_total_time: float
    alternative_total_time: float
    time_difference: float
    improvement: bool
    predicted_position: Optional[int] = None
    stint_comparison: Optional[List[StintComparisonData]] = None

class OptimalStrategyOption(BaseModel):
    strategy: List[PitStopResponse]
    total_time: float
    improvement: float
    rank: int

class OptimalStrategyResponse(BaseModel):
    driver_number: int
    driver_name: Optional[str]
    current_strategy: List[PitStopResponse]
    optimal_strategies: List[OptimalStrategyOption]

class TireDegradationData(BaseModel):
    compound: str
    stint_length: int
    degradation_rate: float
    average_lap_time: float
    stint_start: int

class TireDegradationResponse(BaseModel):
    driver_number: int
    driver_name: Optional[str]
    stints: List[TireDegradationData]
    avg_degradation_by_compound: Dict[str, Dict[str, float]]

class DriverInfo(BaseModel):
    driver_number: int
    name: str
    team: str
    abbreviation: str

class RaceInfo(BaseModel):
    session_key: int
    race_name: str
    total_laps: int
    drivers: List[DriverInfo]

class FieldAnalysisResponse(BaseModel):
    scenario_name: str
    driver_results: Dict[int, StrategyComparisonResponse]
    total_time_saved: float
    drivers_improved: int
    average_improvement: float

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
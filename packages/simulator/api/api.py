#!/usr/bin/env python3
"""
FastAPI application for F1 Strategy Simulator
"""

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import json
import traceback

from core.models import (
    PitStopRequest, DriverStrategyRequest, MultiDriverStrategyRequest,
    StrategyComparisonResponse, OptimalStrategyResponse, TireDegradationResponse,
    RaceInfo, FieldAnalysisResponse, ErrorResponse, DriverInfo,
    PitStopResponse, OptimalStrategyOption, TireDegradationData,
    StintData, StintComparisonData
)
from core.pit_strategy_simulator import F1StrategySimulator, PitStop
from core.strategy_analyzer import StrategyAnalyzer

# Initialize FastAPI app
app = FastAPI(
    title="F1 Strategy Simulator API",
    description="API for simulating and analyzing F1 pit strategies",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize simulator and analyzer
try:
    simulator = F1StrategySimulator()
    analyzer = StrategyAnalyzer()
except Exception as e:
    print(f"Error initializing simulator: {e}")
    simulator = None
    analyzer = None

def convert_pit_stop_to_model(pit_stop: PitStop) -> PitStopResponse:
    """Convert PitStop object to PitStopResponse model"""
    return PitStopResponse(
        lap=pit_stop.lap,
        tire_compound=pit_stop.tire_compound,
        pit_loss=pit_stop.pit_loss
    )

def convert_request_to_pit_stop(pit_request: PitStopRequest) -> PitStop:
    """Convert PitStopRequest to PitStop object"""
    return PitStop(
        lap=pit_request.lap,
        tire_compound=pit_request.tire_compound,
        pit_loss=pit_request.pit_loss
    )

def convert_stint_data(stint_dict: Dict) -> Optional[StintData]:
    """Convert stint dictionary to StintData model"""
    if stint_dict is None:
        return None
    return StintData(
        stint_number=stint_dict["stint_number"],
        start_lap=stint_dict["start_lap"],
        end_lap=stint_dict["end_lap"],
        tire_compound=stint_dict["tire_compound"],
        stint_length=stint_dict["stint_length"]
    )

def convert_stint_comparison(stint_comparison: List[Dict]) -> List[StintComparisonData]:
    """Convert stint comparison data to StintComparisonData models"""
    return [
        StintComparisonData(
            stint_number=stint["stint_number"],
            actual_stint=convert_stint_data(stint["actual_stint"]),
            alternative_stint=convert_stint_data(stint["alternative_stint"]),
            actual_time=stint["actual_time"],
            alternative_time=stint["alternative_time"],
            time_difference=stint["time_difference"]
        )
        for stint in stint_comparison
    ]

def get_driver_name(driver_number: int) -> Optional[str]:
    """Get driver name from driver number"""
    if simulator is None:
        return None
    
    driver_info = simulator.drivers_df[
        simulator.drivers_df['driver_number'] == driver_number
    ]
    
    if not driver_info.empty:
        return driver_info.iloc[0]['broadcast_name']
    return None

@app.get("/", summary="API Health Check")
async def root():
    """Health check endpoint"""
    return {
        "message": "F1 Strategy Simulator API",
        "status": "running",
        "version": "1.0.0",
        "simulator_loaded": simulator is not None
    }

@app.get("/race-info", response_model=RaceInfo, summary="Get Race Information")
async def get_race_info():
    """Get information about the loaded race"""
    if simulator is None:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        drivers = []
        for _, driver in simulator.drivers_df.iterrows():
            drivers.append(DriverInfo(
                driver_number=int(driver['driver_number']),
                name=driver['broadcast_name'],
                team=driver['team_name'],
                abbreviation=driver['name_acronym']
            ))
        
        max_lap = int(simulator.lap_times_df['lap_number'].max()) if not simulator.lap_times_df.empty else 53
        
        return RaceInfo(
            session_key=int(simulator.lap_times_df['session_key'].iloc[0]) if not simulator.lap_times_df.empty else 0,
            race_name="2024 Japan GP",
            total_laps=max_lap,
            drivers=drivers
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting race info: {str(e)}")

@app.post("/simulate-strategy", response_model=StrategyComparisonResponse, summary="Simulate Alternative Strategy")
async def simulate_strategy(request: DriverStrategyRequest):
    """Simulate an alternative pit strategy for a driver"""
    if simulator is None:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        # Convert request to PitStop objects
        alternative_strategy = [convert_request_to_pit_stop(pit) for pit in request.pit_stops]
        
        # Run comparison
        result = simulator.compare_strategies(request.driver_number, alternative_strategy)
        
        # Convert to response model
        stint_comparison = None
        if "stint_comparison" in result and result["stint_comparison"]:
            stint_comparison = convert_stint_comparison(result["stint_comparison"])
        
        return StrategyComparisonResponse(
            driver_number=request.driver_number,
            driver_name=get_driver_name(request.driver_number),
            actual_strategy=[convert_pit_stop_to_model(pit) for pit in result["actual_strategy"]],
            alternative_strategy=[convert_pit_stop_to_model(pit) for pit in result["alternative_strategy"]],
            actual_total_time=result["actual_total_time"],
            alternative_total_time=result["alternative_total_time"],
            time_difference=result["time_difference"],
            improvement=result["improvement"],
            stint_comparison=stint_comparison
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error simulating strategy: {str(e)}")

@app.get("/optimal-strategy/{driver_number}", response_model=OptimalStrategyResponse, summary="Find Optimal Strategy")
async def get_optimal_strategy(
    driver_number: int = Path(..., ge=1, le=99, description="Driver number"),
    max_stops: int = Query(2, ge=1, le=3, description="Maximum number of pit stops"),
    top_n: int = Query(5, ge=1, le=20, description="Number of top strategies to return")
):
    """Find optimal pit strategies for a driver"""
    if analyzer is None:
        raise HTTPException(status_code=500, detail="Analyzer not initialized")
    
    try:
        # Get current strategy
        current_strategy = simulator.get_actual_strategy(driver_number)
        
        # Find optimal strategies
        optimal_strategies = analyzer.find_optimal_windows(driver_number, max_stops)
        
        # Convert to response format
        optimal_options = []
        for i, strategy in enumerate(optimal_strategies[:top_n]):
            optimal_options.append(OptimalStrategyOption(
                strategy=[convert_pit_stop_to_model(pit) for pit in strategy["strategy"]],
                total_time=strategy["total_time"],
                improvement=strategy["improvement"],
                rank=i + 1
            ))
        
        return OptimalStrategyResponse(
            driver_number=driver_number,
            driver_name=get_driver_name(driver_number),
            current_strategy=[convert_pit_stop_to_model(pit) for pit in current_strategy],
            optimal_strategies=optimal_options
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error finding optimal strategy: {str(e)}")

@app.get("/tire-degradation/{driver_number}", response_model=TireDegradationResponse, summary="Analyze Tire Degradation")
async def get_tire_degradation(
    driver_number: int = Path(..., ge=1, le=99, description="Driver number")
):
    """Analyze tire degradation patterns for a driver"""
    if analyzer is None:
        raise HTTPException(status_code=500, detail="Analyzer not initialized")
    
    try:
        degradation_data = analyzer.analyze_tire_degradation(driver_number)
        
        # Convert stint data
        stints = [
            TireDegradationData(
                compound=stint["compound"],
                stint_length=stint["stint_length"],
                degradation_rate=stint["degradation_rate"],
                average_lap_time=stint["average_lap_time"],
                stint_start=stint["stint_start"]
            )
            for stint in degradation_data["stints"]
        ]
        
        return TireDegradationResponse(
            driver_number=driver_number,
            driver_name=get_driver_name(driver_number),
            stints=stints,
            avg_degradation_by_compound=degradation_data["avg_degradation_by_compound"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error analyzing tire degradation: {str(e)}")

@app.post("/field-analysis", response_model=FieldAnalysisResponse, summary="Analyze Field-Wide Strategy Changes")
async def analyze_field_strategies(request: MultiDriverStrategyRequest):
    """Analyze the impact of strategy changes across multiple drivers"""
    if simulator is None:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        # Convert request format
        strategies = {}
        for driver_num, pit_requests in request.strategies.items():
            strategies[driver_num] = [convert_request_to_pit_stop(pit) for pit in pit_requests]
        
        # Run field analysis
        results = simulator.analyze_field_impact(strategies)
        
        # Convert to response format
        driver_results = {}
        for driver_num, result in results.items():
            driver_results[driver_num] = StrategyComparisonResponse(
                driver_number=driver_num,
                driver_name=get_driver_name(driver_num),
                actual_strategy=[convert_pit_stop_to_model(pit) for pit in result["actual_strategy"]],
                alternative_strategy=[convert_pit_stop_to_model(pit) for pit in result["alternative_strategy"]],
                actual_total_time=result["actual_total_time"],
                alternative_total_time=result["alternative_total_time"],
                time_difference=result["time_difference"],
                improvement=result["improvement"],
                predicted_position=result.get("predicted_position")
            )
        
        # Calculate field statistics
        improvements = [r["time_difference"] for r in results.values()]
        total_time_saved = -sum(improvements)
        drivers_improved = sum(1 for imp in improvements if imp < 0)
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        
        return FieldAnalysisResponse(
            scenario_name="Custom Field Analysis",
            driver_results=driver_results,
            total_time_saved=total_time_saved,
            drivers_improved=drivers_improved,
            average_improvement=avg_improvement
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error analyzing field strategies: {str(e)}")

@app.get("/drivers", response_model=List[DriverInfo], summary="Get All Drivers")
async def get_drivers():
    """Get list of all drivers in the race"""
    if simulator is None:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        drivers = []
        for _, driver in simulator.drivers_df.iterrows():
            drivers.append(DriverInfo(
                driver_number=int(driver['driver_number']),
                name=driver['broadcast_name'],
                team=driver['team_name'],
                abbreviation=driver['name_acronym']
            ))
        
        return sorted(drivers, key=lambda x: x.driver_number)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting drivers: {str(e)}")

@app.get("/actual-strategy/{driver_number}", response_model=List[PitStopResponse], summary="Get Actual Strategy")
async def get_actual_strategy(
    driver_number: int = Path(..., ge=1, le=99, description="Driver number")
):
    """Get the actual pit strategy used by a driver in the race"""
    if simulator is None:
        raise HTTPException(status_code=500, detail="Simulator not initialized")
    
    try:
        actual_strategy = simulator.get_actual_strategy(driver_number)
        return [convert_pit_stop_to_model(pit) for pit in actual_strategy]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error getting actual strategy: {str(e)}")

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input", "detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
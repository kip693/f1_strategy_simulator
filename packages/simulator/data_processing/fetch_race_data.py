#!/usr/bin/env python3
"""
F1 Race Data Fetcher
Fetches race data from OpenF1 API and exports to CSV format
"""

import requests
import pandas as pd
import json
from datetime import datetime
import sys
import os

class F1DataFetcher:
    def __init__(self):
        self.base_url = "https://api.openf1.org/v1"
        
    def get_sessions(self, year=2024, country_name="Japan"):
        """Get session information for a specific race"""
        url = f"{self.base_url}/sessions"
        params = {
            "year": year,
            "country_name": country_name
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_race_session_key(self, year=2024, country_name="Japan"):
        """Get the session key for the race (not qualifying or practice)"""
        sessions = self.get_sessions(year, country_name)
        
        for session in sessions:
            if session.get("session_name") == "Race":
                return session.get("session_key")
        
        raise ValueError(f"Race session not found for {year} {country_name}")
    
    def get_drivers(self, session_key):
        """Get all drivers for a specific session"""
        url = f"{self.base_url}/drivers"
        params = {"session_key": session_key}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_lap_times(self, session_key, driver_number=None):
        """Get lap times for all drivers or specific driver"""
        url = f"{self.base_url}/laps"
        params = {"session_key": session_key}
        
        if driver_number:
            params["driver_number"] = driver_number
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_pit_stops(self, session_key):
        """Get pit stop data for the session"""
        url = f"{self.base_url}/pit"
        params = {"session_key": session_key}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_positions(self, session_key):
        """Get position data throughout the race"""
        url = f"{self.base_url}/position"
        params = {"session_key": session_key}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_stints(self, session_key):
        """Get stint data for the session"""
        url = f"{self.base_url}/stints"
        params = {"session_key": session_key}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

def fetch_and_save_race_data(year=2024, country="Japan", output_dir="data"):
    """Fetch complete race data and save to CSV files"""
    
    fetcher = F1DataFetcher()
    
    try:
        print(f"Fetching {year} {country} GP data...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get session key
        session_key = fetcher.get_race_session_key(year, country)
        print(f"Session key: {session_key}")
        
        # Get drivers
        print("Fetching drivers...")
        drivers = fetcher.get_drivers(session_key)
        drivers_df = pd.DataFrame(drivers)
        drivers_df.to_csv(f"{output_dir}/drivers.csv", index=False)
        print(f"Saved {len(drivers)} drivers to drivers.csv")
        
        # Get lap times
        print("Fetching lap times...")
        lap_times = fetcher.get_lap_times(session_key)
        lap_times_df = pd.DataFrame(lap_times)
        lap_times_df.to_csv(f"{output_dir}/lap_times.csv", index=False)
        print(f"Saved {len(lap_times)} lap times to lap_times.csv")
        
        # Get pit stops
        print("Fetching pit stops...")
        pit_stops = fetcher.get_pit_stops(session_key)
        if pit_stops:
            pit_stops_df = pd.DataFrame(pit_stops)
            pit_stops_df.to_csv(f"{output_dir}/pit_stops.csv", index=False)
            print(f"Saved {len(pit_stops)} pit stops to pit_stops.csv")
        else:
            print("No pit stop data available")
        
        # Get positions
        print("Fetching positions...")
        positions = fetcher.get_positions(session_key)
        if positions:
            positions_df = pd.DataFrame(positions)
            positions_df.to_csv(f"{output_dir}/positions.csv", index=False)
            print(f"Saved {len(positions)} position records to positions.csv")
        else:
            print("No position data available")
        
        # Get stints
        print("Fetching stints...")
        stints = fetcher.get_stints(session_key)
        if stints:
            stints_df = pd.DataFrame(stints)
            stints_df.to_csv(f"{output_dir}/stints.csv", index=False)
            print(f"Saved {len(stints)} stint records to stints.csv")
        else:
            print("No stint data available")
        
        # Save session info
        sessions = fetcher.get_sessions(year, country)
        sessions_df = pd.DataFrame(sessions)
        sessions_df.to_csv(f"{output_dir}/sessions.csv", index=False)
        print(f"Saved session info to sessions.csv")
        
        print(f"\nAll data saved to '{output_dir}' directory")
        
        # Display summary
        print("\n=== DATA SUMMARY ===")
        print(f"Drivers: {len(drivers)}")
        print(f"Lap times: {len(lap_times)}")
        print(f"Pit stops: {len(pit_stops) if pit_stops else 0}")
        print(f"Position records: {len(positions) if positions else 0}")
        print(f"Stint records: {len(stints) if stints else 0}")
        
        return {
            "session_key": session_key,
            "drivers": drivers_df,
            "lap_times": lap_times_df,
            "pit_stops": pit_stops_df if pit_stops else None,
            "positions": positions_df if positions else None,
            "stints": stints_df if stints else None,
            "sessions": sessions_df
        }
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    # Default to 2024 Japan GP as specified in the requirements
    year = 2024
    country = "Japan"
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        year = int(sys.argv[1])
    if len(sys.argv) > 2:
        country = sys.argv[2]
    
    data = fetch_and_save_race_data(year, country)
    
    if data:
        print(f"\nSuccessfully fetched and saved {year} {country} GP data!")
    else:
        print("Failed to fetch race data")
        sys.exit(1)
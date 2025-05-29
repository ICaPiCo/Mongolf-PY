import requests
import json
import math
from datetime import datetime, timedelta, timezone
from time import sleep

def get_windgram_table(location="45.5043,5.834", forecast_date=None, run_time=None):
    """
    Fetches windgram data and returns a structured table with wind data.
    
    Args:
        location (str): Location as "lat,lon"
        forecast_date (str, optional): Forecast date in YYYYMMDD format
        run_time (str, optional): Model run time in YYYYMMDD18 format
        
    Returns:
        list: Nested list structure [[[hour],[altitude],[speed],[direction]], [...]]
    """
    # Set defaults if not specified
    if run_time is None:
        run_time = get_latest_run_time()
    
    if forecast_date is None:
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        forecast_date = tomorrow.strftime('%Y%m%d')
    
    # Fetch data
    data = fetch_windgram_data(run_time, location, forecast_date)
    
    if not data or 'data' not in data:
        return []
    
    result = []
    
    # Process each hour
    hours = sorted(data['data'].keys())
    for hour in hours:
        hour_data = data['data'][hour]
        
        # Get height levels and wind components
        z_levels = hour_data.get('z', [])
        u_wind = hour_data.get('umet', [])
        v_wind = hour_data.get('vmet', [])
        
        if not z_levels or not u_wind or not v_wind:
            continue
            
        # Create a record for this hour
        hour_altitudes = []
        hour_speeds = []
        hour_directions = []
        
        for i in range(len(z_levels)):
            if i < len(u_wind) and i < len(v_wind):
                altitude = z_levels[i]
                u = u_wind[i]
                v = v_wind[i]
                
                # Calculate wind speed and direction
                speed = ((u**2 + v**2)**0.5) * 3.6  # m/s to km/h
                direction = (270 - math.degrees(math.atan2(v, u))) % 360
                
                hour_altitudes.append(altitude)
                hour_speeds.append(round(speed, 1))
                hour_directions.append(round(direction, 1))
        
        # Only add if we have data
        if hour_altitudes:
            result.append([[hour], hour_altitudes, hour_speeds, hour_directions])
    
    return result

def get_latest_run_time():
    """Determines the latest available model run time."""
    now = datetime.now(timezone.utc)
    # Use 18Z run from yesterday or day before yesterday based on current time
    run_date = now.date() - timedelta(days=1 if now.hour >= 20 else 2)
    return run_date.strftime('%Y%m%d') + '18'

def fetch_windgram_data(run_time, location, forecast_date):
    """Fetches windgram data for specified parameters."""
    url = "https://data0.meteo-parapente.com/data.php"
    
    # Try both parameter sets that might work
    params_options = [
        {'run': run_time, 'location': location, 'date': forecast_date, 'plot': 'windgram', 'format': 'json'},
        {'run': run_time, 'location': location, 'date': forecast_date, 'type': 'windgram', 'mode': 'data'}
    ]
    
    for params in params_options:
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    continue
        except requests.exceptions.RequestException:
            continue
    
    return None

def get_grid_weather_data(grid_size=8):
    """
    Creates a grid of weather data points and returns both the weather data and grid positions.
    
    Args:
        grid_size (int): Size of the grid (grid_size x grid_size)
        
    Returns:
        tuple: (fullWeather, fullPositions) containing weather data and coordinates
    """
    # Starting coordinates (upper left corner)
    start_lat = 68.841464
    start_lon = -33.214573
    
    # Grid increments (based on comments in original code)
    lon_increment = 0.2803271796875  # approx 8.97° per 32 grid points
    lat_increment = 0.1721861015625  # approx 5.51° per 32 grid points
    
    fullWeather = []
    fullPositions = []
    
    print(f"Fetching weather data for {grid_size}x{grid_size} grid...")
    
    # Loop through the grid
    for row in range(grid_size):
        curr_lat = start_lat - (lat_increment * row)
        
        for col in range(grid_size):
            curr_lon = start_lon + (lon_increment * col)
            
            # Format location string and get weather data
            location = f"{curr_lat},{curr_lon}"
            print(f"Fetching data for position {row+1},{col+1}: {location}")
            
            # Get weather data for this position
            weather_data = get_windgram_table(location)
            
            # Add to our result lists
            fullWeather.append(weather_data)
            fullPositions.append([curr_lat, curr_lon])
            
            # Small delay to avoid overwhelming the API
            sleep(1)
    
    return fullWeather, fullPositions

# Example usage:
if __name__ == "__main__":
    # Get weather data for a single location
    # wind_data = get_windgram_table()
    # print(wind_data)
    
    # Or get weather data for a grid of locations
    weather_grid, positions_grid = get_grid_weather_data(grid_size=8)
    print(f"Collected weather data for {len(weather_grid)} locations")
    print(f"First position: {positions_grid[0]}")
    print(f"First weather data sample: {weather_grid[0][:1]}")  # Show just first hour for first location
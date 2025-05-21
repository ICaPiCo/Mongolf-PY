"""
Meteo-Parapente Windgram Data Fetcher

This script fetches and displays wind data from Meteo-Parapente's API, focusing on wind speed
and direction at different altitudes, as well as cloud cover and other meteorological data.

The script can be used to get forecasts for paragliding or other weather-dependent activities.
"""

import requests
import json
import math
from datetime import datetime, timedelta, timezone
import argparse


def get_latest_run_time():
    """
    Determines the latest available model run time.
    
    Meteo-Parapente updates their models at specific times of the day (18Z run).
    This function calculates which run is likely to be available based on current time.
    
    Returns:
        str: Date string in format 'YYYYMMDD18' representing the run time
    """
    now = datetime.now(timezone.utc)
    # Use 18Z run from yesterday or day before yesterday based on current time
    run_date = now.date() - timedelta(days=1 if now.hour >= 20 else 2)
    return run_date.strftime('%Y%m%d') + '18'


def fetch_windgram_data(run_time, location, forecast_date):
    """
    Fetches windgram data from Meteo-Parapente API for specified parameters.
    
    Args:
        run_time (str): Model run time (format: YYYYMMDD18)
        location (str): Location coordinates as "lat,lon"
        forecast_date (str): Date for forecast (format: YYYYMMDD)
    
    Returns:
        dict: JSON data from API or None if request fails
    """
    url = "https://data0.meteo-parapente.com/data.php"
    
    # Try both parameter sets that might work (API might have different parameter formats)
    params_options = [
        {'run': run_time, 'location': location, 'date': forecast_date, 'plot': 'windgram', 'format': 'json'},
        {'run': run_time, 'location': location, 'date': forecast_date, 'type': 'windgram', 'mode': 'data'}
    ]
    
    print(f"Requesting data for run: {run_time}, location: {location}, date: {forecast_date}")
    
    # Try each parameter option until one works
    for params in params_options:
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    continue  # Try next parameter set if JSON parsing fails
        except requests.exceptions.RequestException:
            continue  # Try next parameter set if request fails
    
    print("Failed to retrieve data")
    return None


def get_wind_arrow(degrees):
    """
    Returns an arrow character representing wind direction.
    
    Args:
        degrees (float): Wind direction in meteorological degrees (0=N, 90=E, etc.)
    
    Returns:
        str: Arrow character pointing in the direction the wind is coming FROM
    """
    arrows = {0: "↓", 45: "↙", 90: "←", 135: "↖", 180: "↑", 225: "↗", 270: "→", 315: "↘"}
    closest = min(arrows.keys(), key=lambda x: abs((degrees - x + 180) % 360 - 180))
    return arrows[closest]


def format_windgram_data(data):
    """
    Formats the windgram data for display in a readable text format.
    
    Args:
        data (dict): JSON data from Meteo-Parapente API
    
    Returns:
        str: Formatted string representation of the data
    """
    if not data:
        return "No data to display"
    
    output = []
    output.append("===== METEO-PARAPENTE WINDGRAM DATA =====")
    
    # Location info
    if 'gridCoords' in data:
        grid = data['gridCoords']
        output.append(f"\nLOCATION: {grid.get('lat', 'Unknown')}, {grid.get('lon', 'Unknown')}")
    
    # Process hourly data
    if 'data' in data and isinstance(data['data'], dict):
        hours = sorted(data['data'].keys())  # Sort hours chronologically
        
        if hours:
            output.append("\nHOURLY FORECAST DATA:")
            
            # Create header for wind table
            header = "Hour     "
            levels = [0, 500, 1000, 1500, 2000, 2500, 3000]  # Altitude levels in meters
            for level in levels:
                header += f"| {level}m         "
            header += "| Rain  | PBL"  # PBL = Planetary Boundary Layer
            output.append(header)
            output.append("-" * len(header))
            
            # Process each hour's data
            for hour in hours:
                hour_data = data['data'][hour]
                
                # Get height levels and wind components
                z_levels = hour_data.get('z', [])  # Altitude levels
                u_wind = hour_data.get('umet', [])  # West-East component (u)
                v_wind = hour_data.get('vmet', [])  # South-North component (v)
                
                row = f"{hour:<8}"
                
                # Add wind for levels of interest
                if z_levels and u_wind and v_wind:
                    for target_height in levels:
                        # Find closest height level to our target
                        if not z_levels:
                            row += "| N/A           "
                            continue
                            
                        closest_idx = min(range(len(z_levels)), key=lambda i: abs(z_levels[i] - target_height))
                        
                        if closest_idx < len(u_wind) and closest_idx < len(v_wind):
                            u = u_wind[closest_idx]
                            v = v_wind[closest_idx]
                            
                            # Calculate wind speed and direction
                            speed = ((u**2 + v**2)**0.5) * 3.6  # Convert m/s to km/h
                            direction = (270 - math.degrees(math.atan2(v, u))) % 360  # Calculate meteorological direction
                            arrow = get_wind_arrow(direction)
                            
                            row += f"| {speed:.1f}km/h {arrow:<3} "
                        else:
                            row += "| N/A           "
                else:
                    for _ in levels:
                        row += "| N/A           "
                
                # Add precipitation and PBL height
                rain = hour_data.get('raintot', 0)  # Total precipitation
                pbl = hour_data.get('pblh', 0)      # Planetary Boundary Layer height
                row += f"| {rain:.1f}mm | {pbl:.0f}m"
                output.append(row)
            
            # Add cloud cover section if data available
            cloud_data = []
            for hour in hours:
                hour_data = data['data'][hour]
                if 'cfrach' in hour_data or 'cfracl' in hour_data or 'cfracm' in hour_data:
                    low = hour_data.get('cfracl', 0)   # Low cloud cover fraction
                    mid = hour_data.get('cfracm', 0)   # Medium cloud cover fraction
                    high = hour_data.get('cfrach', 0)  # High cloud cover fraction
                    cloud_data.append((hour, low, mid, high))
            
            if cloud_data:
                output.append("\nCLOUD COVER:")
                header = f"{'Hour':<8} | {'Low':<8} | {'Mid':<8} | {'High':<8} | {'Total':<8}"
                output.append(header)
                output.append("-" * len(header))
                
                for hour, low, mid, high in cloud_data:
                    total = min(10, low + mid + high)  # Cap total cloud cover at 10/10
                    row = f"{hour:<8} | {low:<8.1f} | {mid:<8.1f} | {high:<8.1f} | {total:<8.1f}"
                    output.append(row)
    
    output.append("\n=========================================")
    return "\n".join(output)


def extract_wind_vectors(hour_data):
    """
    Extracts wind speeds and directions from a single hour's data.
    
    Args:
        hour_data (dict): Data for a specific hour from the API
        
    Returns:
        tuple: Two lists containing wind speeds (km/h) and directions (degrees)
    """
    z = hour_data.get('z', [])      # Height levels
    u = hour_data.get('umet', [])   # West-East component
    v = hour_data.get('vmet', [])   # South-North component
    
    wind_speeds = []
    wind_dirs = []

    for i in range(min(len(z), len(u), len(v))):
        speed = (u[i]**2 + v[i]**2)**0.5 * 3.6  # Convert m/s to km/h
        direction = (270 - math.degrees(math.atan2(v[i], u[i]))) % 360  # Meteorological direction

        wind_speeds.append(speed)
        wind_dirs.append(direction)

    return wind_speeds, wind_dirs


def extract_wind_data(data, altitude=None):
    """
    Extracts organized wind data for all hours at specified altitude or all altitudes.
    
    Args:
        data (dict): JSON data from Meteo-Parapente API
        altitude (float, optional): Target altitude in meters. If None, returns data for all altitudes.
    
    Returns:
        dict: Dictionary with keys: 'hours', 'altitudes', 'speeds', 'directions'
              Each containing lists of corresponding data points.
              
              If altitude is specified, returns simpler dict with keys:
              'hours', 'speeds', 'directions' for that altitude only.
    """
    if not data or 'data' not in data:
        return None
    
    result = {
        'hours': [],
        'altitudes': [],
        'speeds': [],
        'directions': []
    }
    
    # If specific altitude requested, simplify the result structure
    if altitude is not None:
        result = {
            'hours': [],
            'speeds': [],
            'directions': []
        }
    
    # Sort hours chronologically
    hours = sorted(data['data'].keys())
    
    for hour in hours:
        hour_data = data['data'][hour]
        
        # Get height levels and wind components
        z_levels = hour_data.get('z', [])
        u_wind = hour_data.get('umet', [])
        v_wind = hour_data.get('vmet', [])
        
        # Skip if missing data
        if not z_levels or not u_wind or not v_wind:
            continue
        
        # If specific altitude requested, find closest data point
        if altitude is not None:
            if not z_levels:
                continue
                
            closest_idx = min(range(len(z_levels)), key=lambda i: abs(z_levels[i] - altitude))
            
            if closest_idx < len(u_wind) and closest_idx < len(v_wind):
                u = u_wind[closest_idx]
                v = v_wind[closest_idx]
                
                # Calculate wind speed and direction
                speed = ((u**2 + v**2)**0.5) * 3.6  # m/s to km/h
                direction = (270 - math.degrees(math.atan2(v, u))) % 360
                
                result['hours'].append(hour)
                result['speeds'].append(speed)
                result['directions'].append(direction)
        else:
            # Add all altitudes and corresponding wind data
            speeds, directions = extract_wind_vectors(hour_data)
            
            result['hours'].append(hour)
            result['altitudes'].append(z_levels)
            result['speeds'].append(speeds)
            result['directions'].append(directions)
    
    return result


def main():
    """
    Main function to process command line arguments and execute the program.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fetch windgram data from Meteo-Parapente')
    parser.add_argument('--location', default="45.5043,5.834", help='Location as "lat,lon"')
    parser.add_argument('--date', help='Forecast date (YYYYMMDD)')
    parser.add_argument('--run', help='Model run time (YYYYMMDD18)')
    parser.add_argument('--save', action='store_true', help='Save raw JSON data')
    parser.add_argument('--raw', action='store_true', help='Display raw JSON')
    
    args = parser.parse_args()
    
    # Set defaults if not specified
    location = args.location
    run_time = args.run if args.run else get_latest_run_time()
    
    if args.date:
        forecast_date = args.date
    else:
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        forecast_date = tomorrow.strftime('%Y%m%d')
    
    # Fetch and process data
    data = fetch_windgram_data(run_time, location, forecast_date)
    
    if data:
        # Save JSON if requested
        if args.save:
            filename = f"windgram_{location.replace(',', '_')}_{forecast_date}.json"
            try:
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"Data saved to {filename}")
            except Exception as e:
                print(f"Error saving data: {e}")
        
        # Display data
        if args.raw:
            print("\n===== RAW JSON =====")
            print(json.dumps(data, indent=2)[:2000] + "..." if len(json.dumps(data, indent=2)) > 2000 else json.dumps(data, indent=2))
        else:
            print("\n" + format_windgram_data(data))
    else:
        print("\nNo data retrieved. Please check your inputs and connection.")


if __name__ == "__main__":
    main()
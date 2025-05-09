import requests
import json
import math
from datetime import datetime, timedelta, timezone
import argparse

def get_latest_run_time():
    """
    Determines the latest available model run time.
    Meteo-Parapente provides runs at 00Z, 06Z, 12Z, and 18Z.
    """
    now = datetime.now(timezone.utc)
    
    # Based on observed patterns, we'll use the most recent available run
    # If current time is before 20:00 UTC, use the 18Z run from the day before yesterday
    # Otherwise use the 18Z run from yesterday
    if now.hour < 20:
        run_date = now.date() - timedelta(days=2)
    else:
        run_date = now.date() - timedelta(days=1)
    
    # Format as YYYYMMDD18 (using 18Z run)
    return run_date.strftime('%Y%m%d') + '18'

def fetch_windgram_data(run_time, location, forecast_date):
    """
    Fetches windgram data in JSON format for the specified parameters.
    
    Args:
        run_time (str): Model run time in format YYYYMMDD18
        location (str): Location coordinates in format "lat,lon"
        forecast_date (str): Forecast date in format YYYYMMDD
        
    Returns:
        dict: JSON data or None if request fails
    """
    base_url = "https://data0.meteo-parapente.com/data.php"
    
    # Try both parameter sets to see which one works
    parameter_sets = [
        # First attempt - using 'plot' and 'format'
        {
            'run': run_time,
            'location': location,
            'date': forecast_date,
            'plot': 'windgram',
            'format': 'json'
        },
        # Second attempt - using 'type' and 'mode'
        {
            'run': run_time,
            'location': location,
            'date': forecast_date,
            'type': 'windgram',
            'mode': 'data'
        }
    ]
    
    print(f"Requesting data with parameters:")
    print(f"- Run time: {run_time}")
    print(f"- Location: {location}")
    print(f"- Forecast date: {forecast_date}")
    
    for i, params in enumerate(parameter_sets):
        try:
            print(f"\nAttempt {i+1}:")
            # Print the full URL for debugging
            request = requests.Request('GET', base_url, params=params)
            prepared_request = request.prepare()
            print(f"Full URL: {prepared_request.url}")
            
            # Make request with timeout
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                content_length = len(response.content)
                print(f"Response received - Content-Type: {content_type}, Length: {content_length} bytes")
                
                try:
                    # Try to parse as JSON
                    data = response.json()
                    print("JSON data successfully retrieved!")
                    return data
                except json.JSONDecodeError:
                    print("Response not valid JSON. First 100 characters:")
                    print(response.text[:100] + "..." if len(response.text) > 100 else response.text)
            else:
                print(f"Request failed with status code: {response.status_code}")
                print(f"Response: {response.text[:200]}..." if response.text else "No text response")
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
    
    print("\nAll attempts failed to get JSON data")
    return None

def format_windgram_data(data):
    """
    Formats the windgram data for display.
    
    Args:
        data (dict): The JSON data from the API
        
    Returns:
        str: Formatted string representation of the data
    """
    if not data:
        return "No data to display"
    
    output = []
    output.append("===== METEO-PARAPENTE WINDGRAM DATA =====")
    
    # Print location information from gridCoords
    if 'gridCoords' in data:
        grid = data['gridCoords']
        output.append("\nLOCATION:")
        output.append(f"Coordinates: {grid.get('lat', 'Unknown')}, {grid.get('lon', 'Unknown')}")
        output.append(f"Grid: domain={grid.get('domain', 'Unknown')}, sn={grid.get('sn', 'Unknown')}, we={grid.get('we', 'Unknown')}")
        if 'latDiff' in grid or 'lonDiff' in grid:
            output.append(f"Offset: latDiff={grid.get('latDiff', 0)}, lonDiff={grid.get('lonDiff', 0)}")
    
    # Add timestamp if available
    if 'time' in data:
        # Convert Unix timestamp to readable date if it looks like a timestamp
        try:
            if isinstance(data['time'], (int, float)) and data['time'] > 1000000000:
                timestamp = datetime.fromtimestamp(data['time'], timezone.utc)
                output.append(f"\nData timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            else:
                output.append(f"\nTimestamp: {data['time']}")
        except:
            output.append(f"\nTimestamp: {data['time']}")
    
    # Print status if available
    if 'status' in data:
        output.append(f"Status: {data['status']}")
    
    # Process hourly data
    if 'data' in data and isinstance(data['data'], dict):
        hourly_data = data['data']
        
        # Sort hours for consistent display
        hours = sorted(hourly_data.keys())
        
        if hours:
            output.append("\nHOURLY FORECAST DATA:")
            
            # Extract wind data for each hour
            wind_table = []
            for hour in hours:
                hour_data = hourly_data[hour]
                
                # Get the height levels
                z_levels = hour_data.get('z', [])
                
                # Get wind components
                u_wind = hour_data.get('umet', [])
                v_wind = hour_data.get('vmet', [])
                
                # Calculate wind speed and direction for specific levels
                wind_info = []
                
                if z_levels and u_wind and v_wind:
                    # Define height levels of interest (in meters)
                    levels_of_interest = [0, 500, 1000, 1500, 2000, 2500, 3000]
                    
                    for target_height in levels_of_interest:
                        # Find the closest height level
                        closest_idx = min(range(len(z_levels)), key=lambda i: abs(z_levels[i] - target_height))
                        
                        if closest_idx < len(u_wind) and closest_idx < len(v_wind):
                            u = u_wind[closest_idx]
                            v = v_wind[closest_idx]
                            
                            # Calculate wind speed (convert to km/h)
                            speed = ((u**2 + v**2)**0.5) * 3.6  # Convert m/s to km/h
                            
                            # Calculate wind direction (meteorological convention)
                            direction = (270 - math.degrees(math.atan2(v, u))) % 360
                            
                            wind_info.append((target_height, speed, direction))
                
                # Add precipitation if available
                rain = hour_data.get('raintot', 0)
                
                # Add PBL height if available
                pbl = hour_data.get('pblh', 0)
                
                wind_table.append((hour, wind_info, rain, pbl))
            
            # Display the wind table
            if wind_table:
                # First, format the header
                header = "Hour     "
                for level in [0, 500, 1000, 1500, 2000, 2500, 3000]:
                    header += f"| {level}m         "
                header += "| Rain  | PBL"
                output.append(header)
                
                separator = "-" * len(header)
                output.append(separator)
                
                # Then format each row
                for hour, wind_info, rain, pbl in wind_table:
                    row = f"{hour:<8}"
                    
                    # Add wind for each level
                    for target_height, speed, direction in wind_info:
                        direction_arrow = get_wind_direction_arrow(direction)
                        row += f"| {speed:.1f}km/h {direction_arrow:<3} "
                    
                    # If some levels were missing, add empty cells
                    for _ in range(7 - len(wind_info)):
                        row += "| N/A           "
                    
                    # Add rain and PBL
                    row += f"| {rain:.1f}mm | {pbl:.0f}m"
                    output.append(row)
        
        # If we have cloud data, create a cloud cover section
        cloud_data = []
        for hour in hours:
            hour_data = hourly_data[hour]
            if 'cfrach' in hour_data or 'cfracl' in hour_data or 'cfracm' in hour_data:
                low = hour_data.get('cfracl', 0)
                mid = hour_data.get('cfracm', 0)
                high = hour_data.get('cfrach', 0)
                cloud_data.append((hour, low, mid, high))
        
        if cloud_data:
            output.append("\nCLOUD COVER:")
            header = f"{'Hour':<8} | {'Low':<8} | {'Mid':<8} | {'High':<8} | {'Total':<8}"
            output.append(header)
            output.append("-" * len(header))
            
            for hour, low, mid, high in cloud_data:
                total = min(10, low + mid + high)  # Cap at 10/10
                row = f"{hour:<8} | {low:<8.1f} | {mid:<8.1f} | {high:<8.1f} | {total:<8.1f}"
                output.append(row)
    
    output.append("\n=========================================")
    return "\n".join(output)

def get_wind_direction_arrow(degrees):
    """
    Returns an arrow character representing wind direction.
    Wind direction is where the wind is coming FROM.
    
    Args:
        degrees: Wind direction in degrees (meteorological convention)
        
    Returns:
        str: Arrow character pointing in wind direction
    """
    # Define 8 arrow directions
    arrows = {
        0: "↓",    # N wind (comes from North, blows South)
        45: "↙",   # NE wind
        90: "←",   # E wind
        135: "↖",  # SE wind
        180: "↑",  # S wind
        225: "↗",  # SW wind
        270: "→",  # W wind
        315: "↘",  # NW wind
    }
    
    # Find closest direction
    closest = min(arrows.keys(), key=lambda x: abs((degrees - x + 180) % 360 - 180))
    return arrows[closest]

def save_json_data(data, filename):
    """
    Saves the JSON data to a file for later analysis.
    """
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Fetch windgram data from Meteo-Parapente')
    parser.add_argument('--location', default="45.5043,5.834", 
                        help='Location coordinates as "lat,lon" (default: 45.5043,5.834 - near Grenoble, France)')
    parser.add_argument('--date', 
                        help='Forecast date in YYYYMMDD format (default: tomorrow)')
    parser.add_argument('--run', 
                        help='Model run time in YYYYMMDD18 format (default: auto-detect latest run)')
    parser.add_argument('--save', action='store_true', 
                        help='Save raw JSON data to file')
    parser.add_argument('--raw', action='store_true',
                        help='Display raw JSON structure instead of formatted data')
    parser.add_argument('--debug', action='store_true',
                        help='Print detailed debug information')
    
    args = parser.parse_args()
    
    # Process arguments
    location = args.location
    
    # Get tomorrow's date if not specified
    if args.date:
        forecast_date = args.date
    else:
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        forecast_date = tomorrow.strftime('%Y%m%d')
    
    # Get latest model run time if not specified
    run_time = args.run if args.run else get_latest_run_time()
    print(f"Using run time: {run_time}")
    
    # Fetch JSON data
    print("\n--- Fetching windgram data ---")
    data = fetch_windgram_data(run_time, location, forecast_date)
    
    # Process the results
    if data:
        # Save raw JSON if requested
        if args.save:
            filename = f"windgram_{location.replace(',', '_')}_{forecast_date}.json"
            save_json_data(data, filename)
        
        # Display the data
        if args.raw:
            print("\n===== RAW JSON STRUCTURE =====")
            print(json.dumps(data, indent=2)[:4000] + "..." if len(json.dumps(data, indent=2)) > 4000 else json.dumps(data, indent=2))
            print("\n(Limited to first 4000 characters)")
        elif args.debug:
            # Print detailed structure
            print("\n===== JSON STRUCTURE DETAILS =====")
            def print_structure(obj, prefix="", max_depth=3, current_depth=0):
                if current_depth >= max_depth:
                    return
                
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if isinstance(v, (dict, list)):
                            print(f"{prefix}{k}: {type(v).__name__} with {len(v)} items")
                            print_structure(v, prefix + "  ", max_depth, current_depth + 1)
                        else:
                            print(f"{prefix}{k}: {type(v).__name__} = {v}")
                elif isinstance(obj, list) and len(obj) > 0:
                    print(f"{prefix}List with {len(obj)} items, first item type: {type(obj[0]).__name__}")
                    if len(obj) > 0:
                        if isinstance(obj[0], (dict, list)):
                            print_structure(obj[0], prefix + "  ", max_depth, current_depth + 1)
                        else:
                            print(f"{prefix}  Sample: {obj[0]}")
            
            print_structure(data)
            
            # Then print normal formatted data
            print("\n" + format_windgram_data(data))
        else:
            print("\n" + format_windgram_data(data))
    else:
        print("\nNo data could be retrieved. Please try:")
        print("1. Checking your internet connection")
        print("2. Verifying the location coordinates are valid")
        print("3. Trying a different run time or forecast date")
        print("4. Visiting the Meteo-Parapente website directly")

if __name__ == "__main__":
    main()
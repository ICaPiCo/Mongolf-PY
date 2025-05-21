import requests
import json
import math
from datetime import datetime, timedelta, timezone
import argparse

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
    
    print(f"Requesting data for run: {run_time}, location: {location}, date: {forecast_date}")
    
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
    
    print("Failed to retrieve data")
    return None

def get_wind_arrow(degrees):
    """Returns an arrow character representing wind direction."""
    arrows = {0: "↓", 45: "↙", 90: "←", 135: "↖", 180: "↑", 225: "↗", 270: "→", 315: "↘"}
    closest = min(arrows.keys(), key=lambda x: abs((degrees - x + 180) % 360 - 180))
    return arrows[closest]

def format_windgram_data(data):
    """Formats the windgram data for display."""
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
        hours = sorted(data['data'].keys())
        
        if hours:
            output.append("\nHOURLY FORECAST DATA:")
            
            # Create header for wind table
            header = "Hour     "
            levels = [0, 500, 1000, 1500, 2000, 2500, 3000]
            for level in levels:
                header += f"| {level}m         "
            header += "| Rain  | PBL"
            output.append(header)
            output.append("-" * len(header))
            
            # Process each hour
            for hour in hours:
                hour_data = data['data'][hour]
                
                # Get height levels and wind components
                z_levels = hour_data.get('z', [])
                u_wind = hour_data.get('umet', [])
                v_wind = hour_data.get('vmet', [])
                
                row = f"{hour:<8}"
                
                # Add wind for levels of interest
                if z_levels and u_wind and v_wind:
                    for target_height in levels:
                        # Find closest height level
                        if not z_levels:
                            row += "| N/A           "
                            continue
                            
                        closest_idx = min(range(len(z_levels)), key=lambda i: abs(z_levels[i] - target_height))
                        
                        if closest_idx < len(u_wind) and closest_idx < len(v_wind):
                            u = u_wind[closest_idx]
                            v = v_wind[closest_idx]
                            
                            # Calculate wind speed and direction
                            speed = ((u**2 + v**2)**0.5) * 3.6  # m/s to km/h
                            direction = (270 - math.degrees(math.atan2(v, u))) % 360
                            arrow = get_wind_arrow(direction)
                            
                            row += f"| {speed:.1f}km/h {arrow:<3} "
                        else:
                            row += "| N/A           "
                else:
                    for _ in levels:
                        row += "| N/A           "
                
                # Add rain and PBL
                rain = hour_data.get('raintot', 0)
                pbl = hour_data.get('pblh', 0)
                row += f"| {rain:.1f}mm | {pbl:.0f}m"
                output.append(row)
            
            # Add cloud cover section if data available
            cloud_data = []
            for hour in hours:
                hour_data = data['data'][hour]
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

def main():
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
# we need to sort data into lists for speed, lists for dir, with same indexes
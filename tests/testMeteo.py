import requests
import json
import math
from datetime import datetime, timedelta, timezone
from time import sleep

fullWeather=[]
fullPositions=[]
lat=68.841464
lon=-33.214573

def get_windgram_table(location="45.5043,5.834", forecast_date=None, run_time=None, debug=False):
    """
    Fetches windgram data and returns a structured table with wind data.
    
    Args:
        location (str): Location as "lat,lon"
        forecast_date (str, optional): Forecast date in YYYYMMDD format
        run_time (str, optional): Model run time in YYYYMMDD18 format
        debug (bool): Print debug information
        
    Returns:
        list: Nested list structure [[[hour],[altitude],[speed],[direction]], [...]]
    """
    # Set defaults if not specified
    if run_time is None:
        run_time = get_latest_run_time()
    
    if forecast_date is None:
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        forecast_date = tomorrow.strftime('%Y%m%d')
    
    if debug:
        print(f"Requesting data for location: {location}, date: {forecast_date}, run: {run_time}")
    
    # Fetch data
    data = fetch_windgram_data(run_time, location, forecast_date, debug=debug)
    
    if not data:
        if debug:
            print("No data returned from API")
        return []
    
    if debug:
        print(f"Raw data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        if isinstance(data, dict):
            if 'error' in data:
                print(f"API Error: {data['error']}")
            if 'data' in data:
                print(f"Data structure keys: {list(data['data'].keys())[:5]}...")  # Show first 5 keys
    
    if 'data' not in data:
        if debug:
            print("'data' key not found in response")
            if isinstance(data, dict) and 'error' in data:
                print(f"Error message: {data['error']}")
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
    # Try different run times - sometimes data isn't available for the latest run
    possible_runs = []
    
    # Try different days and different run times (00Z, 06Z, 12Z, 18Z)
    for days_back in range(1, 4):  # Try 1-3 days back
        run_date = now.date() - timedelta(days=days_back)
        for run_hour in ['18', '12', '06', '00']:
            possible_runs.append(run_date.strftime('%Y%m%d') + run_hour)
    
    return possible_runs[0]  # Return the first one for now, but we'll try multiple

def fetch_windgram_data(run_time, location, forecast_date, debug=False):
    """Fetches windgram data for specified parameters."""
    url = "https://data0.meteo-parapente.com/data.php"
    
    # Try both parameter sets that might work
    params_options = [
        {'run': run_time, 'location': location, 'date': forecast_date, 'plot': 'windgram', 'format': 'json'},
        {'run': run_time, 'location': location, 'date': forecast_date, 'type': 'windgram', 'mode': 'data'},
        {'run': run_time, 'lat': location.split(',')[0], 'lon': location.split(',')[1], 'date': forecast_date, 'plot': 'windgram'},
        {'model': 'gfs', 'run': run_time, 'location': location, 'date': forecast_date, 'type': 'windgram'},
        # Try with different model names
        {'model': 'gfs25', 'run': run_time, 'location': location, 'date': forecast_date, 'plot': 'windgram', 'format': 'json'},
        {'model': 'ecmwf', 'run': run_time, 'location': location, 'date': forecast_date, 'plot': 'windgram', 'format': 'json'},
    ]
    
    # If we have run_time issues, try multiple run times    
    if debug and 'error' in str(run_time).lower():
        print("Trying multiple run times...")
        now = datetime.now(timezone.utc)
        for days_back in range(1, 4):
            for run_hour in ['18', '12', '06', '00']:
                alt_run_time = (now.date() - timedelta(days=days_back)).strftime('%Y%m%d') + run_hour
                params_options.append({'run': alt_run_time, 'location': location, 'date': forecast_date, 'plot': 'windgram', 'format': 'json'})
    
    for i, params in enumerate(params_options):
        try:
            if debug:
                print(f"Trying parameter set {i+1}: {params}")
            
            response = requests.get(url, params=params, timeout=30)
            
            if debug:
                print(f"Response status: {response.status_code}")
                print(f"Response content length: {len(response.content)}")
                if response.status_code != 200:
                    print(f"Response text: {response.text[:200]}...")
            
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    if debug:
                        print(f"Successfully parsed JSON with keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dict'}")
                        if isinstance(json_data, dict) and 'error' in json_data:
                            print(f"API returned error: {json_data['error']}")
                        if isinstance(json_data, dict) and 'data' in json_data:
                            print(f"SUCCESS: Found data key!")
                            return json_data
                    
                    # Only return if it actually has data, not just an error
                    if isinstance(json_data, dict) and 'data' in json_data:
                        return json_data
                        
                except json.JSONDecodeError as e:
                    if debug:
                        print(f"JSON decode error: {e}")
                        print(f"Response text: {response.text[:500]}...")
                    continue
        except requests.exceptions.RequestException as e:
            if debug:
                print(f"Request error: {e}")
            continue
    
    if debug:
        print("All parameter sets failed")
    return None

def save_data_to_files(weather_data, positions_data, weather_filename="weather_data.json", positions_filename="positions_data.json"):
    """
    Save weather and positions data to separate JSON files.
    
    Args:
        weather_data (list): The fullWeather data
        positions_data (list): The fullPositions data
        weather_filename (str): Filename for weather data
        positions_filename (str): Filename for positions data
    """
    try:
        # Save weather data
        with open(weather_filename, 'w') as f:
            json.dump(weather_data, f, indent=2)
        print(f"Weather data saved to {weather_filename}")
        
        # Save positions data
        with open(positions_filename, 'w') as f:
            json.dump(positions_data, f, indent=2)
        print(f"Positions data saved to {positions_filename}")
        
    except Exception as e:
        print(f"Error saving data: {e}")

# Example usage:
if __name__ == "__main__":
    wind_data = get_windgram_table()
    print(wind_data)

#[[[hour],[altitude],[speed],[direction]],[[hour],[altitude],[speed],[direction]]]
#4950km
#68.732386, 38.549185 (up right)
#24.707283, 37.255776 (bottom right)
#68.841464, -33.214573 (up left)

#right to left = 0; -33.214573 -> 38.549185 -> <-> 71,763758 = 7950km = 256px longitude 1px = 0,2803271796875°
#up to down = 68.786925 -> 24.707283 -> 44,079642 <->  = 7950km = 256px latitude 1px = 0,1721861015625°
# longitude = 0,2803271796875 * 32 = 8,9704
# latitude = 0,1721861015625 * 32 = 5,51

print("Starting data collection...")

# Test with the first position to see what's happening
test_lat = 68.841464
test_lon = -33.214573 + 0.2803271796875 * (0-1)
print(f"Testing with first position: lat={test_lat:.6f}, lon={test_lon:.6f}")
test_weather = get_windgram_table(f"{test_lat},{test_lon}", debug=True)
print(f"Test result length: {len(test_weather)}")
if test_weather:
    print(f"Sample data: {test_weather[0] if test_weather else 'No data'}")

print("\nStarting full data collection...")
for y in range(8):
    for i in range(8):
        lon = -33.214573 + 0.2803271796875 * (i-1)
        print(f"Fetching data for position {len(fullPositions) + 1}/64: lat={lat:.6f}, lon={lon:.6f}")
        
        weather = get_windgram_table(f"{lat},{lon}")
        fullWeather.append(weather)
        fullPositions.append([lat, lon])
        
        # Add more info about the result
        if weather:
            print(f"  -> Got {len(weather)} time periods")
        else:
            print(f"  -> No data returned")
        
        # Optional: Add a small delay to be respectful to the API
        sleep(0.5)
        
    lat = 68.841464 - 0.1721861015625 * (y+1)  # Fixed the indexing issue

print("Data collection complete!")
print(f"Collected data for {len(fullPositions)} positions")

# Save the collected data to files
save_data_to_files(fullWeather, fullPositions)

print("All data saved to files successfully!")
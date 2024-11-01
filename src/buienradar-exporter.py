import time
import logging
from prometheus_client import Counter, Gauge, start_http_server
import requests
from datetime import datetime
import os

# Define the port
PORT = 9002

# Initialize the Prometheus metrics dictionary
prometheus_gauges = {}
error_count = Counter('buienradar_api_errors_total', 'The number of errors encountered while accessing the Buienradar API')

# Get proxy settings from environment variables
HTTP_PROXY = os.getenv('HTTP_PROXY')
HTTPS_PROXY = os.getenv('HTTPS_PROXY')

PROXIES = {
    'http': HTTP_PROXY,
    'https': HTTPS_PROXY
}

def buienradar_current_data():
    """Fetch current data from Buienradar and yield formatted station data."""
    try:
        response = requests.get('https://data.buienradar.nl/2.0/feed/json', proxies=PROXIES)
        response.raise_for_status()
        document = response.json()
        for station in document['actual']['stationmeasurements']:
            yield {
                'name': station.get('stationname')[len('Meetstation '):],
                'regio': station.get('regio'),
                'airpressure': station.get('airpressure'),
                'visibility': station.get('visibility'),
                'weatherdescription': station.get('weatherdescription'),
                'winddirection': station.get('winddirection'),
                'lat': station.get('lat'),
                'lon': station.get('lon'),
                'temperature': station.get('temperature'),
                'groundtemperature': station.get('groundtemperature'),
                'feeltemperature': station.get('feeltemperature'),
                'windgusts': station.get('windgusts'),
                'windspeed': station.get('windspeed'),
                'windspeed_bft': station.get('windspeedBft'),
                'humidity': station.get('humidity'),
                'precipitation': station.get('precipitation'),
                'rain_fall_last_24_hour': station.get('rainFallLast24Hour'),
                'rain_fall_last_hour': station.get('rainFallLastHour'),
                'winddirection_degrees': station.get('winddirectiondegrees'),
                'sun_power': station.get('sunpower'),
                'sunrise': document['actual']['sunrise'],
                'sunset': document['actual']['sunset']
            }
    except requests.RequestException as e:
        error_count.inc()
        logging.error(f"{e}")
        return []

def initialize_gauges():
    """Initialize the Prometheus gauges for each metric with help text."""
    general_metrics = {
        'airpressure': 'Air pressure in hPa',
        'visibility': 'Visibility in meters',
        'lat': 'Latitude of the station',
        'lon': 'Longitude of the station',
        'temperature': 'Temperature in degrees Celsius',
        'groundtemperature': 'Ground temperature in degrees Celsius',
        'feeltemperature': 'Feels-like temperature in degrees Celsius',
        'windgusts': 'Wind gust speed in meters per second',
        'windspeed': 'Wind speed in meters per second',
        'windspeed_bft': 'Wind speed on the Beaufort scale',
        'humidity': 'Humidity in percentage',
        'precipitation': 'Precipitation in millimeters',
        'rain_fall_last_24_hour': 'Rainfall in the last 24 hours in millimeters',
        'rain_fall_last_hour': 'Rainfall in the last hour in millimeters',
        'winddirection_degrees': 'Wind direction in degrees',
        'sun_power': 'Sun power in watts per square meter',
        'sunrise': 'Time of sunrise in epoch seconds',
        'sunset': 'Time of sunset in epoch seconds',
    }

    for metric, help_text in general_metrics.items():
        prometheus_gauges[metric] = Gauge(f'buienradar_{metric}', help_text, ['station', 'regio'])

    prometheus_gauges['weatherdescription'] = Gauge('buienradar_weather_description', 'Weather description of the station', ['station', 'regio', 'weatherdescription'])
    prometheus_gauges['winddirection'] = Gauge('buienradar_wind_direction', 'Wind direction of the station', ['station', 'regio', 'winddirection'])

def convert_to_epoch(time_string):
    """Convert time in format '2024-10-13T08:00:00' to epoch seconds."""
    dt = datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%S')
    epoch = int(dt.timestamp())
    return epoch

def main():
    """Main function to start Prometheus exporter and fetch/update metrics."""
    logging.basicConfig(level=logging.INFO, format='level=%(levelname)s msg="%(message)s"')
    start_http_server(PORT)
    logging.info(f"Started Prometheus buienradar exporter on port {PORT}")
    
    while True:
        data = list(buienradar_current_data())
        if data and not prometheus_gauges:
            initialize_gauges()
        if data:
            sunrise_time = data[0].get('sunrise')
            sunset_time = data[0].get('sunset')
            sunrise_epoch = convert_to_epoch(sunrise_time)
            sunset_epoch = convert_to_epoch(sunset_time)
            prometheus_gauges['sunrise'].labels(station="global", regio="global").set(sunrise_epoch)
            prometheus_gauges['sunset'].labels(station="global", regio="global").set(sunset_epoch)
            logging.debug(f"Sunrise: {sunrise_time}, Sunset: {sunset_time}")
        
        logging.info(f"Got data for {len(data)} stations")
        for station in data:
            name = station['name']
            regio = station['regio']
            weatherdescription = station['weatherdescription']
            winddirection = station['winddirection']
            for metric, value in station.items():
                if value is not None:
                    if metric in ['weatherdescription', 'winddirection']:
                        prometheus_gauges[metric].labels(station=name, regio=regio, **{metric: value}).set(1)
                    elif metric not in ['name', 'regio', 'weatherdescription', 'winddirection', 'sunrise', 'sunset']:
                        prometheus_gauges[metric].labels(station=name, regio=regio).set(value)
        time.sleep(5 * 60)  # Buienradar queries the KNMI which refreshes every 10 minutes

if __name__ == "__main__":
    main()

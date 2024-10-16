# Buienradar Prometheus Exporter

This script fetches weather data from Buienradar and exposes it as Prometheus metrics. It runs a web server to serve these metrics.

## Usage

```bash
docker run -d \
    -p 9002:9002 \
    --name buienradar_exporter \
    maikel09/buienradar-exporter
```

## Script Details

The script fetches data from Buienradar every 5 minutes, processes it, and exposes it as Prometheus metrics.

### Metrics

- `buienradar_airpressure` - Air pressure in hPa
- `buienradar_visibility` - Visibility in meters
- `buienradar_lat` - Latitude of the station
- `buienradar_lon` - Longitude of the station
- `buienradar_temperature` - Temperature in degrees Celsius
- `buienradar_groundtemperature` - Ground temperature in degrees Celsius
- `buienradar_feeltemperature` - Feels-like temperature in degrees Celsius
- `buienradar_windgusts` - Wind gust speed in meters per second
- `buienradar_windspeed` - Wind speed in meters per second
- `buienradar_windspeed_bft` - Wind speed on the Beaufort scale
- `buienradar_humidity` - Humidity in percentage
- `buienradar_precipitation` - Precipitation in millimeters
- `buienradar_rain_fall_last_24_hour` - Rainfall in the last 24 hours in millimeters
- `buienradar_rain_fall_last_hour` - Rainfall in the last hour in millimeters
- `buienradar_winddirection_degrees` - Wind direction in degrees
- `buienradar_sun_power` - Sun power in watts per square meter
- `buienradar_sunrise` - Time of sunrise in epoch seconds
- `buienradar_sunset` - Time of sunset in epoch seconds
- `buienradar_weather_description` - Weather description of the station
- `buienradar_wind_direction` - Wind direction of the station

### Error Metrics

- `buienradar_api_errors_total` - The number of errors encountered while accessing the Buienradar API

## Configuration

### Environment Variables

- `HTTP_PROXY`: Set this variable to use an HTTP proxy.
- `HTTPS_PROXY`: Set this variable to use an HTTPS proxy.

## Logging

The script uses `logging` to log information in `logfmt` format.

### Example Log Entry

```
INFO level=info msg="Started Prometheus buienradar exporter on port 9002"
INFO level=info msg="Got data for 10 stations"
INFO level=info msg="Sunrise: 2024-10-13T08:00:00, Sunset: 2024-10-13T18:00:00"
```

## Author

Maikel Wagteveld

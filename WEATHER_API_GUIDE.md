# Weather API Integration Guide

## Overview

The Ecofy Backend now includes a complete weather forecast integration using WeatherAPI.com. This provides 14-day weather forecasts for any location worldwide.

## Setup

### 1. Get Your WeatherAPI Key

1. Sign up at [https://www.weatherapi.com](https://www.weatherapi.com)
2. Go to your dashboard and copy your API key
3. The free tier supports 14-day forecasts with 1 million calls/month

### 2. Configure Environment Variable

Add your API key to the `.env` file:

```env
WEATHER_API_KEY=your_actual_api_key_here
```

### 3. Install Dependencies

The `weatherapi` package is already in `requirements.txt`. If you need to reinstall:

```bash
pip install -r requirements.txt
```

## API Endpoints

### 1. Simple 14-Day Forecast (Recommended)

**Endpoint:** `GET /api/weather/forecast`

Returns simplified daily forecasts without hourly data.

**Query Parameters:**
- `location` (required): City name, coordinates, or location query
  - Examples: `"Dar es Salaam,TZ"`, `"-6.7924,39.2083"`, `"Arusha"`
- `days` (optional): Number of days (1-14, default: 14)
- `include_alerts` (optional): Include weather alerts (default: true)
- `include_aqi` (optional): Include air quality index (default: true)

**Example Request:**
```bash
curl "http://localhost:8000/api/weather/forecast?location=Dar%20es%20Salaam,TZ&days=14"
```

**Example Response:**
```json
{
  "location_name": "Dar es Salaam",
  "country": "Tanzania",
  "timezone": "Africa/Dar_es_Salaam",
  "local_time": "2026-01-27 14:30",
  "forecast_days": [
    {
      "date": "2026-01-27",
      "condition": "Partly cloudy",
      "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png",
      "max_temp_c": 32.5,
      "min_temp_c": 24.8,
      "avg_temp_c": 28.2,
      "chance_of_rain": 30,
      "total_precip_mm": 2.5,
      "avg_humidity": 75,
      "max_wind_kph": 18.5,
      "uv": 8.0,
      "sunrise": "06:15 AM",
      "sunset": "06:45 PM"
    },
    // ... 13 more days
  ]
}
```

### 2. Detailed Forecast with Hourly Data

**Endpoint:** `GET /api/weather/forecast/detailed`

Returns complete forecast including 24-hour data for each day.

**Query Parameters:** Same as simple forecast

**Example Request:**
```bash
curl "http://localhost:8000/api/weather/forecast/detailed?location=Arusha&days=7"
```

### 3. Current Weather

**Endpoint:** `GET /api/weather/current`

Returns real-time weather conditions.

**Query Parameters:**
- `location` (required): Location to get weather for

**Example Request:**
```bash
curl "http://localhost:8000/api/weather/current?location=Dar%20es%20Salaam"
```

## Usage Examples

### Python (using requests)

```python
import requests

# Simple forecast
response = requests.get(
    "http://localhost:8000/api/weather/forecast",
    params={
        "location": "Dar es Salaam,TZ",
        "days": 14
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Location: {data['location_name']}, {data['country']}")
    
    for day in data['forecast_days']:
        print(f"\n{day['date']}: {day['condition']}")
        print(f"  Temp: {day['min_temp_c']}°C - {day['max_temp_c']}°C")
        print(f"  Rain chance: {day['chance_of_rain']}%")
        print(f"  Humidity: {day['avg_humidity']}%")
else:
    print(f"Error: {response.json()}")
```

### JavaScript/TypeScript (Frontend)

```javascript
async function getWeatherForecast(location, days = 14) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/weather/forecast?location=${encodeURIComponent(location)}&days=${days}`
    );
    
    if (!response.ok) {
      throw new Error('Weather API request failed');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching weather:', error);
    throw error;
  }
}

// Usage
getWeatherForecast('Dar es Salaam,TZ', 14)
  .then(forecast => {
    console.log(`Weather for ${forecast.location_name}`);
    forecast.forecast_days.forEach(day => {
      console.log(`${day.date}: ${day.condition}, ${day.max_temp_c}°C`);
    });
  });
```

### With Authentication (if your app requires it)

```python
import requests

# Get auth token first
login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "user@example.com", "password": "password"}
)
token = login_response.json()['access_token']

# Make authenticated weather request
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/weather/forecast",
    params={"location": "Dar es Salaam", "days": 14},
    headers=headers  # If your endpoint requires auth
)
```

## Location Formats

The weather API accepts various location formats:

1. **City name:** `Dar es Salaam`, `Arusha`, `Mwanza`
2. **City with country code:** `Dar es Salaam,TZ`, `London,UK`
3. **Coordinates (lat,lon):** `-6.7924,39.2083`
4. **Zip code:** `12345` (for supported countries)
5. **IP address:** `auto:ip` (detects location from IP)

## Response Data Explained

### Daily Forecast Fields

- `date`: Forecast date (YYYY-MM-DD)
- `condition`: Weather description (e.g., "Partly cloudy", "Light rain")
- `icon`: URL to weather icon image
- `max_temp_c` / `min_temp_c` / `avg_temp_c`: Temperatures in Celsius
- `chance_of_rain`: Probability of rain (0-100%)
- `total_precip_mm`: Expected precipitation in millimeters
- `avg_humidity`: Average humidity percentage
- `max_wind_kph`: Maximum wind speed in km/h
- `uv`: UV index (0-11+, higher = more intense)
- `sunrise` / `sunset`: Local sunrise and sunset times

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid parameters)
- `503`: Weather API service unavailable
- `500`: Server error

**Example Error Response:**
```json
{
  "detail": "No location found matching parameter 'q'"
}
```

## Agricultural Use Cases

### 1. Planting Decisions

Check precipitation forecasts for the next 14 days to plan planting:

```python
forecast = get_weather_forecast("Arusha", 14)

rainy_days = [
    day for day in forecast['forecast_days'] 
    if day['chance_of_rain'] > 70
]

print(f"Expected rainy days: {len(rainy_days)}")
```

### 2. Irrigation Planning

Calculate irrigation needs based on rainfall:

```python
total_rainfall = sum(
    day['total_precip_mm'] 
    for day in forecast['forecast_days'][:7]  # Next 7 days
)

if total_rainfall < 10:  # mm
    print("Low rainfall expected - increase irrigation")
```

### 3. Pest/Disease Alerts

High humidity + warm temps can indicate disease risk:

```python
risk_days = [
    day for day in forecast['forecast_days']
    if day['avg_humidity'] > 80 and day['avg_temp_c'] > 25
]

if len(risk_days) > 3:
    print("High disease risk - monitor crops closely")
```

## Testing

Test the weather endpoint:

```bash
# Start the server
uvicorn app.main:app --reload

# In another terminal, test the endpoint
curl "http://localhost:8000/api/weather/forecast?location=Dar%20es%20Salaam&days=14"
```

## API Documentation

Once your server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

All weather endpoints are documented there with interactive testing capabilities.

## Limitations & Notes

- **Free tier:** 1 million API calls/month (very generous)
- **Max forecast days:** 14 (WeatherAPI limitation on free tier)
- **Hourly data:** Available for all 14 days via `/forecast/detailed`
- **Historical data:** Not included (use different endpoint if needed)
- **Rate limits:** Respect API rate limits; implement caching if needed

## Support

For issues or questions:
1. Check WeatherAPI docs: https://www.weatherapi.com/docs/
2. Review server logs for detailed error messages
3. Verify your API key is valid and active

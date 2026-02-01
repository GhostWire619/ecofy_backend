# Weather API - Quick Start

## ✅ Implementation Complete!

I've successfully implemented a complete weather forecast API for your Ecofy backend. Here's what was added:

## 📁 New Files Created

1. **[app/schemas/weather.py](app/schemas/weather.py)** - Pydantic models for weather data
2. **[app/services/weather_service.py](app/services/weather_service.py)** - Service layer for WeatherAPI integration
3. **[app/api/routes/weather.py](app/api/routes/weather.py)** - FastAPI routes for weather endpoints
4. **[WEATHER_API_GUIDE.md](WEATHER_API_GUIDE.md)** - Complete usage documentation

## 🚀 Quick Setup (3 steps)

### 1. Get Your API Key
- Sign up at: https://www.weatherapi.com
- Copy your API key from the dashboard (free tier works great!)

### 2. Add to .env file
```env
WEATHER_API_KEY=your_api_key_here
```

### 3. Install Dependencies (if needed)
```bash
# Activate your virtual environment
venv\Scripts\activate

# Install/update packages
pip install -r requirements.txt
```

## 🌤️ API Endpoints

### 1. Simple 14-Day Forecast (Recommended)
```
GET /api/weather/forecast?location=Dar es Salaam,TZ&days=14
```

Returns clean daily summaries: temps, rain chance, humidity, wind, UV, sunrise/sunset.

### 2. Detailed Forecast with Hourly Data
```
GET /api/weather/forecast/detailed?location=Dar es Salaam&days=14
```

Includes everything + 24-hour data for each day.

### 3. Current Weather
```
GET /api/weather/current?location=Dar es Salaam
```

Real-time conditions.

## 🧪 Test It

### Start the server:
```bash
venv\Scripts\activate
uvicorn app.main:app --reload
```

### Test with curl:
```bash
curl "http://localhost:8000/api/weather/forecast?location=Dar%20es%20Salaam,TZ&days=14"
```

### Or visit the docs:
- http://localhost:8000/docs (Swagger UI - interactive testing!)
- http://localhost:8000/redoc

## 📊 Example Response

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
      "max_temp_c": 32.5,
      "min_temp_c": 24.8,
      "chance_of_rain": 30,
      "total_precip_mm": 2.5,
      "sunrise": "06:15 AM",
      "sunset": "06:45 PM"
    }
    // ... 13 more days
  ]
}
```

## 🌍 Location Formats Supported

- City name: `Dar es Salaam`, `Arusha`
- With country: `Dar es Salaam,TZ`
- Coordinates: `-6.7924,39.2083`
- Auto-detect: `auto:ip`

## 🌾 Agricultural Use Cases

Perfect for:
- **Planting decisions** - Check rain forecasts
- **Irrigation planning** - Calculate rainfall totals
- **Pest/disease alerts** - Monitor humidity + temp patterns
- **Harvest timing** - Avoid rainy periods

## 📚 Full Documentation

See [WEATHER_API_GUIDE.md](WEATHER_API_GUIDE.md) for:
- Detailed API documentation
- Code examples (Python, JavaScript)
- Agricultural use cases
- Error handling
- Advanced features

## ✨ What You Get

- ✅ 14-day weather forecasts
- ✅ Current weather conditions
- ✅ Daily + hourly data
- ✅ Rain probability & amounts
- ✅ Temperature, humidity, wind, UV
- ✅ Sunrise/sunset times
- ✅ Weather alerts (when available)
- ✅ Air quality index
- ✅ Free tier: 1M calls/month

## 🎯 Next Steps

1. **Add your API key** to `.env`
2. **Start the server**: `uvicorn app.main:app --reload`
3. **Test it**: Visit http://localhost:8000/docs
4. **Integrate**: Use the endpoints in your app!

Need help? Check [WEATHER_API_GUIDE.md](WEATHER_API_GUIDE.md) for examples and troubleshooting.

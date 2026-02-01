from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import logging

from app.schemas.weather import (
    WeatherForecastRequest,
    SimpleWeatherForecastResponse,
)
from app.services.weather_service import get_weather_service, WeatherService
from weatherapi.rest import ApiException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/forecast", response_model=SimpleWeatherForecastResponse)
async def get_weather_forecast(
    location: str = Query(
        ..., 
        description="Location to get weather for (e.g., 'Dar es Salaam,TZ', '-6.7924,39.2083')",
        example="Dar es Salaam,TZ"
    ),
    days: int = Query(
        default=14,
        ge=1,
        le=14,
        description="Number of forecast days (1-14)"
    ),
    include_alerts: bool = Query(
        default=True,
        description="Include weather alerts"
    ),
    include_aqi: bool = Query(
        default=True,
        description="Include air quality index"
    ),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get weather forecast for the next 1-14 days.
    
    Returns simplified daily forecast including:
    - Temperature (max, min, average)
    - Weather condition and icon
    - Chance of rain and precipitation amount
    - Humidity, wind speed, UV index
    - Sunrise and sunset times
    
    **Example locations:**
    - City name: `Dar es Salaam` or `Dar es Salaam,TZ`
    - Coordinates: `-6.7924,39.2083` (lat,lon)
    - Zip code: `12345` (for supported countries)
    """
    try:
        logger.info(f"Weather forecast requested for {location}, {days} days")
        
        forecast = weather_service.get_simple_forecast(
            location=location,
            days=days,
            include_alerts=include_alerts,
            include_aqi=include_aqi
        )
        
        return forecast
        
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except ApiException as e:
        logger.error(f"WeatherAPI error: {e}")
        error_msg = "Failed to fetch weather data"
        
        if hasattr(e, 'body'):
            try:
                # Try to parse error body for better error message
                import json
                error_body = json.loads(e.body) if isinstance(e.body, str) else e.body
                if isinstance(error_body, dict) and 'error' in error_body:
                    error_msg = error_body['error'].get('message', error_msg)
            except:
                pass
        
        raise HTTPException(status_code=503, detail=error_msg)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while fetching weather data"
        )


@router.get("/forecast/detailed")
async def get_detailed_weather_forecast(
    location: str = Query(
        ..., 
        description="Location to get weather for",
        example="Dar es Salaam,TZ"
    ),
    days: int = Query(
        default=14,
        ge=1,
        le=14,
        description="Number of forecast days (1-14)"
    ),
    include_alerts: bool = Query(
        default=True,
        description="Include weather alerts"
    ),
    include_aqi: bool = Query(
        default=True,
        description="Include air quality index"
    ),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get detailed weather forecast including hourly data.
    
    Returns complete forecast data including:
    - All daily aggregates
    - Hourly forecast (24 hours per day)
    - Astronomical data (sunrise, sunset, moon phase)
    - Weather alerts (if any)
    - Air quality index (if available)
    
    **Warning:** This endpoint returns significantly more data than `/forecast`.
    Use it only when you need hourly details.
    """
    try:
        logger.info(f"Detailed weather forecast requested for {location}, {days} days")
        
        forecast = weather_service.get_forecast(
            location=location,
            days=days,
            include_alerts=include_alerts,
            include_aqi=include_aqi
        )
        
        # Convert the weatherapi response to a dictionary
        # The response object has to_dict() method
        return forecast.to_dict()
        
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except ApiException as e:
        logger.error(f"WeatherAPI error: {e}")
        error_msg = "Failed to fetch weather data"
        
        if hasattr(e, 'body'):
            try:
                import json
                error_body = json.loads(e.body) if isinstance(e.body, str) else e.body
                if isinstance(error_body, dict) and 'error' in error_body:
                    error_msg = error_body['error'].get('message', error_msg)
            except:
                pass
        
        raise HTTPException(status_code=503, detail=error_msg)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while fetching weather data"
        )


@router.get("/current")
async def get_current_weather(
    location: str = Query(
        ..., 
        description="Location to get current weather for",
        example="Dar es Salaam,TZ"
    ),
    weather_service: WeatherService = Depends(get_weather_service)
):
    """
    Get current weather conditions for a location.
    
    Returns real-time weather data including:
    - Current temperature, feels-like temperature
    - Weather condition
    - Wind speed and direction
    - Humidity, pressure, visibility
    - UV index
    - Air quality (if available)
    """
    try:
        logger.info(f"Current weather requested for {location}")
        
        current = weather_service.get_current_weather(location=location)
        
        # Convert to dictionary
        return current.to_dict()
        
    except ApiException as e:
        logger.error(f"WeatherAPI error: {e}")
        error_msg = "Failed to fetch current weather"
        
        if hasattr(e, 'body'):
            try:
                import json
                error_body = json.loads(e.body) if isinstance(e.body, str) else e.body
                if isinstance(error_body, dict) and 'error' in error_body:
                    error_msg = error_body['error'].get('message', error_msg)
            except:
                pass
        
        raise HTTPException(status_code=503, detail=error_msg)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while fetching current weather"
        )

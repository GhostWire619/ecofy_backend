import logging
from typing import Optional, Dict, Any
import weatherapi
from weatherapi.rest import ApiException

from app.core.config import settings
from app.schemas.weather import (
    WeatherForecastResponse, 
    SimpleDayForecast, 
    SimpleWeatherForecastResponse
)

logger = logging.getLogger(__name__)


class WeatherService:
    """Service to interact with WeatherAPI.com for weather forecasts"""
    
    def __init__(self):
        if not settings.WEATHER_API_KEY:
            logger.warning("WEATHER_API_KEY not configured in environment")
            raise ValueError("Weather API key is required but not configured")
        
        # Configure the weatherapi client
        self.configuration = weatherapi.Configuration()
        self.configuration.api_key['key'] = settings.WEATHER_API_KEY
        
        # Create API client and instance
        self.api_client = weatherapi.ApiClient(self.configuration)
        self.api_instance = weatherapi.APIsApi(self.api_client)
    
    def get_forecast(
        self,
        location: str,
        days: int = 14,
        include_alerts: bool = True,
        include_aqi: bool = True
    ) -> Dict[str, Any]:
        """
        Get weather forecast for a location
        
        Args:
            location: Location query (city name, coordinates, etc.)
            days: Number of days to forecast (1-14)
            include_alerts: Include weather alerts
            include_aqi: Include air quality index
            
        Returns:
            Weather forecast data as dictionary
            
        Raises:
            ApiException: If the API request fails
            ValueError: If parameters are invalid
        """
        if not 1 <= days <= 14:
            raise ValueError("Days must be between 1 and 14")
        
        try:
            logger.info(f"Fetching {days}-day forecast for location: {location}")
            
            # Call the forecast endpoint
            response = self.api_instance.forecast_weather(
                q=location,
                days=days,
                alerts='yes' if include_alerts else 'no',
                aqi='yes' if include_aqi else 'no'
            )
            
            logger.info(f"Successfully retrieved forecast for {response.location.name}")
            return response
            
        except ApiException as e:
            logger.error(f"WeatherAPI error: {e}")
            if hasattr(e, 'body'):
                logger.error(f"Error details: {e.body}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting forecast: {e}")
            raise
    
    def get_simple_forecast(
        self,
        location: str,
        days: int = 14,
        include_alerts: bool = True,
        include_aqi: bool = True
    ) -> SimpleWeatherForecastResponse:
        """
        Get a simplified weather forecast (without hourly data)
        
        Args:
            location: Location query (city name, coordinates, etc.)
            days: Number of days to forecast (1-14)
            include_alerts: Include weather alerts
            include_aqi: Include air quality index
            
        Returns:
            Simplified weather forecast response
        """
        # Get full forecast from API
        response = self.get_forecast(location, days, include_alerts, include_aqi)
        
        # Transform to simplified format
        forecast_days = []
        for day_forecast in response.forecast.forecastday:
            simple_day = SimpleDayForecast(
                date=day_forecast.date,
                condition=day_forecast.day.condition.text,
                icon=day_forecast.day.condition.icon,
                max_temp_c=day_forecast.day.maxtemp_c,
                min_temp_c=day_forecast.day.mintemp_c,
                avg_temp_c=day_forecast.day.avgtemp_c,
                chance_of_rain=day_forecast.day.daily_chance_of_rain,
                total_precip_mm=day_forecast.day.totalprecip_mm,
                avg_humidity=day_forecast.day.avghumidity,
                max_wind_kph=day_forecast.day.maxwind_kph,
                uv=day_forecast.day.uv,
                sunrise=day_forecast.astro.sunrise,
                sunset=day_forecast.astro.sunset
            )
            forecast_days.append(simple_day)
        
        return SimpleWeatherForecastResponse(
            location_name=response.location.name,
            country=response.location.country,
            timezone=response.location.tz_id,
            local_time=response.location.localtime,
            forecast_days=forecast_days
        )
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """
        Get current weather for a location
        
        Args:
            location: Location query (city name, coordinates, etc.)
            
        Returns:
            Current weather data
        """
        try:
            logger.info(f"Fetching current weather for location: {location}")
            
            response = self.api_instance.realtime_weather(q=location, aqi='yes')
            
            logger.info(f"Successfully retrieved current weather for {response.location.name}")
            return response
            
        except ApiException as e:
            logger.error(f"WeatherAPI error: {e}")
            if hasattr(e, 'body'):
                logger.error(f"Error details: {e.body}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting current weather: {e}")
            raise


# Singleton instance
_weather_service: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    """Get or create the weather service instance"""
    global _weather_service
    
    if _weather_service is None:
        _weather_service = WeatherService()
    
    return _weather_service

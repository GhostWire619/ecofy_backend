from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import httpx
from typing import Optional

from app.api.deps import get_current_user
from app.core.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.farm import SoilParameters

router = APIRouter()

@router.get("/weather/forecast", response_model=dict)
async def get_weather_forecast(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    current_user: User = Depends(get_current_user)
):
    if not settings.WEATHER_API_KEY:
        # If no API key, return mock data
        return {
            "current": {
                "temp": 25.4,
                "humidity": 78,
                "wind_speed": 3.6,
                "weather": [{"main": "Cloudy", "description": "Partly cloudy"}]
            },
            "daily": [
                {
                    "dt": 1635768000,
                    "temp": {"day": 26.7, "min": 19.8, "max": 29.1},
                    "humidity": 75,
                    "wind_speed": 4.2,
                    "weather": [{"main": "Sunny", "description": "Clear sky"}]
                }
                # More days would be included here
            ],
            "alerts": []
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openweathermap.org/data/3.0/onecall",
                params={
                    "lat": lat,
                    "lon": lng,
                    "exclude": "minutely,hourly",
                    "units": "metric",
                    "appid": settings.WEATHER_API_KEY
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Weather service unavailable"
                )
            
            return response.json()
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to fetch weather data"
        )


@router.get("/satellite/soil", response_model=SoilParameters)
async def get_satellite_soil_data(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    current_user: User = Depends(get_current_user)
):
    if not settings.SATELLITE_API_KEY:
        # If no API key, return mock data
        return {
            "moisture": "Medium",
            "organic_carbon": "1.5%",
            "texture": "Sandy Loam",
            "ph": "6.8",
            "ec": "0.35 dS/m",
            "salinity": "Low",
            "water_holding": "Medium",
            "organic_matter": "Medium",
            "npk": "N: Medium, P: Low, K: High"
        }
    
    try:
        # In a real app, this would call a satellite data service
        # For demo purposes, we'll return mock data
        return {
            "moisture": "Medium",
            "organic_carbon": "1.5%",
            "texture": "Sandy Loam",
            "ph": "6.8",
            "ec": "0.35 dS/m",
            "salinity": "Low",
            "water_holding": "Medium",
            "organic_matter": "Medium",
            "npk": "N: Medium, P: Low, K: High"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to fetch satellite data"
        ) 
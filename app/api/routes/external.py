from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import httpx
import requests
from typing import Optional
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta
import logging

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
    # Check if needed packages are properly installed
    if not all(module_name in globals() for module_name in ["openmeteo_requests", "pd", "requests_cache", "retry"]):
        # If required packages are not installed, return mock data
        return {
            "current": {
                "temp": 25.4,
                "humidity": 78,
                "wind_speed": 3.6,
                "weather": [{"main": "Cloudy", "description": "Partly cloudy"}]
            },
            "daily": [
                {
                    "dt": int(datetime.now().timestamp()),
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
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)
        
        # Configure the API request
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lng,
            "hourly": ["temperature_2m", "relative_humidity_2m", "cloud_cover", "soil_temperature_18cm", "wind_speed_10m"],
            "current": ["wind_speed_10m", "wind_direction_10m", "temperature_2m", "relative_humidity_2m", "precipitation", "cloud_cover", "rain"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "relative_humidity_2m_mean", "wind_speed_10m_max"]
        }
        
        responses = openmeteo.weather_api(url, params=params)
        
        # Process first location
        response = responses[0]
        
        # Process current weather data
        current = response.Current()
        current_wind_speed = float(current.Variables(0).Value())  # Convert to Python float
        current_wind_direction = float(current.Variables(1).Value())
        current_temperature = float(current.Variables(2).Value())
        current_humidity = float(current.Variables(3).Value())
        current_precipitation = float(current.Variables(4).Value())
        current_cloud_cover = float(current.Variables(5).Value())
        current_rain = float(current.Variables(6).Value())
        
        # Determine weather condition based on cloud cover and rain
        weather_main = "Clear"
        weather_description = "Clear sky"
        
        if current_cloud_cover > 80:
            weather_main = "Clouds"
            weather_description = "Overcast"
        elif current_cloud_cover > 50:
            weather_main = "Clouds"
            weather_description = "Cloudy"
        elif current_cloud_cover > 25:
            weather_main = "Clouds"
            weather_description = "Partly cloudy"
            
        if current_rain > 0:
            weather_main = "Rain"
            if current_rain < 1:
                weather_description = "Light rain"
            elif current_rain < 5:
                weather_description = "Moderate rain"
            else:
                weather_description = "Heavy rain"
        
        # Format current weather in the expected structure
        current_weather = {
            "temp": current_temperature,
            "humidity": current_humidity,
            "wind_speed": current_wind_speed,
            "weather": [{"main": weather_main, "description": weather_description}]
        }
        
        # Process daily data
        daily = response.Daily()
        daily_data = []
        
        # Get timestamps for each day
        daily_times = pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )
        
        # Convert NumPy arrays to Python lists
        daily_max_temp = [float(x) for x in daily.Variables(0).ValuesAsNumpy()]
        daily_min_temp = [float(x) for x in daily.Variables(1).ValuesAsNumpy()]
        daily_mean_temp = [float(x) for x in daily.Variables(2).ValuesAsNumpy()]
        daily_humidity = [float(x) for x in daily.Variables(3).ValuesAsNumpy()]
        daily_wind_speed = [float(x) for x in daily.Variables(4).ValuesAsNumpy()]
        
        for i in range(len(daily_times)):
            # Simple weather estimation based on the temperature difference
            temp_diff = daily_max_temp[i] - daily_min_temp[i]
            weather_main = "Sunny"
            weather_desc = "Clear sky"
            
            if temp_diff < 5:  # Small temperature difference often means cloudy
                weather_main = "Clouds"
                weather_desc = "Partly cloudy"
            
            daily_data.append({
                "dt": int(daily_times[i].timestamp()),
                "temp": {
                    "day": daily_mean_temp[i],
                    "min": daily_min_temp[i],
                    "max": daily_max_temp[i]
                },
                "humidity": daily_humidity[i],
                "wind_speed": daily_wind_speed[i],
                "weather": [{"main": weather_main, "description": weather_desc}]
            })
        
        # Return the weather data in the expected format
        return {
            "current": current_weather,
            "daily": daily_data,
            "alerts": []  # Open-Meteo doesn't provide alerts in the free version
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch weather data: {str(e)}"
        )


@router.get("/satellite/soil", response_model=SoilParameters)
async def get_satellite_soil_data(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    current_user: User = Depends(get_current_user)
):
    """Get soil data from satellite API."""
    logger = logging.getLogger(__name__)
    logger.info(f"Fetching soil data for coordinates: {lat}, {lng}")
    
    # Default soil parameters to return if something fails
    default_soil_params = SoilParameters(
        moisture="Medium (Default)",
        organic_carbon="1.5% (Default)",
        texture="Sandy Loam (Default)",
        ph="6.8 (Default)",
        ec="0.35 dS/m (Default)",
        salinity="Low (Default)",
        water_holding="Medium (Default)",
        organic_matter="Medium (Default)",
        npk="N: Medium, P: Low, K: High (Default)"
    )
    
    # Check if ISDA credentials are available
    if not (settings.ISDA_USERNAME and settings.ISDA_PASSWORD):
        logger.warning("ISDA credentials not set, using mock data")
        # If no credentials, return default data
        return default_soil_params
    
    try:
        logger.info(f"Using credentials - Username: {settings.ISDA_USERNAME}")
        # Use the ISDA Africa API
        base_url = "https://api.isda-africa.com"
        
        # Get access token
        payload = {"username": settings.ISDA_USERNAME, "password": settings.ISDA_PASSWORD}
        logger.info("Authenticating with ISDA API")
        
        try:
            auth_response = requests.post(f"{base_url}/login", data=payload)
            logger.info(f"Auth response status: {auth_response.status_code}")
            
            if auth_response.status_code != 200:
                logger.error(f"Auth failed with response: {auth_response.text}")
                # Return default data on authentication failure
                return default_soil_params
            
            # Get access token
            try:
                access_token = auth_response.json().get("access_token")
                if not access_token:
                    logger.error("No access token in auth response")
                    # Return default data if no token
                    return default_soil_params
            except Exception as e:
                logger.error(f"Error parsing auth response: {str(e)}")
                # Return default data on JSON parsing error
                return default_soil_params
            
            logger.info("Successfully obtained access token")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # List of soil properties to fetch
            properties = [
                "ph", 
                "carbon_organic",
                "nitrogen_total", 
                "phosphorous_extractable", 
                "potassium_extractable",
                "texture_class", 
                "cation_exchange_capacity",
                "sand_content", 
                "silt_content", 
                "clay_content",
                "stone_content",
                "bulk_density"
            ]
            
            logger.info(f"Fetching {len(properties)} soil properties")
            
            # Fetch soil properties
            soil_data = {}
            successful_properties = 0
            
            for prop in properties:
                logger.info(f"Fetching property: {prop}")
                try:
                    response = requests.get(
                        f"{base_url}/isdasoil/v2/soilproperty",
                        params={
                            "lat": lat,
                            "lon": lng,
                            "property": prop,
                            "depth": "0-20"
                        },
                        headers=headers
                    )
                    
                    logger.info(f"Property {prop} response status: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        if prop in data.get("property", {}):
                            soil_data[prop] = data["property"][prop]
                            logger.info(f"Successfully fetched {prop}")
                            successful_properties += 1
                        else:
                            logger.warning(f"Property {prop} not found in response data")
                    else:
                        logger.error(f"Failed to fetch {prop}: {response.text}")
                except Exception as e:
                    logger.error(f"Error fetching property {prop}: {str(e)}")
            
            # If no soil data was fetched, return default data
            if successful_properties == 0:
                logger.warning("No soil data fetched, using default data")
                return default_soil_params
            
            logger.info(f"Successfully fetched {successful_properties} out of {len(properties)} properties")
            
        except Exception as e:
            logger.error(f"Error during API authentication: {str(e)}")
            # Return default data on authentication error
            return default_soil_params
        
        logger.info(f"Processing soil data, {len(soil_data)} properties fetched")
        
        # Calculate water holding capacity based on soil texture
        water_holding = "Low"
        if "clay_content" in soil_data and "sand_content" in soil_data:
            clay = soil_data["clay_content"][0]["value"]["value"] if soil_data["clay_content"] else 0
            sand = soil_data["sand_content"][0]["value"]["value"] if soil_data["sand_content"] else 0
            
            if clay > 30:  # High clay content
                water_holding = "High"
            elif clay > 15 or sand < 50:  # Medium clay content or less sandy
                water_holding = "Medium"
        
        # Determine moisture level based on soil composition
        moisture = "Medium"
        if "clay_content" in soil_data and "sand_content" in soil_data:
            clay = soil_data["clay_content"][0]["value"]["value"] if soil_data["clay_content"] else 0
            sand = soil_data["sand_content"][0]["value"]["value"] if soil_data["sand_content"] else 0
            
            if clay > 35:
                moisture = "High"
            elif sand > 60:
                moisture = "Low"
        
        # Get organic matter from organic carbon (approximate conversion)
        organic_matter = "Medium"
        if "carbon_organic" in soil_data:
            oc = soil_data["carbon_organic"][0]["value"]["value"] if soil_data["carbon_organic"] else 0
            # Organic matter is approximately 1.72 times organic carbon
            om_value = oc * 1.72 / 10  # Convert from g/kg to %
            
            if om_value > 3:
                organic_matter = "High"
            elif om_value < 1:
                organic_matter = "Low"
            else:
                organic_matter = f"{om_value:.1f}%"
        
        # Format NPK values
        npk = "N: Medium, P: Low, K: High"
        n_value = "Medium"
        p_value = "Low"
        k_value = "Medium"
        
        if "nitrogen_total" in soil_data:
            n = soil_data["nitrogen_total"][0]["value"]["value"] if soil_data["nitrogen_total"] else 0
            if n > 1.5:
                n_value = "High"
            elif n < 0.7:
                n_value = "Low"
            else:
                n_value = f"{n} g/kg"
        
        if "phosphorous_extractable" in soil_data:
            p = soil_data["phosphorous_extractable"][0]["value"]["value"] if soil_data["phosphorous_extractable"] else 0
            if p > 20:
                p_value = "High"
            elif p < 10:
                p_value = "Low"
            else:
                p_value = f"{p} ppm"
        
        if "potassium_extractable" in soil_data:
            k = soil_data["potassium_extractable"][0]["value"]["value"] if soil_data["potassium_extractable"] else 0
            if k > 200:
                k_value = "High"
            elif k < 100:
                k_value = "Low"
            else:
                k_value = f"{k} ppm"
        
        npk = f"N: {n_value}, P: {p_value}, K: {k_value}"
        
        # Format electrical conductivity (EC) - approximated from CEC
        ec = "0.35 dS/m"
        if "cation_exchange_capacity" in soil_data:
            cec = soil_data["cation_exchange_capacity"][0]["value"]["value"] if soil_data["cation_exchange_capacity"] else 0
            # Very rough approximation, actual conversion would need more parameters
            ec = f"{(cec * 0.1):.2f} dS/m"
        
        # Determine salinity level based on approximated EC
        salinity = "Low"
        if "cation_exchange_capacity" in soil_data:
            cec = soil_data["cation_exchange_capacity"][0]["value"]["value"] if soil_data["cation_exchange_capacity"] else 0
            if cec > 25:
                salinity = "Medium"
            elif cec > 40:
                salinity = "High"
        
        # Extract texture class
        texture = "Sandy Loam"
        if "texture_class" in soil_data:
            texture = soil_data["texture_class"][0]["value"]["value"] if soil_data["texture_class"] else "Sandy Loam"
        
        # Format pH
        ph = "6.8"
        if "ph" in soil_data:
            ph = str(soil_data["ph"][0]["value"]["value"]) if soil_data["ph"] else "6.8"
        
        # Format organic carbon
        organic_carbon = "1.5%"
        if "carbon_organic" in soil_data:
            oc = soil_data["carbon_organic"][0]["value"]["value"] if soil_data["carbon_organic"] else 0
            organic_carbon = f"{oc/10:.1f}%" # Convert from g/kg to %
        
        # Create and return a SoilParameters object
        return SoilParameters(
            moisture=moisture,
            organic_carbon=organic_carbon,
            texture=texture,
            ph=ph,
            ec=ec,
            salinity=salinity,
            water_holding=water_holding,
            organic_matter=organic_matter,
            npk=npk
        )
        
    except Exception as e:
        logger.error(f"Error in get_satellite_soil_data: {str(e)}")
        # Return default parameters on any unexpected error
        return default_soil_params 
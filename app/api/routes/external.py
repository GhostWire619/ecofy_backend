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
import weatherapi
from weatherapi.rest import ApiException

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
    """
    Get weather forecast using weatherapi.com
    """
    # Configure API key authorization: ApiKeyAuth
    configuration = weatherapi.Configuration()
    configuration.api_key['key'] = 'd09bcdfd9ebe471c8ab104556252406'
    # create an instance of the API class
    api_instance = weatherapi.APIsApi(weatherapi.ApiClient(configuration))
    q = f"{lat},{lng}"
    try:
        # Current weather API
        api_response = api_instance.realtime_weather(q)
        # Format the response to match the previous structure
        current = api_response['current']
        location = api_response['location']
        result = {
            "current": {
                "temp": current.get("temp_c"),
                "humidity": current.get("humidity"),
                "wind_speed": current.get("wind_kph"),
                "weather": [{
                    "main": current.get("condition", {}).get("text", "Unknown"),
                    "description": current.get("condition", {}).get("text", "Unknown")
                }],
                "last_updated": current.get("last_updated")
            },
            "location": {
                "name": location.get("name"),
                "region": location.get("region"),
                "country": location.get("country"),
                "lat": location.get("lat"),
                "lon": location.get("lon"),
                "tz_id": location.get("tz_id"),
                "localtime": location.get("localtime")
            },
            "alerts": []
        }
        # Optionally, you can add forecast if needed (requires forecast API call)
        return result
    except ApiException as e:
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
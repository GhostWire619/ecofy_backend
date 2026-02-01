"""
Agricultural Analysis Service using Gemini AI
Provides insights on soil, climate, market, and general agricultural data
"""

import json
import logging
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from app.core.config import settings

logger = logging.getLogger(__name__)


class AgriculturalGeminiService:
    """Service for agricultural data analysis using Gemini"""

    def __init__(self):
        self.api_key = None
        self.client = None
        self.analysis_model = "gemini-2.0-flash-exp"
        
    def _ensure_initialized(self):
        """Lazy initialization of Gemini client"""
        if self.client is None:
            self.api_key = settings.GOOGLE_GEMINI_API_KEY
            if not self.api_key:
                raise ValueError("GOOGLE_GEMINI_API_KEY environment variable not set")
            
            self.client = genai.Client(api_key=self.api_key)

    def analyze_location_data(
        self,
        coordinates: Dict[str, float],
        soil_data: Dict[str, Any],
        weather_data: Dict[str, Any],
        crop_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Analyze agricultural data for a specific location
        
        Args:
            coordinates: {"latitude": float, "longitude": float}
            soil_data: Soil properties (pH, nutrients, moisture, texture, etc.)
            weather_data: Weather conditions (temperature, rainfall, humidity, etc.)
            crop_data: Optional current crop information
            
        Returns:
            {
                "soil_insights": "...",
                "climate_insights": "...",
                "market_insights": "...",
                "general_insights": "..."
            }
        """
        self._ensure_initialized()
        
        try:
            prompt = self._build_location_analysis_prompt(
                coordinates, soil_data, weather_data, crop_data
            )
            
            response = self.client.models.generate_content(
                model=self.analysis_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )
            
            result = json.loads(response.text)
            
            # Ensure all required keys are present
            return {
                "soil_insights": result.get("soil_insights", ""),
                "climate_insights": result.get("climate_insights", ""),
                "market_insights": result.get("market_insights", ""),
                "general_insights": result.get("general_insights", "")
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response.text}")
            raise ValueError("Failed to parse AI response as JSON")
        except Exception as e:
            logger.error(f"Error in location data analysis: {e}")
            raise

    def analyze_crop_specific(
        self,
        crop_name: str,
        coordinates: Optional[Dict[str, float]] = None,
        soil_data: Optional[Dict[str, Any]] = None,
        weather_data: Optional[Dict[str, Any]] = None,
        additional_context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Analyze data specific to a particular crop
        
        Args:
            crop_name: Name of the crop to analyze
            coordinates: Optional location coordinates
            soil_data: Optional soil properties
            weather_data: Optional weather conditions
            additional_context: Optional additional information
            
        Returns:
            {
                "soil_insights": "...",
                "climate_insights": "...",
                "market_insights": "...",
                "general_insights": "..."
            }
        """
        self._ensure_initialized()
        
        try:
            prompt = self._build_crop_analysis_prompt(
                crop_name, coordinates, soil_data, weather_data, additional_context
            )
            
            response = self.client.models.generate_content(
                model=self.analysis_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )
            
            result = json.loads(response.text)
            
            return {
                "soil_insights": result.get("soil_insights", ""),
                "climate_insights": result.get("climate_insights", ""),
                "market_insights": result.get("market_insights", ""),
                "general_insights": result.get("general_insights", "")
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError("Failed to parse AI response as JSON")
        except Exception as e:
            logger.error(f"Error in crop-specific analysis: {e}")
            raise

    def _build_location_analysis_prompt(
        self,
        coordinates: Dict[str, float],
        soil_data: Dict[str, Any],
        weather_data: Dict[str, Any],
        crop_data: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for location-based analysis"""
        
        return f"""You are an expert agricultural consultant with deep knowledge of soil science, climatology, agronomy, and agricultural markets.

        Analyze the following agricultural data and provide comprehensive, actionable insights:

        **Location Coordinates:**
        {json.dumps(coordinates, indent=2)}

        **Soil Data:**
        {json.dumps(soil_data, indent=2)}

        **Weather Data:**
        {json.dumps(weather_data, indent=2)}

        {f'**Current Crop Data:**\n{json.dumps(crop_data, indent=2)}' if crop_data else '**Current Status:** No crop currently planted'}

        Provide your analysis in the following JSON format with detailed, specific insights:

        {{
            "soil_insights": "Analyze soil health, nutrient levels, pH balance, organic matter content, texture, drainage, and provide specific recommendations for soil improvement. Identify any deficiencies or excesses.",
            "climate_insights": "Analyze weather patterns, temperature ranges, rainfall adequacy, humidity levels, seasonal variations, and climate suitability. Discuss potential climate-related risks and optimal planting windows.",
            "market_insights": "Provide insights on crop market trends for this region, demand-supply dynamics, price forecasts, value-added opportunities, and recommended crops based on market potential.",
            "general_insights": "Provide overall recommendations, best practices for this location, water management strategies, pest and disease considerations, and any other relevant agricultural guidance."
        }}

        Be specific, practical, and actionable. Use data-driven insights."""

    def _build_crop_analysis_prompt(
        self,
        crop_name: str,
        coordinates: Optional[Dict[str, float]],
        soil_data: Optional[Dict[str, Any]],
        weather_data: Optional[Dict[str, Any]],
        additional_context: Optional[str]
    ) -> str:
        """Build prompt for crop-specific analysis"""
        
        location_info = f"\n**Location Coordinates:**\n{json.dumps(coordinates, indent=2)}" if coordinates else ""
        soil_info = f"\n**Soil Data:**\n{json.dumps(soil_data, indent=2)}" if soil_data else ""
        weather_info = f"\n**Weather Data:**\n{json.dumps(weather_data, indent=2)}" if weather_data else ""
        context_info = f"\n**Additional Context:**\n{additional_context}" if additional_context else ""
        
        return f"""You are an expert agricultural consultant specializing in crop production and management.

        Analyze the following information for **{crop_name}** cultivation:
        {location_info}{soil_info}{weather_info}{context_info}

        Provide comprehensive insights specific to {crop_name} in the following JSON format:

        {{
            "soil_insights": "Analyze soil requirements for {crop_name}, including ideal pH range, nutrient needs (NPK and micronutrients), soil texture preferences, organic matter requirements, and provide specific soil preparation and amendment recommendations.",
            "climate_insights": "Analyze climate requirements for {crop_name}, including optimal temperature range, rainfall needs, humidity preferences, sunlight requirements, frost sensitivity, and growing season timing. Assess climate suitability based on provided data.",
            "market_insights": "Provide market analysis for {crop_name}, including current market trends, demand outlook, pricing forecasts, export opportunities, value chain options, and profitability potential in the given region.",
            "general_insights": "Provide comprehensive cultivation guidance for {crop_name}, including planting techniques, irrigation strategies, fertilization schedules, pest and disease management, harvesting best practices, and yield optimization strategies."
        }}

        Be specific to {crop_name} and provide actionable, data-driven recommendations."""


# Singleton instance
agricultural_service = AgriculturalGeminiService()
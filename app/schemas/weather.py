from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class WeatherCondition(BaseModel):
    text: str
    icon: str
    code: int


class Astro(BaseModel):
    sunrise: str
    sunset: str
    moonrise: str
    moonset: str
    moon_phase: str
    moon_illumination: str


class HourlyForecast(BaseModel):
    time_epoch: int
    time: str
    temp_c: float
    temp_f: float
    is_day: int
    condition: WeatherCondition
    wind_mph: float
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: float
    pressure_in: float
    precip_mm: float
    precip_in: float
    humidity: int
    cloud: int
    feelslike_c: float
    feelslike_f: float
    windchill_c: float
    windchill_f: float
    heatindex_c: float
    heatindex_f: float
    dewpoint_c: float
    dewpoint_f: float
    will_it_rain: int
    chance_of_rain: int
    will_it_snow: int
    chance_of_snow: int
    vis_km: float
    vis_miles: float
    gust_mph: float
    gust_kph: float
    uv: float


class DayForecast(BaseModel):
    maxtemp_c: float
    maxtemp_f: float
    mintemp_c: float
    mintemp_f: float
    avgtemp_c: float
    avgtemp_f: float
    maxwind_mph: float
    maxwind_kph: float
    totalprecip_mm: float
    totalprecip_in: float
    totalsnow_cm: float
    avgvis_km: float
    avgvis_miles: float
    avghumidity: int
    daily_will_it_rain: int
    daily_chance_of_rain: int
    daily_will_it_snow: int
    daily_chance_of_snow: int
    condition: WeatherCondition
    uv: float


class ForecastDay(BaseModel):
    date: str
    date_epoch: int
    day: DayForecast
    astro: Astro
    hour: List[HourlyForecast]


class Location(BaseModel):
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str
    localtime_epoch: int
    localtime: str


class Current(BaseModel):
    last_updated_epoch: int
    last_updated: str
    temp_c: float
    temp_f: float
    is_day: int
    condition: WeatherCondition
    wind_mph: float
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: float
    pressure_in: float
    precip_mm: float
    precip_in: float
    humidity: int
    cloud: int
    feelslike_c: float
    feelslike_f: float
    windchill_c: float
    windchill_f: float
    heatindex_c: float
    heatindex_f: float
    dewpoint_c: float
    dewpoint_f: float
    vis_km: float
    vis_miles: float
    uv: float
    gust_mph: float
    gust_kph: float


class Forecast(BaseModel):
    forecastday: List[ForecastDay]


class WeatherForecastResponse(BaseModel):
    location: Location
    current: Current
    forecast: Forecast


class WeatherForecastRequest(BaseModel):
    location: str = Field(
        ..., 
        description="Location query (city name, coordinates 'lat,lon', etc.)",
        example="Dar es Salaam,TZ"
    )
    days: int = Field(
        default=14, 
        ge=1, 
        le=14, 
        description="Number of days to forecast (1-14)"
    )
    include_hourly: bool = Field(
        default=False, 
        description="Include hourly forecast data"
    )
    include_alerts: bool = Field(
        default=True, 
        description="Include weather alerts"
    )
    include_aqi: bool = Field(
        default=True, 
        description="Include air quality index"
    )


class SimpleDayForecast(BaseModel):
    """Simplified version without hourly data for lighter responses"""
    date: str
    condition: str
    icon: str
    max_temp_c: float
    min_temp_c: float
    avg_temp_c: float
    chance_of_rain: int
    total_precip_mm: float
    avg_humidity: int
    max_wind_kph: float
    uv: float
    sunrise: str
    sunset: str


class SimpleWeatherForecastResponse(BaseModel):
    location_name: str
    country: str
    timezone: str
    local_time: str
    forecast_days: List[SimpleDayForecast]

"""
Test script for the Weather API endpoints.
Run this after starting the server to verify everything works.

Usage:
    python test_weather_api.py
"""

import requests
import json
from pprint import pprint


BASE_URL = "http://localhost:8000/api/weather"


def test_simple_forecast():
    """Test the simple 14-day forecast endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Simple 14-Day Forecast")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/forecast",
        params={
            "location": "Dar es Salaam,TZ",
            "days": 14
        }
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success! Got forecast for {data['location_name']}, {data['country']}")
        print(f"Timezone: {data['timezone']}")
        print(f"Local time: {data['local_time']}")
        print(f"\nFirst 3 days forecast:")
        
        for day in data['forecast_days'][:3]:
            print(f"\n📅 {day['date']} - {day['condition']}")
            print(f"   🌡️  Temperature: {day['min_temp_c']}°C - {day['max_temp_c']}°C (avg: {day['avg_temp_c']}°C)")
            print(f"   🌧️  Rain chance: {day['chance_of_rain']}% ({day['total_precip_mm']}mm)")
            print(f"   💨 Wind: {day['max_wind_kph']} km/h")
            print(f"   💧 Humidity: {day['avg_humidity']}%")
            print(f"   ☀️  UV Index: {day['uv']}")
            print(f"   🌅 Sunrise: {day['sunrise']} | Sunset: {day['sunset']}")
        
        print(f"\n... and {len(data['forecast_days']) - 3} more days")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
        return False


def test_detailed_forecast():
    """Test the detailed forecast with hourly data"""
    print("\n" + "="*60)
    print("TEST 2: Detailed Forecast (7 days)")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/forecast/detailed",
        params={
            "location": "Arusha,TZ",
            "days": 7
        }
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        location = data['location']
        forecast = data['forecast']['forecastday']
        
        print(f"\n✅ Success! Got detailed forecast for {location['name']}")
        print(f"Total days: {len(forecast)}")
        print(f"First day has {len(forecast[0]['hour'])} hourly entries")
        
        # Show first day's summary
        first_day = forecast[0]
        print(f"\n📅 {first_day['date']} Summary:")
        print(f"   Condition: {first_day['day']['condition']['text']}")
        print(f"   Temp range: {first_day['day']['mintemp_c']}°C - {first_day['day']['maxtemp_c']}°C")
        
        # Show a few hourly entries
        print(f"\n   Hourly samples:")
        for hour in first_day['hour'][::6]:  # Every 6 hours
            print(f"   {hour['time']}: {hour['temp_c']}°C, {hour['condition']['text']}, Rain: {hour['chance_of_rain']}%")
        
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
        return False


def test_current_weather():
    """Test current weather endpoint"""
    print("\n" + "="*60)
    print("TEST 3: Current Weather")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/current",
        params={
            "location": "Mwanza,TZ"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        location = data['location']
        current = data['current']
        
        print(f"\n✅ Success! Current weather in {location['name']}, {location['country']}")
        print(f"Local time: {location['localtime']}")
        print(f"\n🌤️  Current Conditions:")
        print(f"   Condition: {current['condition']['text']}")
        print(f"   Temperature: {current['temp_c']}°C (feels like {current['feelslike_c']}°C)")
        print(f"   Humidity: {current['humidity']}%")
        print(f"   Wind: {current['wind_kph']} km/h {current['wind_dir']}")
        print(f"   Pressure: {current['pressure_mb']} mb")
        print(f"   Visibility: {current['vis_km']} km")
        print(f"   UV Index: {current['uv']}")
        
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
        return False


def test_different_locations():
    """Test various location formats"""
    print("\n" + "="*60)
    print("TEST 4: Different Location Formats")
    print("="*60)
    
    locations = [
        ("Dodoma", "City name only"),
        ("Zanzibar,TZ", "City with country code"),
        ("-6.7924,39.2083", "Coordinates (Dar es Salaam)"),
    ]
    
    for location, description in locations:
        print(f"\n📍 Testing: {description} - '{location}'")
        response = requests.get(
            f"{BASE_URL}/forecast",
            params={"location": location, "days": 3}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data['location_name']}, {data['country']}")
        else:
            print(f"   ❌ Failed: {response.json().get('detail', 'Unknown error')}")


def test_error_handling():
    """Test error cases"""
    print("\n" + "="*60)
    print("TEST 5: Error Handling")
    print("="*60)
    
    # Invalid location
    print("\n🧪 Test: Invalid location")
    response = requests.get(
        f"{BASE_URL}/forecast",
        params={"location": "InvalidCity12345XYZ", "days": 7}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   ✅ Correctly returns error: {response.json().get('detail', 'Unknown')}")
    
    # Invalid days parameter
    print("\n🧪 Test: Invalid days (>14)")
    response = requests.get(
        f"{BASE_URL}/forecast",
        params={"location": "Dar es Salaam", "days": 20}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   ✅ Correctly returns error: {response.json().get('detail', [{}])[0].get('msg', 'Unknown')}")


def main():
    print("\n" + "="*60)
    print("🌤️  WEATHER API TEST SUITE")
    print("="*60)
    print("\nMake sure the server is running:")
    print("  uvicorn app.main:app --reload")
    print("\nStarting tests...\n")
    
    try:
        results = {
            "Simple Forecast": test_simple_forecast(),
            "Detailed Forecast": test_detailed_forecast(),
            "Current Weather": test_current_weather(),
        }
        
        test_different_locations()
        test_error_handling()
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        print("\n" + "="*60)
        if all(results.values()):
            print("🎉 All tests passed! Weather API is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to the server!")
        print("Make sure the server is running:")
        print("  uvicorn app.main:app --reload")
        print("\nOr check if you're using a different port.\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")


if __name__ == "__main__":
    main()

import requests
from config import Config
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenWeatherMapTool:
    def __init__(self):
        self.api_key = Config.OPENWEATHERMAP_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        if not self.api_key:
            logger.error("OpenWeatherMap API Key is not configured!")
            raise ValueError("OpenWeatherMap API Key is missing.")

    async def get_weather_forecast(self, city: str) -> dict:
        """
        For best results, city should be in the format "CityName,CountryCode"
        e.g., "San Francisco,US" or "London,GB".
        For US cities, "CityName,StateCode,CountryCode" (e.g., "San Francisco,CA,US") might also work.
        """
        logger.info(f"Attempting to fetch weather for city: '{city}'")
        try:
            params = {"q": city, "appid": self.api_key, "units": "metric"}
            response = await asyncio.to_thread(
                requests.get, self.base_url, params = params
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched weather for '{city}': {data['weather'][0]['description']}, Temp: {data['main']['temp']}°C")
            return {
                "city": city,
                "temperature": data["main"]["temp"],
                "weather": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "country": data.get("sys", {}).get("country") # Adding country for context
            }
        
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error fetching weather data for '{city}': {http_err.response.status_code} - {http_err.response.text}")
            # You could raise a custom error or return a specific dict indicating failure
            raise # Re-raise the error to be caught by the agent/orchestrator
        except Exception as e:
            logger.error(f"Generic error fetching weather data for '{city}': {str(e)}", exc_info=True)
            raise

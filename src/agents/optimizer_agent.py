# src/agents/optimizer_agent.py
from src.agents.base_agent import BaseAgent
from src.tools.google_maps_tool import GoogleMapsTool
from src.tools.openweathermap_tool import OpenWeatherMapTool
from src.prompts.optimizer_prompts import OPTIMIZER_PROMPT
import logging
import traceback
from datetime import timedelta
from types import MappingProxyType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.maps_tool = GoogleMapsTool()
        self.weather_tool = OpenWeatherMapTool()

    async def process(self, input_data: dict) -> dict:
        try:
            initial_plan = input_data.get("initial_plan")
            origin = input_data.get("origin")
            destination = input_data.get("destination")
            preferences = input_data.get("preferences")

            missing_inputs = []
            if not initial_plan:
                missing_inputs.append("initial_plan")
            if not origin:
                missing_inputs.append("origin")
            if not destination:
                missing_inputs.append("destination")
            if not preferences:
                missing_inputs.append("preferences")

            if missing_inputs:
                logger.error(f"Missing required inputs: {', '.join(missing_inputs)}")
                raise ValueError(f"Missing required input data: {', '.join(missing_inputs)}")

            logger.info(f"Optimizer input - initial_plan: {initial_plan}")
            logger.info(f"Optimizer input - origin: {origin} (type: {type(origin)})")
            logger.info(f"Optimizer input - destination: {destination} (type: {type(destination)})")
            logger.info(f"Optimizer input - preferences: {preferences}")

            route_data = await self.maps_tool.get_directions(origin, destination)
            # Convert route_data to serializable format
            if route_data:
                route_data = self._serialize_route_data(route_data)
            logger.info(f"Serialized route data: {route_data}")

            logger.info(f"Fetching weather for origin: {origin}")
            origin_weather_data = await self.weather_tool.get_weather_forecast(origin)
            # Serialize weather data
            origin_weather_data = self._serialize_route_data(origin_weather_data)
            logger.info(f"Serialized origin weather data: {origin_weather_data}")

            logger.info(f"Fetching weather for destination: {destination}")
            destination_weather_data = await self.weather_tool.get_weather_forecast(destination)
            # Serialize weather data
            destination_weather_data = self._serialize_route_data(destination_weather_data)
            logger.info(f"Serialized destination weather data: {destination_weather_data}")

            prompt = OPTIMIZER_PROMPT.format(
                initial_plan=initial_plan,
                route_data=route_data,
                weather_origin = origin_weather_data,
                weather_destination = destination_weather_data,
                preferences=preferences
            )
            optimized_plan = await self.generate_response(prompt)

            result = {
                "optimized_plan": optimized_plan,
                "route_data": route_data,
                "weather_origin": origin_weather_data,
                "weather_destination": destination_weather_data
            }
            logger.info(f"Optimizer output: {result}")
            return result
        except Exception as e:
            logger.error(f"OptimizerAgent error: {str(e)}\nTraceback: {traceback.format_exc()}")
            raise

    def _serialize_route_data(self, data):
        """
        Convert Route, timedelta, mappingproxy, Descriptor, or other non-serializable objects to serializable format.
        
        Args:
            data: Input data (Route, dict, list, timedelta, mappingproxy, Descriptor, etc.).
        
        Returns:
            Serializable data (dict, list, str, etc.).
        """
        try:
            if isinstance(data, dict):
                return {key: self._serialize_route_data(value) for key, value in data.items()}
            elif isinstance(data, MappingProxyType):
                return self._serialize_route_data(dict(data))
            elif isinstance(data, timedelta):
                return str(data)  # e.g., '0:30:00'
            elif isinstance(data, list):
                return [self._serialize_route_data(item) for item in data]
            elif hasattr(data, '__dict__'):
                return self._serialize_route_data(data.__dict__)
            elif str(type(data)).find('Descriptor') != -1:
                return str(data)  # Convert Descriptor to string
            elif data is None:
                return None
            else:
                return data
        except Exception as e:
            logger.error(f"Error serializing data: {str(e)}")
            raise
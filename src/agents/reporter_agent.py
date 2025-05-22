from src.agents.base_agent import BaseAgent
from src.prompts.common_prompts import REPORTER_PROMPT
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReporterAgent(BaseAgent):
    async def process(self, input_data: dict) -> dict:
        try:
            optimized_plan = input_data.get("optimized_plan")
            route_data = input_data.get("route_data")
            weather_origin = input_data.get("weather_origin")
            weather_destination = input_data.get("weather_destination")
            preferences = input_data.get("preferences",{})

            missing_inputs = []
            if not optimized_plan:
                missing_inputs.append("optimized_plan")
            if not route_data:
                missing_inputs.append("route_data")
            if not weather_origin:
                missing_inputs.append("weather_origin")
            if not weather_destination:
                missing_inputs.append("weather_destination")
            if not preferences:
                missing_inputs.append("preferences")

            if missing_inputs:
                logger.error(f"Missing required inputs: {', '.join(missing_inputs)}")
                raise ValueError(f"Missing required input data: {', '.join(missing_inputs)}")
            
            logger.info(f"Reporter input - optimized_plan: {optimized_plan}")
            logger.info(f"Reporter input - route_data: {route_data}")
            logger.info(f"Reporter input - weather_origin: {weather_origin}")
            logger.info(f"Reporter input - weather_destination: {weather_destination}")
            logger.info(f"Reporter input - preferences: {preferences}")

            prompt = REPORTER_PROMPT.format(
                optimized_plan = optimized_plan,
                route_data=json.dumps(route_data),
                weather_origin_data = weather_origin,
                weather_destination_data = weather_destination,
                preferences=json.dumps(preferences),

            )
            final_report = await self.generate_response(prompt)

            return {"final_itinerary": final_report}
        except Exception as e:
            logger.error(f"ReporterAgent error: {str(e)}")
            raise
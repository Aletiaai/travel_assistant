# src/agents/planner_agent.py
from src.agents.base_agent import BaseAgent
from src.llm_integration.llm_client import LLMClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    async def process(self, input_data: dict) -> str:
        try:
            query = input_data.get("query", "")
            origin = input_data.get("origin", "")
            destination = input_data.get("destination", "")
            preferences = input_data.get("preferences", {})
            refinement = input_data.get("refinement", None)
            prior_itinerary = input_data.get("prior_itinerary", None)
            planner_prompt = input_data.get("planner_prompt", "")

            # Validate inputs
            if not query:
                logger.error("Query is empty or missing")
                raise ValueError("Query is required and cannot be empty")
            if not origin:
                logger.error("Origin is empty or missing")
                raise ValueError("Origin is required and cannot be empty")
            if not destination:
                logger.error("Destination is empty or missing")
                raise ValueError("Destination is required and cannot be empty")

            # Construct prompt
            prompt = planner_prompt or "Plan a trip from {origin} to {destination} with preferences: {preferences}."
            if refinement:
                prompt += f" Apply refinement: {refinement}."
            if prior_itinerary:
                prompt += f" Based on prior itinerary: {prior_itinerary}."

            # Format prompt
            formatted_prompt = prompt.format(
                query=query,
                origin=origin,
                destination=destination,
                preferences=preferences,
                refinement=refinement or "",
                prior_itinerary=prior_itinerary or ""
            )
            logger.info(f"Planner prompt: {formatted_prompt}")

            # Generate plan
            plan = await self.llm_client.generate(formatted_prompt)
            logger.info(f"Generated plan: {plan}")
            return plan
        except Exception as e:
            logger.error(f"Planner error: {str(e)}")
            raise
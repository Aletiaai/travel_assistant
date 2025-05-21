# src/orchestrator/main_orchestrator.py
from src.agents.planner_agent import PlannerAgent
from src.agents.optimizer_agent import OptimizerAgent
from src.agents.reporter_agent import ReporterAgent
from src.orchestrator.state_manager import StateManager
import logging
import json
from datetime import timedelta
from types import MappingProxyType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, timedelta):
            return str(obj)
        elif isinstance(obj, MappingProxyType):
            return dict(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif str(type(obj)).find('Descriptor') != -1:
            return str(obj)
        return super().default(obj)

class MainOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.optimizer = OptimizerAgent()
        self.reporter = ReporterAgent()
        self.state_manager = StateManager()

    async def process_query(self, query: str, origin: str, destination: str, preferences: dict, planner_prompt: str = None, refinement: str = None, prior_itinerary: dict = None) -> dict:
        try:
            # Validate inputs
            if not query:
                logger.error("Query is empty or missing")
                raise ValueError("Query is required")
            if not origin:
                logger.error("Origin is empty or missing")
                raise ValueError("Origin is required")
            if not destination:
                logger.error("Destination is empty or missing")
                raise ValueError("Destination is required")

            # Initialize state
            state = {
                "query": query,
                "origin": origin,
                "destination": destination,
                "preferences": preferences,
                "refinement": refinement,
                "prior_itinerary": prior_itinerary
            }
            self.state_manager.update_state(state)
            logger.info(f"Orchestrator state initialized: {json.dumps(state, indent=2, cls=CustomJSONEncoder)}")

            # Generate initial plan with refinement context
            initial_plan_input = {
                "query": query,
                "origin": origin,
                "destination": destination,
                "preferences": preferences,
                "refinement": refinement,
                "prior_itinerary": prior_itinerary.get("final_itinerary") if prior_itinerary else None,
                "planner_prompt": planner_prompt
            }
            logger.info(f"Planner input: {json.dumps(initial_plan_input, indent=2, cls=CustomJSONEncoder)}")
            initial_plan = await self.planner.process(initial_plan_input)
            self.state_manager.update_state({"initial_plan": initial_plan})
            logger.info(f"Initial plan generated: {initial_plan}")

            # Optimize plan
            optimizer_input = {
                "initial_plan": initial_plan,
                "origin": origin,
                "destination": destination,
                "preferences": preferences,
                "refinement": refinement
            }
            optimized_data = await self.optimizer.process(optimizer_input)
            self.state_manager.update_state(optimized_data)
            logger.info(f"Optimized data: {json.dumps(optimized_data, indent=2, cls=CustomJSONEncoder)}")

            # Generate final itinerary
            final_itinerary = await self.reporter.process(self.state_manager.get_state())
            self.state_manager.update_state({"final_itinerary": final_itinerary})
            logger.info(f"Final itinerary generated: {json.dumps(final_itinerary, indent=2, cls=CustomJSONEncoder)}")

            return final_itinerary
        except Exception as e:
            logger.error(f"Orchestrator error: {str(e)}")
            raise
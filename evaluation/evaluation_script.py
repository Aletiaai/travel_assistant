# evaluation/evaluation_script.py
from src.orchestrator.main_orchestrator import MainOrchestrator
from src.prompts.planner_prompts import PLANNER_PROMPT_CASUAL, PLANNER_PROMPT_PRECISE, PLANNER_PROMPT_SCENIC
from src.llm_integration.llm_client import LLMClient
from src.prompts.llm_critique_prompts import CRITIQUE_PROMPT
from evaluation.metrics import compute_average_scores, find_best_prompt
import json
import logging
from typing import Dict, List, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvaluationScript:
    def __init__(self):
        self.orchestrator = MainOrchestrator()
        self.llm_client = LLMClient()

    async def run_evaluation(self, query: str, origin: str, destination: str, preferences: dict, refinement: str = None, prior_itinerary: dict = None) -> Tuple[Optional[dict], List[dict]]:
        try:
            if not query:
                raise ValueError("Query parameter is required and cannot be empty")
            logger.info(f"Starting evaluation with query: {query}")
            
            results = []
            prompt_types = {
                "casual": PLANNER_PROMPT_CASUAL,
                "precise": PLANNER_PROMPT_PRECISE,
                "scenic": PLANNER_PROMPT_SCENIC
            }
            itinerary = None

            for prompt_name, planner_prompt in prompt_types.items():
                try:
                    logger.info(f"Evaluating prompt: {prompt_name}")
                    itinerary = await self.orchestrator.process_query(
                        query=query,
                        origin=origin,
                        destination=destination,
                        preferences=preferences,
                        planner_prompt=planner_prompt,
                        refinement=refinement,
                        prior_itinerary=prior_itinerary
                    )

                    # Extract final_itinerary string from dictionary
                    final_itinerary = itinerary.get("final_itinerary")
                    if not isinstance(final_itinerary, str):
                        logger.error(f"Invalid final_itinerary type: {type(final_itinerary)}")
                        results.append({
                            "prompt": prompt_name,
                            "error": f"Invalid final_itinerary format: expected str, got {type(final_itinerary)}"
                        })
                        continue

                    critique_prompt = CRITIQUE_PROMPT.format(
                        query=query,
                        origin=origin,
                        destination=destination,
                        preferences=preferences,
                        itinerary=final_itinerary
                    )
                    critique_response = await self.llm_client.generate(critique_prompt)

                    try:
                        critique_json = json.loads(critique_response)
                        route_feasibility = float(critique_json.get("route_feasibility", 0))
                        constraint_satisfaction = float(critique_json.get("constraint_satisfaction", 0))
                        response_quality = float(critique_json.get("response_quality", 0))
                        total = (route_feasibility + constraint_satisfaction + response_quality) / 3
                        result = {
                            "prompt": prompt_name,
                            "route_feasibility": route_feasibility,
                            "constraint_satisfaction": constraint_satisfaction,
                            "response_quality": response_quality,
                            "total": total,
                            "comments": critique_json.get("comments", "")
                        }
                    except (json.JSONDecodeError, ValueError) as e:
                        logger.error(f"Failed to parse critique response for {prompt_name}: {str(e)}")
                        result = {
                            "prompt": prompt_name,
                            "route_feasibility": 0.0,
                            "constraint_satisfaction": 0.0,
                            "response_quality": 0.0,
                            "total": 0.0,
                            "error": f"Failed to parse critique response: {str(e)}"
                        }

                    results.append(result)
                    logger.info(f"Evaluation result for {prompt_name}: {result}")
                except Exception as e:
                    logger.error(f"Evaluation error for {prompt_name}: {str(e)}")
                    results.append({
                        "prompt": prompt_name,
                        "route_feasibility": 0.0,
                        "constraint_satisfaction": 0.0,
                        "response_quality": 0.0,
                        "total": 0.0,
                        "error": str(e)
                    })

            avg_scores = compute_average_scores(results)
            best_prompt = find_best_prompt(results)
            logger.info(f"Average evaluation scores: {avg_scores}")
            logger.info(f"Best prompt: {best_prompt}")

            return itinerary or {}, results
        except Exception as e:
            logger.error(f"Evaluation script error: {str(e)}")
            return {}, results
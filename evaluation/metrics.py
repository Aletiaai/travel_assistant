# evaluation/metrics.py
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compute_average_scores(results: List[Dict]) -> Dict:
    """
    Compute average scores for route_feasibility, constraint_satisfaction, response_quality, and total
    across all prompt evaluations.
    
    Args:
        results: List of evaluation results, each containing 'route_feasibility',
                'constraint_satisfaction', 'response_quality', 'total', and 'prompt'.
    
    Returns:
        Dictionary with average scores for each metric and a list of prompts evaluated.
    """
    try:
        if not results:
            logger.warning("No results provided for averaging")
            return {"prompts": [], "avg_route_feasibility": 0.0, "avg_constraint_satisfaction": 0.0,
                    "avg_response_quality": 0.0, "avg_total": 0.0}

        valid_results = [r for r in results if "error" not in r]
        if not valid_results:
            logger.warning("No valid results for averaging")
            return {"prompts": [r["prompt"] for r in results], "avg_route_feasibility": 0.0,
                    "avg_constraint_satisfaction": 0.0, "avg_response_quality": 0.0, "avg_total": 0.0}

        prompts = [r["prompt"] for r in valid_results]
        avg_scores = {
            "prompts": prompts,
            "avg_route_feasibility": sum(r["route_feasibility"] for r in valid_results) / len(valid_results),
            "avg_constraint_satisfaction": sum(r["constraint_satisfaction"] for r in valid_results) / len(valid_results),
            "avg_response_quality": sum(r["response_quality"] for r in valid_results) / len(valid_results),
            "avg_total": sum(r["total"] for r in valid_results) / len(valid_results)
        }
        logger.info(f"Average scores computed: {avg_scores}")
        return avg_scores
    except Exception as e:
        logger.error(f"Error computing average scores: {str(e)}")
        return {"prompts": [r["prompt"] for r in results], "avg_route_feasibility": 0.0,
                "avg_constraint_satisfaction": 0.0, "avg_response_quality": 0.0, "avg_total": 0.0}

def find_best_prompt(results: List[Dict]) -> Dict:
    """
    Identify the prompt with the highest total score.
    
    Args:
        results: List of evaluation results, each containing 'total' and 'prompt'.
    
    Returns:
        Dictionary with the best prompt, its total score, and evaluation details.
    """
    try:
        valid_results = [r for r in results if "error" not in r]
        if not valid_results:
            logger.warning("No valid results for finding best prompt")
            return {"best_prompt": None, "total_score": 0.0, "details": {}}

        best_result = max(valid_results, key=lambda x: x["total"], default={"prompt": None, "total": 0.0})
        result = {
            "best_prompt": best_result["prompt"],
            "total_score": best_result["total"],
            "details": {
                "route_feasibility": best_result["route_feasibility"],
                "constraint_satisfaction": best_result["constraint_satisfaction"],
                "response_quality": best_result["response_quality"],
                "comments": best_result["comments"]
            }
        }
        logger.info(f"Best prompt identified: {result}")
        return result
    except Exception as e:
        logger.error(f"Error finding best prompt: {str(e)}")
        return {"best_prompt": None, "total_score": 0.0, "details": {}}
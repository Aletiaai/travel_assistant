# tests/integration/test_prompt_comparison.py
import pytest
from unittest.mock import AsyncMock, patch
from evaluation.evaluation_script import EvaluationScript

@pytest.mark.asyncio
async def test_prompt_comparison():
    # Initialize EvaluationScript
    evaluator = EvaluationScript()

    # Mock input data
    query = "Plan a scenic trip from San Francisco to Los Angeles"
    origin = "San Francisco, CA, US"
    destination = "Los Angeles, CA, US"
    preferences = {"avoid_bad_weather": True, "include_pois": True}

    # Mock responses
    mock_initial_plan = "Drive from San Francisco to Los Angeles with scenic stops"
    mock_route_data = {"distance": "600 km", "duration": "6 hours"}
    mock_weather_origin = {"city": "San Francisco", "temperature": 20, "weather": "clear"}
    mock_weather_destination = {"city": "Los Angeles", "temperature": 25, "weather": "sunny"}
    mock_optimized_plan = "Optimized plan: Drive with stops at scenic points, avoiding rain"
    mock_final_itinerary = """
    # Travel Itinerary
    **From**: San Francisco, CA, US
    **To**: Los Angeles, CA, US
    **Distance**: 600 km
    **Duration**: 6 hours
    **Weather**: Clear in San Francisco, Sunny in Los Angeles
    **Plan**: Drive with scenic stops
    """
    mock_critique_response = """
    {
        "route_feasibility": 0.9,
        "constraint_satisfaction": 0.85,
        "response_quality": 0.8,
        "comments": "Well-planned itinerary with scenic stops"
    }
    """
    mock_optimizer_output = {
        "optimized_plan": mock_optimized_plan,
        "route_data": mock_route_data,
        "weather_origin": mock_weather_origin,
        "weather_destination": mock_weather_destination
    }

    # Patch dependencies
    with patch.object(evaluator.orchestrator.planner, "process", AsyncMock(return_value=mock_initial_plan)), \
         patch.object(evaluator.orchestrator.optimizer, "process", AsyncMock(return_value=mock_optimizer_output)), \
         patch.object(evaluator.orchestrator.reporter, "process", AsyncMock(return_value={"final_itinerary": mock_final_itinerary})), \
         patch.object(evaluator.llm_client, "generate", AsyncMock(return_value=mock_critique_response)):
        result = await evaluator.run_evaluation(query, origin, destination, preferences)

    # Assertions for tuple return
    assert isinstance(result, tuple), "Result should be a tuple"
    assert len(result) == 2, "Result tuple should contain itinerary and results"
    itinerary, results = result

    # Validate itinerary
    assert isinstance(itinerary, dict), "Itinerary should be a dictionary"
    assert "final_itinerary" in itinerary, "Itinerary should contain 'final_itinerary' key"
    assert itinerary == {"final_itinerary": mock_final_itinerary}, "Itinerary should match mocked response"
    assert isinstance(itinerary["final_itinerary"], str), "Itinerary value should be a string"

    # Validate results
    assert isinstance(results, list), "Results should be a list"
    assert len(results) == 3, "Results should contain evaluations for three prompts"
    prompt_names = {result["prompt"] for result in results}
    assert prompt_names == {"casual", "precise", "scenic"}, "Results should cover all prompt types"

    for result in results:
        if "error" in result:
            continue  # Skip failed prompts
        assert "route_feasibility" in result, "Result should contain route_feasibility score"
        assert "constraint_satisfaction" in result, "Result should contain constraint satisfaction score"
        assert "response_quality" in result, "Result should contain response quality score"
        assert "total" in result, "Result should contain total score"
        assert "comments" in result, "Result should contain comments"
        assert result["route_feasibility"] == 0.9, f"Route feasibility score should be 0.9 for {result['prompt']}"
        assert result["constraint_satisfaction"] == 0.85, f"Constraint satisfaction score should be 0.85 for {result['prompt']}"
        assert result["response_quality"] == 0.8, f"Response quality score should be 0.8 for {result['prompt']}"
        assert result["total"] == pytest.approx(0.85, 0.01), f"Total score should be ~0.85 for {result['prompt']}"

@pytest.mark.asyncio
async def test_prompt_comparison_evaluation_error():
    # Initialize EvaluationScript
    evaluator = EvaluationScript()

    # Mock input data
    query = "Plan a scenic trip from San Francisco to Los Angeles"
    origin = "San Francisco, CA, US"
    destination = "Los Angeles, CA, US"
    preferences = {"avoid_bad_weather": True}

    # Mock invalid critique response
    mock_invalid_critique = "Invalid JSON response"
    mock_final_itinerary = "Final itinerary"
    mock_optimizer_output = {
        "optimized_plan": "Optimized plan",
        "route_data": {"distance": "600 km"},
        "weather_origin": {"city": "San Francisco"},
        "weather_destination": {"city": "Los Angeles"}
    }

    # Patch dependencies to simulate an evaluation error
    with patch.object(evaluator.orchestrator.planner, "process", AsyncMock(return_value="Initial plan")), \
         patch.object(evaluator.orchestrator.optimizer, "process", AsyncMock(return_value=mock_optimizer_output)), \
         patch.object(evaluator.orchestrator.reporter, "process", AsyncMock(return_value={"final_itinerary": mock_final_itinerary})), \
         patch.object(evaluator.llm_client, "generate", AsyncMock(return_value=mock_invalid_critique)):
        result = await evaluator.run_evaluation(query, origin, destination, preferences)

    # Assertions for tuple return
    assert isinstance(result, tuple), "Result should be a tuple"
    assert len(result) == 2, "Result tuple should contain itinerary and results"
    itinerary, results = result

    # Validate itinerary
    assert isinstance(itinerary, dict), "Itinerary should be a dictionary"
    assert "final_itinerary" in itinerary, "Itinerary should contain 'final_itinerary' key"
    assert itinerary == {"final_itinerary": mock_final_itinerary}, "Itinerary should match mocked response"

    # Validate results
    assert isinstance(results, list), "Results should be a list"
    assert len(results) == 3, "Results should contain evaluations for three prompts"
    for result in results:
        assert "error" in result, "Result should contain an error due to invalid critique"
        assert result["route_feasibility"] == 0.0, "Route feasibility should be 0.0 for invalid critique"
        assert result["constraint_satisfaction"] == 0.0, "Constraint satisfaction should be 0.0 for invalid critique"
        assert result["response_quality"] == 0.0, "Response quality should be 0.0 for invalid critique"
        assert result["total"] == 0.0, "Total score should be 0.0 for invalid critique"
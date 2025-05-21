import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.orchestrator.main_orchestrator import MainOrchestrator
from src.prompts.planner_prompts import PLANNER_PROMPT_CASUAL

@pytest.mark.asyncio
async def test_full_trip_flow():
    # Initialize MainOrchestrator
    orchestrator = MainOrchestrator()

    # Mock input data
    query = "Plan a scenic trip from San Francisco to Los Angeles"
    origin = "San Francisco, CA, US"
    destination = "Los Angeles, CA, US"
    preferences = {"avoid_bad_weather": True, "include_pois": True}
    planner_prompt = PLANNER_PROMPT_CASUAL

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

    # Patch dependencies
    with patch.object(orchestrator.planner, "generate_response", AsyncMock(return_value=mock_initial_plan)), \
         patch.object(orchestrator.optimizer.maps_tool, "get_directions", AsyncMock(return_value=mock_route_data)), \
         patch.object(orchestrator.optimizer.weather_tool, "get_weather_forecast", AsyncMock(side_effect=[mock_weather_origin, mock_weather_destination])), \
         patch.object(orchestrator.optimizer, "generate_response", AsyncMock(return_value=mock_optimized_plan)), \
         patch.object(orchestrator.reporter, "generate_response", AsyncMock(return_value=mock_final_itinerary)):
        result = await orchestrator.process_query(query, origin, destination, preferences, planner_prompt)

    # Assertions
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "final_itinerary" in result, "Result should contain 'final_itinerary' key"
    assert result["final_itinerary"] == mock_final_itinerary, "Final itinerary should match mocked response"
    assert isinstance(result["final_itinerary"], str), "Final itinerary should be a string"

@pytest.mark.asyncio
async def test_full_trip_flow_missing_query():
    # Initialize MainOrchestrator
    orchestrator = MainOrchestrator()

    # Mock input data with empty query
    query = ""
    origin = "San Francisco, CA, US"
    destination = "Los Angeles, CA, US"
    preferences = {"avoid_bad_weather": True}
    planner_prompt = PLANNER_PROMPT_CASUAL

    # Test for ValueError
    with pytest.raises(ValueError, match="Query is required"):
        await orchestrator.process_query(query, origin, destination, preferences, planner_prompt)
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.agents.optimizer_agent import OptimizerAgent

@pytest.mark.asyncio
async def test_optimizer_agent_process():
    # Initialize OptimizerAgent
    agent = OptimizerAgent()

    # Mock input data
    input_data = {
        "initial_plan": "Drive from San Francisco to Los Angeles",
        "origin": "San Francisco, CA, US",
        "destination": "Los Angeles, CA, US",
        "preferences": {"avoid_bad_weather": True, "include_pois": True}
    }

    # Mock tool responses
    mock_route_data = {"distance": "600 km", "duration": "6 hours"}
    mock_weather_origin = {"city": "San Francisco", "temperature": 20, "weather": "clear"}
    mock_weather_destination = {"city": "Los Angeles", "temperature": 25, "weather": "sunny"}
    mock_optimized_plan = "Optimized plan: Drive with stops at scenic points, avoiding rain."

    # Patch tool methods and generate_response
    with patch.object(agent.maps_tool, "get_directions", AsyncMock(return_value=mock_route_data)), \
         patch.object(agent.weather_tool, "get_weather_forecast", AsyncMock(side_effect=[mock_weather_origin, mock_weather_destination])), \
         patch.object(agent, "generate_response", AsyncMock(return_value=mock_optimized_plan)):
        result = await agent.process(input_data)

    # Assertions
    assert isinstance(result, dict), "Result should be a dictionary"
    assert result["optimized_plan"] == mock_optimized_plan, "Optimized plan should match mocked response"
    assert result["route_data"] == mock_route_data, "Route data should match mocked response"
    assert result["weather_origin"] == mock_weather_origin, "Weather origin should match mocked response"
    assert result["weather_destination"] == mock_weather_destination, "Weather destination should match mocked response"

@pytest.mark.asyncio
async def test_optimizer_agent_missing_input():
    # Initialize OptimizerAgent
    agent = OptimizerAgent()

    # Mock input data with missing initial_plan
    input_data = {
        "origin": "San Francisco, CA, US",
        "destination": "Los Angeles, CA, US",
        "preferences": {"avoid_bad_weather": True}
    }

    # Test for ValueError
    with pytest.raises(ValueError, match="Missing required input data"):
        await agent.process(input_data)
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.agents.reporter_agent import ReporterAgent

@pytest.mark.asyncio
async def test_reporter_agent_process():
    # Initialize ReporterAgent
    agent = ReporterAgent()

    # Mock input data
    input_data = {
        "optimized_plan": "Drive from San Francisco to Los Angeles with scenic stops",
        "route_data": {"distance": "600 km", "duration": "6 hours"},
        "weather_origin": {"city": "San Francisco", "temperature": 20, "weather": "clear"},
        "weather_destination": {"city": "Los Angeles", "temperature": 25, "weather": "sunny"}
    }

    # Mock LLM response (Google Docs-style text itinerary)
    mock_itinerary = """
    # Travel Itinerary
    **From**: San Francisco, CA, US
    **To**: Los Angeles, CA, US
    **Distance**: 600 km
    **Duration**: 6 hours
    **Weather**: Clear in San Francisco, Sunny in Los Angeles
    **Plan**: Drive with scenic stops
    """

    # Patch generate_response
    with patch.object(agent, "generate_response", AsyncMock(return_value=mock_itinerary)):
        result = await agent.process(input_data)

    # Assertions
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "final_itinerary" in result, "Result should contain 'final_itinerary' key"
    assert result["final_itinerary"] == mock_itinerary, "Final itinerary should match mocked response"
    assert isinstance(result["final_itinerary"], str), "Final itinerary should be a string"

@pytest.mark.asyncio
async def test_reporter_agent_missing_input():
    # Initialize ReporterAgent
    agent = ReporterAgent()

    # Mock input data with missing optimized_plan
    input_data = {
        "route_data": {"distance": "600 km", "duration": "6 hours"},
        "weather_origin": {"city": "San Francisco", "temperature": 20, "weather": "clear"},
        "weather_destination": {"city": "Los Angeles", "temperature": 25, "weather": "sunny"}
    }

    # Test for ValueError
    with pytest.raises(ValueError, match="Missing required input data"):
        await agent.process(input_data)
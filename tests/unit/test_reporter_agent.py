# tests/unit/test_reporter_agent.py
import pytest
from src.agents.reporter_agent import ReporterAgent
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_reporter_agent_process():
    # Initialize ReporterAgent
    agent = ReporterAgent()

    # Mock input data
    input_data = {
        "optimized_plan": "Drive from San Francisco to Los Angeles with scenic stops",
        "route_data": {"distance": "600 km", "duration": "6 hours"},
        "weather_origin": {"city": "San Francisco", "temperature": 20, "weather": "clear"},
        "weather_destination": {"city": "Los Angeles", "temperature": 25, "weather": "sunny"},
        "preferences": {"avoid_bad_weather": True, "include_pois": True}
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

    # Patch llm_client.generate
    with patch.object(agent.llm_client, "generate", AsyncMock(return_value=mock_itinerary)):
        result = await agent.process(input_data)

    assert result["final_itinerary"] == mock_itinerary
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_reporter_agent_missing_input():
    # Initialize ReporterAgent
    agent = ReporterAgent()

    # Mock input data with missing required fields
    input_data = {
        "optimized_plan": "Drive from San Francisco to Los Angeles"
    }

    # Test for ValueError
    with pytest.raises(ValueError, match="Missing required input data"):
        await agent.process(input_data)
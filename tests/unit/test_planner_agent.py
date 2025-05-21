import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.agents.planner_agent import PlannerAgent
from src.prompts.planner_prompts import PLANNER_PROMPT_CASUAL

@pytest.mark.asyncio
async def test_planner_agent_process():
    # Initialize PlannerAgent
    agent = PlannerAgent()

    # Mock input data
    input_data = {
        "query": "Plan a trip from San Francisco to Los Angeles",
        "origin": "San Francisco, CA, US",
        "destination": "Los Angeles, CA, US",
        "preferences": {"avoid_bad_weather": True, "include_pois": True}
    }
    planner_prompt = PLANNER_PROMPT_CASUAL

    # Mock the generate_response method
    mock_response = "Initial plan: Drive from San Francisco to Los Angeles with stops at scenic points."
    with patch.object(agent, "generate_response", AsyncMock(return_value=mock_response)):
        result = await agent.process(planner_prompt, input_data)

    # Assertions
    assert isinstance(result, dict), "Result should be a dictionary"
    assert result["origin"] == input_data["origin"], "Origin should match input"
    assert result["destination"] == input_data["destination"], "Destination should match input"
    assert result["preferences"] == input_data["preferences"], "Preferences should match input"
    assert result["initial_plan"] == mock_response, "Initial plan should match mocked response"

@pytest.mark.asyncio
async def test_planner_agent_missing_query():
    # Initialize PlannerAgent
    agent = PlannerAgent()

    # Mock input data with missing query
    input_data = {
        "origin": "San Francisco, CA, US",
        "destination": "Los Angeles, CA, US",
        "preferences": {"avoid_bad_weather": True}
    }
    planner_prompt = PLANNER_PROMPT_CASUAL

    # Test for ValueError
    with pytest.raises(ValueError, match="Query is required"):
        await agent.process(planner_prompt, input_data)
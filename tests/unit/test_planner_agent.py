# tests/unit/test_planner_agent.py
import pytest
from src.agents.planner_agent import PlannerAgent
from src.prompts.planner_prompts import PLANNER_PROMPT_CASUAL
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_planner_agent_process():
    # Initialize PlannerAgent
    agent = PlannerAgent()

    # Mock input data
    input_data = {
        "query": "Plan a trip from San Francisco to Los Angeles",
        "origin": "San Francisco, CA, US",
        "destination": "Los Angeles, CA, US",
        "preferences": {"avoid_bad_weather": True, "include_pois": True},
        "planner_prompt": PLANNER_PROMPT_CASUAL
    }

    # Mock the llm_client.generate method
    mock_response = "Initial plan: Drive from San Francisco to Los Angeles with stops at scenic points."
    with patch.object(agent.llm_client, "generate", AsyncMock(return_value=mock_response)):
        result = await agent.process(input_data)

    assert result == mock_response
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_planner_agent_missing_query():
    # Initialize PlannerAgent
    agent = PlannerAgent()

    # Mock input data with missing query
    input_data = {
        "origin": "San Francisco, CA, US",
        "destination": "Los Angeles, CA, US",
        "preferences": {"avoid_bad_weather": True},
        "planner_prompt": PLANNER_PROMPT_CASUAL
    }

    # Test for ValueError
    with pytest.raises(ValueError, match="Query is required and cannot be empty"):
        await agent.process(input_data)
# src/agents/base_agent.py
from abc import ABC, abstractmethod
from src.llm_integration.llm_client import LLMClient
import logging
from typing import Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self):
        self.llm_client = LLMClient()

    @abstractmethod
    async def process(self, input_data: dict) -> Union[dict, str]:
        pass

    async def generate_response(self, prompt: str) -> str:
        try:
            return await self.llm_client.generate(prompt)
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
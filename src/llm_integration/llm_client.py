# src/llm_integration/llm_client.py
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from config import Config
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        try:
            Config.validate()
            self.llm = ChatGoogleGenerativeAI(api_key=Config.GEMINI_API_KEY, model=Config.MODEL_NAME)
            logger.info(f"LLM initialized with model: {Config.MODEL_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise

    async def generate(self, prompt: str) -> str:
        try:
            logger.info(f"Sending prompt to model: {prompt[:500]}...")
            messages = [HumanMessage(content=prompt)]
            response = await self.llm.agenerate([messages])
            logger.info(f"Raw response type: {type(response)}")
            logger.info(f"Raw response content: {response}")

            text = response.generations[0][0].message.content
            logger.info(f"Extracted response text: {text[:500]}...")

            if text.startswith("```json") and text.endswith("```"):
                text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
                text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
                logger.info(f"Stripped response text: {text[:500]}...")

            return text
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise
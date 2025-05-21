# src/orchestrator/state_manager.py
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StateManager:
    def __init__(self):
        self.state: Dict = {}
        logger.info("StateManager initialized")

    def update_state(self, new_state: Dict) -> None:
        """
        Update the state with new key-value pairs.
        
        Args:
            new_state: Dictionary containing state data to update.
        """
        try:
            self.state.update(new_state)
            logger.info(f"State updated: {self.state}")
        except Exception as e:
            logger.error(f"Error updating state: {str(e)}")
            raise

    def get_state(self) -> Dict:
        """
        Retrieve the current state.
        
        Returns:
            Current state dictionary.
        """
        try:
            return self.state
        except Exception as e:
            logger.error(f"Error retrieving state: {str(e)}")
            raise

    def clear_state(self) -> None:
        """
        Clear the current state.
        """
        try:
            self.state = {}
            logger.info("State cleared")
        except Exception as e:
            logger.error(f"Error clearing state: {str(e)}")
            raise
"""
Centralized state manager for handling conversation states
"""
from typing import Dict, Any, Optional

class StateManager:
    # user_id -> {'state': 'STATE_NAME', 'metadata': {}}
    _states: Dict[int, Dict[str, Any]] = {}

    @classmethod
    def set_state(cls, user_id: int, state: str, metadata: Optional[Dict[str, Any]] = None):
        """Set the current state for a user"""
        cls._states[user_id] = {
            'state': state,
            'metadata': metadata or {}
        }

    @classmethod
    def get_state(cls, user_id: int) -> Optional[str]:
        """Get the current state name for a user"""
        state_data = cls._states.get(user_id)
        return state_data['state'] if state_data else None

    @classmethod
    def get_metadata(cls, user_id: int) -> Dict[str, Any]:
        """Get metadata associated with current state"""
        state_data = cls._states.get(user_id)
        return state_data['metadata'] if state_data else {}

    @classmethod
    def clear_state(cls, user_id: int):
        """Clear the state for a user"""
        if user_id in cls._states:
            del cls._states[user_id]

    @classmethod
    def is_waiting(cls, user_id: int, state_prefix: str = "") -> bool:
        """Check if user is in a specific state or any state"""
        state = cls.get_state(user_id)
        if not state:
            return False
        return state.startswith(state_prefix)

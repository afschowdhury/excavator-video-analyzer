"""Base agent class for the multi-agent video analysis system"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from rich.console import Console


class BaseAgent(ABC):
    """Abstract base class for all agents in the system"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent

        Args:
            name: Name of the agent
            config: Configuration dictionary for the agent
        """
        self.name = name
        self.config = config or {}
        self.console = Console()
        self.state = {}

    @abstractmethod
    def process(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Process input data and return results

        Args:
            input_data: Input data to process
            context: Optional context from previous agents

        Returns:
            Processed output data
        """
        pass

    def log(self, message: str, level: str = "info"):
        """
        Log a message with appropriate styling

        Args:
            message: Message to log
            level: Log level (info, success, warning, error)
        """
        styles = {
            "info": "[blue]",
            "success": "[green]",
            "warning": "[yellow]",
            "error": "[red]",
        }
        style = styles.get(level, "[white]")
        self.console.print(f"{style}[{self.name}] {message}")

    def update_state(self, key: str, value: Any):
        """
        Update agent state

        Args:
            key: State key
            value: State value
        """
        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get value from agent state

        Args:
            key: State key
            default: Default value if key not found

        Returns:
            State value or default
        """
        return self.state.get(key, default)

    def reset_state(self):
        """Reset agent state"""
        self.state = {}


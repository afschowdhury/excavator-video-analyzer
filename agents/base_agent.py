"""
Base Agent class for ADK integration
"""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from google import genai
from google.genai import types
from rich.console import Console


class BaseAgent(ABC):
    """Base class for all ADK agents"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash-exp",
        name: str = "BaseAgent"
    ):
        """
        Initialize the base agent

        Args:
            api_key (str, optional): Gemini API key
            model (str): Gemini model to use
            name (str): Agent name for logging
        """
        self.api_key = api_key or os.getenv("GENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key required for agent initialization")

        self.model = model
        self.name = name
        self.client = genai.Client(api_key=self.api_key)
        self.console = Console()
        self.results: Dict[str, Any] = {}

    @abstractmethod
    def process(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Process input and generate results
        Must be implemented by subclasses

        Returns:
            Dict[str, Any]: Processing results
        """
        pass

    def get_results(self) -> Dict[str, Any]:
        """
        Get the agent's results

        Returns:
            Dict[str, Any]: Agent results
        """
        return self.results

    def _generate_content(
        self,
        content_parts: list,
        system_instruction: str,
        temperature: float = 0.2,
        top_p: float = 0.95,
        max_tokens: int = 8000
    ) -> str:
        """
        Generate content using Gemini API

        Args:
            content_parts (list): List of content parts (video, text, etc.)
            system_instruction (str): System instruction for the model
            temperature (float): Temperature for generation
            top_p (float): Top-p sampling parameter
            max_tokens (int): Maximum tokens to generate

        Returns:
            str: Generated content text
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=types.Content(parts=content_parts),
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    top_p=top_p,
                    max_output_tokens=max_tokens,
                    system_instruction=system_instruction,
                ),
            )
            return response.text
        except Exception as e:
            self.console.print(f"[bold red]{self.name} Error: {e}")
            raise

    def log(self, message: str, level: str = "info"):
        """
        Log a message

        Args:
            message (str): Message to log
            level (str): Log level (info, warning, error, success)
        """
        colors = {
            "info": "blue",
            "warning": "yellow",
            "error": "red",
            "success": "green"
        }
        color = colors.get(level, "white")
        self.console.print(f"[{color}][{self.name}] {message}")


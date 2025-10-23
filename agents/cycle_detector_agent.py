"""
Cycle Detector Agent - Specializes in detecting and timing excavator dig-dump cycles
"""

from typing import Any, Dict, List

from google.genai import types

from agents.base_agent import BaseAgent
from prompts import POMLParser, PromptManager


class CycleDetectorAgent(BaseAgent):
    """Agent specialized in detecting excavator dig-dump cycles with precise timestamps"""

    def __init__(self, api_key: str = None, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize the Cycle Detector Agent

        Args:
            api_key (str, optional): Gemini API key
            model (str): Gemini model to use
        """
        super().__init__(api_key=api_key, model=model, name="CycleDetector")
        self.prompt_manager = PromptManager()
        self.poml_parser = POMLParser()

    def process(self, video_url: str) -> Dict[str, Any]:
        """
        Process video to detect all dig-dump cycles

        Args:
            video_url (str): URL of the video to analyze

        Returns:
            Dict[str, Any]: Dictionary containing:
                - cycles: List of detected cycles with timestamps
                - summary: Summary statistics
                - raw_response: Raw POML response
        """
        self.log("Starting cycle detection analysis...", "info")

        # Get POML cycle detection prompt
        try:
            system_instruction = self.prompt_manager.get_prompt("cycle_detection")
            prompt_config = self.prompt_manager.get_prompt_config("cycle_detection")
        except KeyError:
            self.log("POML cycle detection template not found, using comprehensive_analysis", "warning")
            system_instruction = self.prompt_manager.get_prompt("comprehensive_analysis")
            prompt_config = self.prompt_manager.get_prompt_config("comprehensive_analysis")

        # Prepare content parts
        content_parts = [
            types.Part(file_data=types.FileData(file_uri=video_url)),
            types.Part(text="Analyze this excavator video and detect ALL dig-dump cycles with precise timestamps using POML markup.")
        ]

        # Generate analysis
        self.log("Analyzing video for cycle detection...", "info")
        raw_response = self._generate_content(
            content_parts=content_parts,
            system_instruction=system_instruction,
            temperature=prompt_config.get("temperature", 0.1),
            top_p=prompt_config.get("top_p", 0.9),
            max_tokens=prompt_config.get("max_tokens", 8000)
        )

        # Parse POML response
        self.log("Parsing cycle data from response...", "info")
        cycles = self.poml_parser.parse_cycles(raw_response)
        summary = self.poml_parser.parse_summary(raw_response)

        # Store results
        self.results = {
            'cycles': cycles,
            'summary': summary,
            'raw_response': raw_response,
            'cycle_count': len(cycles)
        }

        self.log(f"Successfully detected {len(cycles)} cycles", "success")

        return self.results

    def get_cycle_by_id(self, cycle_id: int) -> Dict[str, Any]:
        """
        Get specific cycle by ID

        Args:
            cycle_id (int): Cycle ID to retrieve

        Returns:
            Dict[str, Any]: Cycle data or None if not found
        """
        if 'cycles' not in self.results:
            return None

        for cycle in self.results['cycles']:
            if cycle['id'] == cycle_id:
                return cycle

        return None

    def get_cycles_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for detected cycles

        Returns:
            Dict[str, Any]: Summary statistics
        """
        if 'summary' not in self.results:
            return {}

        return self.results['summary']

    def get_average_cycle_time(self) -> float:
        """
        Calculate average cycle time

        Returns:
            float: Average cycle time in seconds
        """
        if 'cycles' not in self.results or not self.results['cycles']:
            return 0.0

        total_time = 0.0
        count = 0

        for cycle in self.results['cycles']:
            duration_str = cycle.get('total_duration', '0s')
            # Parse duration string (e.g., "32.6s" -> 32.6)
            try:
                time_value = float(duration_str.replace('s', ''))
                total_time += time_value
                count += 1
            except ValueError:
                continue

        return total_time / count if count > 0 else 0.0


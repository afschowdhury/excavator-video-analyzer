"""Performance scoring agent using Gemini AI"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from icecream import ic

from ..base_agent import BaseAgent
from prompts import PromptManager

ic.configureOutput(includeContext=True, prefix="PerformanceScoreAgent- ")


class PerformanceScoreAgent(BaseAgent):
    """Agent responsible for calculating performance scores using AI"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("PerformanceScore", config)
        load_dotenv()
        api_key = os.getenv("GENAI_API_KEY")
        if not api_key:
            raise ValueError("GENAI_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=api_key)
        
        # Load prompt and config from TOML
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "gemini"
        self.prompt_manager = PromptManager(templates_dir=str(prompt_path))
        
        # Get configuration from TOML file
        prompt_config = self.prompt_manager.get_prompt_config("performance_score")
        self.model = self.config.get("model", prompt_config.get("model", "gemini-2.0-flash-exp"))
        self.temperature = self.config.get("temperature", prompt_config.get("temperature", 0.3))
        self.response_mime_type = prompt_config.get("response_mime_type", "application/json")
        
        # Get system prompt
        self.system_prompt = self.prompt_manager.get_prompt("performance_score")
        ic(f"PerformanceScoreAgent initialized with model: {self.model}")

    def process(
        self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate performance scores based on metrics and analytics

        Args:
            input_data: Dictionary containing cycle_metrics and joystick_analytics
            context: Optional context

        Returns:
            Dictionary containing performance scores
        """
        self.log("Generating performance scores with AI", "info")

        cycle_metrics = input_data.get("cycle_metrics", {})
        joystick_analytics = input_data.get("joystick_analytics", {})

        # Build prompt for AI scoring
        prompt = self._build_scoring_prompt(cycle_metrics, joystick_analytics)

        try:
            ic(f"PerformanceScoreAgent calling Gemini with model: {self.model}")
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    response_mime_type=self.response_mime_type,
                    response_schema={
                        "type": "object",
                        "properties": {
                            "productivity_score": {"type": "number"},
                            "productivity_status": {"type": "string"},
                            "control_skill_score": {"type": "number"},
                            "control_skill_status": {"type": "string"},
                            "safety_score": {"type": "number"},
                            "safety_status": {"type": "string"},
                            "overall_assessment": {"type": "string"},
                        },
                        "required": [
                            "productivity_score",
                            "productivity_status",
                            "control_skill_score",
                            "control_skill_status",
                            "safety_score",
                            "safety_status",
                        ],
                    },
                ),
            )

            import json
            scores = json.loads(response.text)

            self.log(
                f"✓ Scores generated: Productivity={scores.get('productivity_score', 0)}, "
                f"Control={scores.get('control_skill_score', 0)}, "
                f"Safety={scores.get('safety_score', 0)}",
                "success",
            )

            return scores

        except Exception as e:
            self.log(f"Failed to generate AI scores: {e}", "warning")
            return self._generate_fallback_scores(cycle_metrics, joystick_analytics)

    def _build_scoring_prompt(
        self, cycle_metrics: Dict[str, Any], joystick_analytics: Dict[str, Any]
    ) -> str:
        """
        Build prompt for AI-based scoring

        Args:
            cycle_metrics: Cycle time metrics
            joystick_analytics: Joystick control analytics

        Returns:
            Formatted prompt string
        """
        prompt = f"""{self.system_prompt}

**Cycle Time Metrics:**
- Average Cycle Time: {cycle_metrics.get('average_cycle_time', 0)}s (Target: {cycle_metrics.get('target_cycle_time', 20)}s)
- Consistency Score: {cycle_metrics.get('consistency_score', 0)}%
- Trend: {cycle_metrics.get('cycle_time_trend', 'Unknown')}
- Total Cycles: {cycle_metrics.get('total_cycles', 0)}

**Joystick Control Analytics:**
- Bimanual Coordination Score (BCS): {joystick_analytics.get('bcs_score', 0)}
- Dual Control Usage: {joystick_analytics.get('control_usage', {}).get('dual_control', 0):.1f}%
- Triple Control Usage: {joystick_analytics.get('control_usage', {}).get('triple_control', 0):.1f}%
- Full Control Usage (4 controls): {joystick_analytics.get('control_usage', {}).get('full_control', 0):.1f}%"""

        return prompt

    def _generate_fallback_scores(
        self, cycle_metrics: Dict[str, Any], joystick_analytics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate fallback scores without AI

        Args:
            cycle_metrics: Cycle time metrics
            joystick_analytics: Joystick control analytics

        Returns:
            Dictionary containing scores
        """
        self.log("Using fallback scoring method", "warning")

        # Simple rule-based scoring
        avg_cycle = cycle_metrics.get("average_cycle_time", 20)
        target = cycle_metrics.get("target_cycle_time", 20)
        consistency = cycle_metrics.get("consistency_score", 50)
        bcs = joystick_analytics.get("bcs_score", 0)
        dual_usage = joystick_analytics.get("control_usage", {}).get("dual_control", 0)

        # Productivity: based on cycle time vs target
        productivity_score = max(0, min(100, 100 - abs(avg_cycle - target) * 3))

        # Control skill: based on BCS and dual control usage
        control_skill_score = (bcs * 100) + (dual_usage * 0.5)
        control_skill_score = max(0, min(100, control_skill_score))

        # Safety: based on consistency
        safety_score = consistency

        def get_status(score):
            if score >= 85:
                return "Excellent"
            elif score >= 70:
                return "Good"
            elif score >= 50:
                return "Satisfactory"
            else:
                return "Needs Improvement"

        return {
            "productivity_score": round(productivity_score, 1),
            "productivity_status": get_status(productivity_score),
            "control_skill_score": round(control_skill_score, 1),
            "control_skill_status": get_status(control_skill_score),
            "safety_score": round(safety_score, 1),
            "safety_status": get_status(safety_score),
            "overall_assessment": "Fallback scoring used due to AI unavailability",
        }


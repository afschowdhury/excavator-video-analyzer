"""AI-powered insights generation agent"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from icecream import ic

from ..base_agent import BaseAgent
from prompts import PromptManager

ic.configureOutput(includeContext=True, prefix="InsightsGeneratorAgent- ")


class InsightsGeneratorAgent(BaseAgent):
    """Agent responsible for generating AI-powered insights and recommendations"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("InsightsGenerator", config)
        load_dotenv()
        api_key = os.getenv("GENAI_API_KEY")
        if not api_key:
            raise ValueError("GENAI_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=api_key)
        
        # Load prompt and config from TOML
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "gemini"
        self.prompt_manager = PromptManager(templates_dir=str(prompt_path))
        
        # Get configuration from TOML file
        prompt_config = self.prompt_manager.get_prompt_config("insights_generator")
        self.model = self.config.get("model", prompt_config.get("model", "gemini-2.0-flash-exp"))
        self.temperature = self.config.get("temperature", prompt_config.get("temperature", 0.4))
        self.response_mime_type = prompt_config.get("response_mime_type", "application/json")
        
        # Get system prompt
        self.system_prompt = self.prompt_manager.get_prompt("insights_generator")
        ic(f"InsightsGeneratorAgent initialized with model: {self.model}")

    def process(
        self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered insights and recommendations

        Args:
            input_data: Dictionary containing all analysis data
            context: Optional context

        Returns:
            Dictionary containing insights and recommendations
        """
        self.log("Generating AI insights with Gemini 2.5 Pro", "info")

        cycle_metrics = input_data.get("cycle_metrics", {})
        joystick_analytics = input_data.get("joystick_analytics", {})
        performance_scores = input_data.get("performance_scores", {})

        # Build comprehensive prompt
        prompt = self._build_insights_prompt(
            cycle_metrics, joystick_analytics, performance_scores
        )

        try:
            ic(f"InsightsGeneratorAgent calling Gemini with model: {self.model}")
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    response_mime_type=self.response_mime_type,
                    response_schema={
                        "type": "object",
                        "properties": {
                            "pattern_recognition": {
                                "type": "object",
                                "properties": {
                                    "control_patterns": {"type": "string"},
                                    "timing_patterns": {"type": "string"},
                                    "efficiency_patterns": {"type": "string"},
                                },
                            },
                            "training_recommendations": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "overall_assessment": {"type": "string"},
                            "proficiency_level": {
                                "type": "string",
                                "enum": ["Beginner", "Intermediate", "Advanced", "Expert"],
                            },
                            "estimated_training_hours": {"type": "number"},
                            "next_focus_areas": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": [
                            "pattern_recognition",
                            "training_recommendations",
                            "overall_assessment",
                            "proficiency_level",
                            "next_focus_areas",
                        ],
                    },
                ),
            )

            import json
            insights = json.loads(response.text)

            self.log("✓ AI insights generated successfully", "success")
            return insights

        except Exception as e:
            self.log(f"Failed to generate AI insights: {e}", "warning")
            return self._generate_fallback_insights(
                cycle_metrics, joystick_analytics, performance_scores
            )

    def _build_insights_prompt(
        self,
        cycle_metrics: Dict[str, Any],
        joystick_analytics: Dict[str, Any],
        performance_scores: Dict[str, Any],
    ) -> str:
        """
        Build comprehensive prompt for insights generation

        Args:
            cycle_metrics: Cycle time metrics
            joystick_analytics: Joystick control analytics
            performance_scores: Performance scores

        Returns:
            Formatted prompt string
        """
        prompt = f"""{self.system_prompt}

**Performance Scores:**
- Productivity: {performance_scores.get('productivity_score', 0)}/100 ({performance_scores.get('productivity_status', 'Unknown')})
- Control Skill: {performance_scores.get('control_skill_score', 0)}/100 ({performance_scores.get('control_skill_status', 'Unknown')})
- Safety: {performance_scores.get('safety_score', 0)}/100 ({performance_scores.get('safety_status', 'Unknown')})

**Cycle Time Analysis:**
- Total Cycles: {cycle_metrics.get('total_cycles', 0)}
- Average Cycle Time: {cycle_metrics.get('average_cycle_time', 0)}s (Target: {cycle_metrics.get('target_cycle_time', 20)}s)
- Consistency Score: {cycle_metrics.get('consistency_score', 0)}%
- Trend: {cycle_metrics.get('cycle_time_trend', 'Unknown')}
- Min/Max: {cycle_metrics.get('min_cycle_time', 0)}s / {cycle_metrics.get('max_cycle_time', 0)}s

**Joystick Control Analytics:**
- Bimanual Coordination Score: {joystick_analytics.get('bcs_score', 0)} (Target: >0.25)
- Dual Control Usage: {joystick_analytics.get('control_usage', {}).get('dual_control', 0):.1f}% (Target: >65%)
- Triple Control Usage: {joystick_analytics.get('control_usage', {}).get('triple_control', 0):.1f}% (Target: >35%)
- Full Control Usage: {joystick_analytics.get('control_usage', {}).get('full_control', 0):.1f}% (Target: >10%)"""

        return prompt

    def _generate_fallback_insights(
        self,
        cycle_metrics: Dict[str, Any],
        joystick_analytics: Dict[str, Any],
        performance_scores: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate fallback insights without AI

        Args:
            cycle_metrics: Cycle time metrics
            joystick_analytics: Joystick control analytics
            performance_scores: Performance scores

        Returns:
            Dictionary containing basic insights
        """
        self.log("Using fallback insights generation", "warning")

        avg_score = (
            performance_scores.get("productivity_score", 0)
            + performance_scores.get("control_skill_score", 0)
            + performance_scores.get("safety_score", 0)
        ) / 3

        if avg_score >= 85:
            proficiency = "Advanced"
            training_hours = 10
        elif avg_score >= 70:
            proficiency = "Intermediate"
            training_hours = 20
        elif avg_score >= 50:
            proficiency = "Beginner"
            training_hours = 40
        else:
            proficiency = "Beginner"
            training_hours = 60

        bcs = joystick_analytics.get("bcs_score", 0)
        dual_usage = joystick_analytics.get("control_usage", {}).get("dual_control", 0)

        recommendations = []
        focus_areas = []

        if bcs < 0.25:
            recommendations.append(
                "Focus on Multi-Joystick Coordination: Practice exercises emphasizing simultaneous control usage"
            )
            focus_areas.append("Bimanual coordination drills")

        if dual_usage < 65:
            recommendations.append(
                "Increase Dual Control Usage: Work on using multiple controls simultaneously during operations"
            )
            focus_areas.append("Simultaneous control exercises")

        if cycle_metrics.get("consistency_score", 0) < 70:
            recommendations.append(
                "Improve Consistency: Practice repetitive cycles to develop muscle memory and timing"
            )
            focus_areas.append("Consistency training with timed cycles")

        if not recommendations:
            recommendations.append("Continue current training regimen and maintain performance levels")
            focus_areas.append("Maintain current skill level with regular practice")

        return {
            "pattern_recognition": {
                "control_patterns": f"BCS of {bcs:.3f} indicates {'good' if bcs > 0.25 else 'developing'} coordination",
                "timing_patterns": f"Cycle time trend: {cycle_metrics.get('cycle_time_trend', 'Unknown')}",
                "efficiency_patterns": f"Consistency score of {cycle_metrics.get('consistency_score', 0):.1f}% indicates {'stable' if cycle_metrics.get('consistency_score', 0) > 70 else 'variable'} performance",
            },
            "training_recommendations": recommendations,
            "overall_assessment": f"The operator demonstrates {proficiency.lower()} proficiency with an overall performance average of {avg_score:.1f}/100. "
            f"Key areas for improvement include control coordination and cycle consistency. With focused training, significant improvement is achievable.",
            "proficiency_level": proficiency,
            "estimated_training_hours": training_hours,
            "next_focus_areas": focus_areas,
        }


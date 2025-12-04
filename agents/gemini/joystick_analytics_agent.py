"""Joystick analytics agent using Gemini AI for report generation"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from icecream import ic

from prompts import PromptManager

from ..base_agent import BaseAgent

ic.configureOutput(includeContext=True, prefix="JoystickAnalyticsAgent- ")


class JoystickAnalyticsAgent(BaseAgent):
    """Agent responsible for processing joystick telemetry and generating analysis reports"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("JoystickAnalytics", config)
        load_dotenv()
        api_key = os.getenv("GENAI_API_KEY")
        if not api_key:
            raise ValueError("GENAI_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=api_key)
        
        # Load prompt and config from TOML
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "gemini"
        self.prompt_manager = PromptManager(templates_dir=str(prompt_path))
        
        # Get configuration from TOML file
        prompt_config = self.prompt_manager.get_prompt_config("joystick_analyzer")
        self.model = self.config.get("model", prompt_config.get("model", "gemini-2.5-pro"))
        self.temperature = self.config.get("temperature", prompt_config.get("temperature", 0.2))
        
        # Get system prompt
        self.system_prompt = self.prompt_manager.get_prompt("joystick_analyzer")
        ic(f"JoystickAnalyticsAgent initialized with model: {self.model}")

    def process(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process joystick data and generate markdown report using Gemini AI

        Args:
            input_data: Path to joystick data directory or stats.json file
            context: Optional context

        Returns:
            Dictionary containing markdown report and structured data
        """
        self.log(f"Processing joystick data from {input_data}", "info")

        # Determine paths and load data
        stats_data = self._load_stats_data(input_data)
        if not stats_data:
            return self._generate_fallback_response()

        # Generate markdown report using Gemini
        markdown_report = self._generate_markdown_report(stats_data)

        # Extract structured data for backward compatibility
        si_matrix = stats_data.get("SI", {})
        bcs_score = stats_data.get("BCS", 0)
        control_usage_raw = stats_data.get("control_usage", {})
        
        control_usage = {
            "single_control": 100.0,
            "dual_control": control_usage_raw.get("2_controls", 0),
            "triple_control": control_usage_raw.get("3_controls", 0),
            "full_control": control_usage_raw.get("4_controls", 0),
        }

        # Prepare image paths (for potential future use)
        base_dir = os.path.dirname(input_data) if os.path.isfile(input_data) else input_data
        heatmap_path = os.path.join(base_dir, "SI_Heatmap.png")
        control_usage_path = os.path.join(base_dir, "control_usage.png")

        result = {
            "markdown_report": markdown_report,
            "si_matrix": si_matrix,
            "bcs_score": round(bcs_score, 3),
            "control_usage": control_usage,
            "heatmap_path": heatmap_path if os.path.exists(heatmap_path) else None,
            "control_usage_path": control_usage_path if os.path.exists(control_usage_path) else None,
        }

        self.log(f"✓ Analytics processed: BCS={bcs_score:.3f}", "success")
        return result

    def _load_stats_data(self, input_data: str) -> Optional[Dict[str, Any]]:
        """
        Load stats.json data from input path

        Args:
            input_data: Path to directory or stats.json file

        Returns:
            Dictionary containing stats data or None on error
        """
        # Determine stats.json path
        if os.path.isdir(input_data):
            stats_path = os.path.join(input_data, "stats.json")
        else:
            stats_path = input_data

        try:
            with open(stats_path, "r") as f:
                return json.load(f)
        except Exception as e:
            self.log(f"Failed to load stats.json: {e}", "error")
            return None

    def _generate_markdown_report(self, stats_data: Dict[str, Any]) -> str:
        """
        Generate markdown report using Gemini AI

        Args:
            stats_data: Dictionary containing SI, BCS, and control_usage data

        Returns:
            Markdown formatted report string
        """
        self.log("Generating markdown report with Gemini AI", "info")

        # Format the JSON data as a string for the prompt
        json_data = json.dumps(stats_data, indent=2)

        # Build the prompt
        prompt = f"""{self.system_prompt}

### INPUT JSON DATA:
```json
{json_data}
```

Please generate the Joystick Coordination Analysis report now."""

        try:
            ic(f"JoystickAnalyticsAgent calling Gemini with model: {self.model}")
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                ),
            )

            markdown_report = response.text
            self.log("✓ Markdown report generated successfully", "success")
            ic(markdown_report)
            return markdown_report

        except Exception as e:
            self.log(f"Failed to generate AI report: {e}", "warning")
            return self._generate_fallback_markdown(stats_data)

    def _generate_fallback_markdown(self, stats_data: Dict[str, Any]) -> str:
        """
        Generate fallback markdown report without AI

        Args:
            stats_data: Dictionary containing joystick analytics data

        Returns:
            Basic markdown report string
        """
        self.log("Using fallback markdown generation", "warning")

        si_matrix = stats_data.get("SI", {})
        bcs_score = stats_data.get("BCS", 0)
        control_usage = stats_data.get("control_usage", {})

        # Extract SI values with safe access
        def get_si(control1: str, control2: str) -> float:
            return si_matrix.get(control1, {}).get(control2, 0.0) or 0.0

        swing_bucket = get_si("Swing", "Bucket")
        swing_boom = get_si("Swing", "Boom")
        arm_bucket = get_si("Arm", "Bucket")
        arm_boom = get_si("Arm", "Boom")

        # BCS interpretation
        if bcs_score < 0.30:
            bcs_interp = "Developing coordination; operator frequently isolates hand movements."
        elif bcs_score < 0.60:
            bcs_interp = "Moderate coordination; operator is beginning to blend movements."
        else:
            bcs_interp = "Expert coordination; fluid simultaneous operation."

        # Control usage status
        def get_status(value: float, benchmark: float) -> str:
            if value >= benchmark:
                return "Strong"
            elif value >= benchmark - 5:
                return "Average"
            else:
                return "Needs Improvement"

        dual_usage = control_usage.get("2_controls", 0)
        triple_usage = control_usage.get("3_controls", 0)
        full_usage = control_usage.get("4_controls", 0)

        dual_status = get_status(dual_usage, 65)
        triple_status = get_status(triple_usage, 35)
        full_status = get_status(full_usage, 10)

        # Key finding
        if dual_usage > 60 and (triple_usage < 30 or full_usage < 5):
            key_finding = "The operator has mastered basic dual-control movements but struggles with complex, compound maneuvers requiring three or four simultaneous controls."
        elif dual_usage < 50:
            key_finding = "Focus on developing basic fluidity with dual-control operations before advancing to more complex multi-control maneuvers."
        else:
            key_finding = "The operator demonstrates expert efficiency across all control configurations, showing mastery of complex multi-joystick coordination."

        markdown = f"""# Joystick Coordination Analysis

## Multi-Joystick Coordination
The Simultaneity Index (SI) Matrix shows how frequently different controls are used together. Higher values indicate better coordination between specific control pairs.

| Control Pair | Function Mapping | Simultaneity Index (SI) |
| :--- | :--- | :--- |
| **Left X + Right X** | (Swing + Bucket) | {swing_bucket:.3f} |
| **Left X + Right Y** | (Swing + Boom) | {swing_boom:.3f} |
| **Left Y + Right X** | (Arm + Bucket) | {arm_bucket:.3f} |
| **Left Y + Right Y** | (Arm + Boom) | {arm_boom:.3f} |

---

## Bimanual Coordination Score (BCS)
**Overall BCS:** {bcs_score:.3f}
**Interpretation:** {bcs_interp}

---

## Simultaneous Control Usage Distribution

| Control Configuration | % of Active Time | Expert Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **Single Control (≥1)** | 100.0% | 100% | N/A |
| **Dual Control (≥2)** | {dual_usage:.1f}% | >65% | {dual_status} |
| **Triple Control (≥3)** | {triple_usage:.1f}% | >35% | {triple_status} |
| **Full Control (4)** | {full_usage:.1f}% | >10% | {full_status} |

**Key Finding:** {key_finding}
"""

        return markdown

    def _generate_fallback_response(self) -> Dict[str, Any]:
        """
        Generate complete fallback response when data loading fails

        Returns:
            Dictionary with default values
        """
        self.log("Using complete fallback response", "warning")
        
        fallback_markdown = """# Joystick Coordination Analysis

## Error
Unable to load joystick telemetry data. Please ensure stats.json file exists and is properly formatted.
"""

        return {
            "markdown_report": fallback_markdown,
            "si_matrix": {},
            "bcs_score": 0.0,
            "control_usage": {
                "single_control": 100.0,
                "dual_control": 0.0,
                "triple_control": 0.0,
                "full_control": 0.0,
            },
            "heatmap_path": None,
            "control_usage_path": None,
        }


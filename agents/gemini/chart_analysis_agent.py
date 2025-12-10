"""Chart analysis agent using Gemini Vision API for visual insights"""

import base64
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

ic.configureOutput(includeContext=True, prefix="ChartAnalysisAgent- ")


class ChartAnalysisAgent(BaseAgent):
    """Agent responsible for analyzing chart images using Gemini Vision API"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ChartAnalysis", config)
        load_dotenv()
        api_key = os.getenv("GENAI_API_KEY")
        if not api_key:
            raise ValueError("GENAI_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=api_key)
        
        # Load prompt and config from TOML
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "gemini"
        self.prompt_manager = PromptManager(templates_dir=str(prompt_path))
        
        # Get configuration from TOML file
        prompt_config = self.prompt_manager.get_prompt_config("chart_analyzer")
        self.model = self.config.get("model", prompt_config.get("model", "gemini-2.0-flash-exp"))
        self.temperature = self.config.get("temperature", prompt_config.get("temperature", 0.3))
        
        # Get system prompt
        self.system_prompt = self.prompt_manager.get_prompt("chart_analyzer")
        ic(f"ChartAnalysisAgent initialized with model: {self.model}")

    def process(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze chart images and generate visual insights report

        Args:
            input_data: Path to joystick data directory containing chart images
            context: Optional context dictionary. Can contain 'trial_id' for new data structure

        Returns:
            Dictionary containing markdown report and base64-encoded images
        """
        # Extract trial_id from context if provided
        trial_id = context.get("trial_id") if context else None
        
        if trial_id:
            self.log(f"Analyzing charts for trial ID: {trial_id}", "info")
        else:
            self.log(f"Analyzing charts from {input_data}", "info")

        # Determine image paths based on trial_id or old structure
        if trial_id:
            # New folder structure with trial_id
            base_dir = Path(__file__).parent.parent.parent / "data" / "joystick_data"
            heatmap_path = str(base_dir / "SI_Heatmaps" / f"SI_Heatmap_{trial_id}.png")
            control_usage_path = str(base_dir / "Control_Usage" / f"control_usage_{trial_id}.png")
        else:
            # Old structure for backward compatibility
            if os.path.isdir(input_data):
                base_dir = input_data
            else:
                base_dir = os.path.dirname(input_data)

            heatmap_path = os.path.join(base_dir, "SI_Heatmap.png")
            control_usage_path = os.path.join(base_dir, "control_usage.png")

        # Check if images exist
        if not os.path.exists(heatmap_path) or not os.path.exists(control_usage_path):
            self.log(f"Chart images not found at {heatmap_path} or {control_usage_path}, using fallback", "warning")
            return self._generate_fallback_response()

        # Load and encode images
        heatmap_base64 = self._load_and_encode_image(heatmap_path)
        control_usage_base64 = self._load_and_encode_image(control_usage_path)

        if not heatmap_base64 or not control_usage_base64:
            self.log("Failed to encode images, using fallback", "warning")
            return self._generate_fallback_response()

        # Generate visual analysis using Gemini Vision
        markdown_report = self._analyze_charts_with_vision(
            heatmap_base64, control_usage_base64
        )

        result = {
            "chart_analysis_markdown": markdown_report,
            "heatmap_image_base64": f"data:image/png;base64,{heatmap_base64}",
            "control_usage_image_base64": f"data:image/png;base64,{control_usage_base64}",
        }

        self.log("✓ Chart analysis completed", "success")
        return result

    def _load_and_encode_image(self, image_path: str) -> Optional[str]:
        """
        Load image and encode to base64

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded string or None on error
        """
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
                return base64.b64encode(image_data).decode("utf-8")
        except Exception as e:
            self.log(f"Failed to encode image {image_path}: {e}", "error")
            return None

    def _analyze_charts_with_vision(
        self, heatmap_base64: str, control_usage_base64: str
    ) -> str:
        """
        Analyze charts using Gemini Vision API

        Args:
            heatmap_base64: Base64 encoded SI heatmap image
            control_usage_base64: Base64 encoded control usage chart

        Returns:
            Markdown formatted analysis report
        """
        self.log("Analyzing charts with Gemini Vision API", "info")

        try:
            ic(f"ChartAnalysisAgent calling Gemini Vision with model: {self.model}")
            
            # Prepare the multi-modal content with both images
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    self.system_prompt,
                    types.Part.from_bytes(
                        data=base64.b64decode(heatmap_base64),
                        mime_type="image/png"
                    ),
                    "This is the Simultaneity Index (SI) Heatmap showing control coordination patterns.",
                    types.Part.from_bytes(
                        data=base64.b64decode(control_usage_base64),
                        mime_type="image/png"
                    ),
                    "This is the Simultaneous Control Usage chart showing percentage of time using multiple controls.",
                    "\nPlease analyze these charts and generate a comprehensive visual analysis report following the template structure."
                ],
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                ),
            )

            markdown_report = response.text
            self.log("✓ Vision analysis completed successfully", "success")
            return markdown_report

        except Exception as e:
            self.log(f"Vision API failed: {e}", "warning")
            return self._generate_fallback_markdown()

    def _generate_fallback_markdown(self) -> str:
        """
        Generate fallback markdown report without vision analysis

        Returns:
            Basic markdown report
        """
        self.log("Using fallback chart analysis", "warning")
        
        markdown = """# Visual Chart Analysis

## Overview
Visual chart analysis is currently unavailable. The system was unable to process the chart images using the vision API.

## Simultaneity Index (SI) Heatmap
The SI Heatmap displays coordination patterns between different excavator controls. Darker colors indicate stronger simultaneity (more frequent coordinated use).

**Key Observations:**
- Analysis requires vision API to interpret color patterns and values
- Typical patterns show stronger coordination between related controls (e.g., Arm-Bucket)

## Control Usage Distribution
The control usage chart shows the percentage of time the operator uses different numbers of controls simultaneously.

**Key Observations:**
- Expert operators typically show >65% dual control usage
- Triple control usage above 35% indicates advanced skill
- Full 4-control coordination above 10% demonstrates mastery

## Recommendations
For detailed visual analysis, please ensure the vision API is properly configured and images are accessible.
"""
        return markdown

    def _generate_fallback_response(self) -> Dict[str, Any]:
        """
        Generate complete fallback response when images not found

        Returns:
            Dictionary with fallback data
        """
        self.log("Using complete fallback response", "warning")
        
        return {
            "chart_analysis_markdown": self._generate_fallback_markdown(),
            "heatmap_image_base64": None,
            "control_usage_image_base64": None,
        }


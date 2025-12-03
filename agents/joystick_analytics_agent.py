"""Joystick analytics agent for processing control data"""

import json
import os
from typing import Any, Dict, Optional
import base64

from .base_agent import BaseAgent


class JoystickAnalyticsAgent(BaseAgent):
    """Agent responsible for processing joystick telemetry and control analytics"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("JoystickAnalytics", config)

    def process(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process joystick data from JSON file

        Args:
            input_data: Path to joystick data directory or stats.json file
            context: Optional context

        Returns:
            Dictionary containing formatted joystick analytics
        """
        self.log(f"Processing joystick data from {input_data}", "info")

        # Determine paths
        if os.path.isdir(input_data):
            stats_path = os.path.join(input_data, "stats.json")
            heatmap_path = os.path.join(input_data, "SI_Heatmap.png")
            control_usage_path = os.path.join(input_data, "control_usage.png")
        else:
            stats_path = input_data
            base_dir = os.path.dirname(input_data)
            heatmap_path = os.path.join(base_dir, "SI_Heatmap.png")
            control_usage_path = os.path.join(base_dir, "control_usage.png")

        # Load stats.json
        try:
            with open(stats_path, "r") as f:
                stats = json.load(f)
        except Exception as e:
            self.log(f"Failed to load stats.json: {e}", "error")
            return self._generate_fallback_data()

        # Extract data
        si_matrix = stats.get("SI", {})
        bcs_score = stats.get("BCS", 0)
        control_usage = stats.get("control_usage", {})

        # Format SI matrix for display
        si_formatted = self._format_si_matrix(si_matrix)

        # Format control usage
        control_usage_formatted = {
            "single_control": 100.0,  # Always 100%
            "dual_control": control_usage.get("2_controls", 0),
            "triple_control": control_usage.get("3_controls", 0),
            "full_control": control_usage.get("4_controls", 0),
        }

        # Load and encode images
        heatmap_image = self._load_image(heatmap_path)
        control_usage_image = self._load_image(control_usage_path)

        analytics = {
            "si_matrix": si_matrix,
            "si_formatted": si_formatted,
            "bcs_score": round(bcs_score, 3),
            "control_usage": control_usage_formatted,
            "heatmap_image": heatmap_image,
            "control_usage_image": control_usage_image,
            "heatmap_path": heatmap_path if os.path.exists(heatmap_path) else None,
            "control_usage_path": control_usage_path if os.path.exists(control_usage_path) else None,
        }

        self.log(f"✓ Analytics processed: BCS={bcs_score:.3f}", "success")
        return analytics

    def _format_si_matrix(self, si_matrix: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Format SI matrix for HTML display

        Args:
            si_matrix: Raw SI matrix data

        Returns:
            Formatted matrix data
        """
        # Create a clean matrix for display
        # Expected structure: Boom, Arm, Bucket vs Swing
        controls = ["Boom", "Arm", "Bucket"]
        
        formatted = {
            "left_y_vs_left_x": si_matrix.get("Boom", {}).get("Swing", 0) or 0,
            "left_y_vs_right_x": si_matrix.get("Boom", {}).get("Arm", 0) or 0,
            "left_y_vs_right_y": si_matrix.get("Boom", {}).get("Bucket", 0) or 0,
        }

        # Also create a full matrix table
        matrix_table = []
        for control in controls:
            row = {
                "control": control,
                "left_x": round(si_matrix.get(control, {}).get("Swing", 0) or 0, 3),
                "right_x": round(si_matrix.get(control, {}).get("Arm", 0) or 0, 3),
                "right_y": round(si_matrix.get(control, {}).get("Bucket", 0) or 0, 3),
            }
            matrix_table.append(row)

        return {
            "summary": formatted,
            "table": matrix_table,
        }

    def _load_image(self, image_path: str) -> Optional[str]:
        """
        Load image and convert to base64 for embedding

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded image string or None
        """
        if not os.path.exists(image_path):
            self.log(f"Image not found: {image_path}", "warning")
            return None

        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode("utf-8")
                return f"data:image/png;base64,{base64_data}"
        except Exception as e:
            self.log(f"Failed to load image {image_path}: {e}", "warning")
            return None

    def _generate_fallback_data(self) -> Dict[str, Any]:
        """
        Generate fallback data when stats.json is not available

        Returns:
            Default analytics data
        """
        self.log("Using fallback joystick data", "warning")
        return {
            "si_matrix": {},
            "si_formatted": {"summary": {}, "table": []},
            "bcs_score": 0,
            "control_usage": {
                "single_control": 100.0,
                "dual_control": 0,
                "triple_control": 0,
                "full_control": 0,
            },
            "heatmap_image": None,
            "control_usage_image": None,
            "heatmap_path": None,
            "control_usage_path": None,
        }


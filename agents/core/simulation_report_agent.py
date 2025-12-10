"""Agent for extracting metrics from simulation report PDFs"""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
from pypdf import PdfReader

from ..base_agent import BaseAgent


class SimulationReportAgent(BaseAgent):
    """Agent responsible for extracting simulation metrics from PDF reports"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("SimulationReportAgent", config)
        self.reports_dir = Path(
            self.config.get("reports_dir", "simulation_report")
        )

    def process(
        self, input_data: Any, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract simulation metrics from PDF report matching the video ID

        Args:
            input_data: Video path or video ID string
            context: Optional context from previous agents

        Returns:
            Dictionary containing extracted metrics:
            {
                'productivity': float (in m³/hr),
                'fuel_burned': float (in L),
                'time_swinging_left': float (in sec),
                'time_swinging_right': float (in sec),
                'found': bool
            }
        """
        # Extract ID from input
        video_id = self._extract_video_id(input_data)
        
        if not video_id:
            self.log("Could not extract video ID from input", "warning")
            return self._empty_result()

        self.log(f"Extracted video ID: {video_id}", "info")

        # Find PDF report
        pdf_path = self.reports_dir / f"{video_id}.pdf"
        
        if not pdf_path.exists():
            self.log(f"No simulation report found for ID: {video_id}", "warning")
            return self._empty_result()

        self.log(f"Found report: {pdf_path}", "info")

        # Extract metrics from PDF
        try:
            metrics = self._extract_metrics_from_pdf(pdf_path)
            metrics['found'] = True
            metrics['video_id'] = video_id
            self.log(
                f"✓ Extracted metrics: Productivity={metrics.get('productivity', 'N/A')}m³/hr, "
                f"Fuel={metrics.get('fuel_burned', 'N/A')}L, "
                f"Left={metrics.get('time_swinging_left', 'N/A')}s, "
                f"Right={metrics.get('time_swinging_right', 'N/A')}s",
                "success"
            )
            return metrics
        except Exception as e:
            self.log(f"Error extracting metrics: {e}", "error")
            return self._empty_result()

    def _extract_video_id(self, input_data: Any) -> Optional[str]:
        """
        Extract video ID from various input formats

        Args:
            input_data: Video path, filename, or ID string

        Returns:
            Video ID string or None
        """
        if isinstance(input_data, str):
            # If it's a path, extract filename
            path = Path(input_data)
            filename = path.stem  # Gets filename without extension
            
            # Try to extract ID pattern (alphanumeric)
            # Handles cases like "B6.mp4" -> "B6", "2.mp4" -> "2", etc.
            match = re.search(r'([A-Za-z]?\d+[A-Za-z]?)', filename)
            if match:
                return match.group(1)
            
            # If no pattern found, use the filename stem as-is
            return filename
        
        return None

    def _extract_metrics_from_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract fuel, swing time, and productivity metrics from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with extracted metrics
        """
        # Read PDF
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # Extract metrics using regex patterns
        metrics = {}

        # Pattern for "Productivity" - format: "Productivity 585.66 m³/hr"
        productivity_pattern = r'Productivity\s+([\d.]+)\s+m³/hr'
        productivity_match = re.search(productivity_pattern, text)
        if productivity_match:
            metrics['productivity'] = float(productivity_match.group(1))

        # Pattern for "Fuel Burned" - format: "Fuel Burned 1.41 L"
        fuel_pattern = r'Fuel Burned\s+([\d.]+)\s+L'
        fuel_match = re.search(fuel_pattern, text)
        if fuel_match:
            metrics['fuel_burned'] = float(fuel_match.group(1))

        # Pattern for "Time Spent Swinging Left"
        # Format 1: "Time Spent Swinging Left 44 sec"
        # Format 2: "Time Spent Swinging Left 00:01:01 mins"
        left_pattern_sec = r'Time Spent Swinging Left\s+([\d.]+)\s+sec'
        left_pattern_mins = r'Time Spent Swinging Left\s+([\d:]+)\s+mins'
        
        left_match = re.search(left_pattern_sec, text)
        if left_match:
            metrics['time_swinging_left'] = float(left_match.group(1))
        else:
            left_match = re.search(left_pattern_mins, text)
            if left_match:
                # Convert mm:ss to seconds
                time_str = left_match.group(1)
                metrics['time_swinging_left'] = self._convert_time_to_seconds(time_str)

        # Pattern for "Time Spent Swinging Right"
        # Format 1: "Time Spent Swinging Right 43 sec"
        # Format 2: "Time Spent Swinging Right 00:01:05 mins"
        right_pattern_sec = r'Time Spent Swinging Right\s+([\d.]+)\s+sec'
        right_pattern_mins = r'Time Spent Swinging Right\s+([\d:]+)\s+mins'
        
        right_match = re.search(right_pattern_sec, text)
        if right_match:
            metrics['time_swinging_right'] = float(right_match.group(1))
        else:
            right_match = re.search(right_pattern_mins, text)
            if right_match:
                # Convert mm:ss to seconds
                time_str = right_match.group(1)
                metrics['time_swinging_right'] = self._convert_time_to_seconds(time_str)

        return metrics

    def _convert_time_to_seconds(self, time_str: str) -> float:
        """
        Convert time string in format HH:MM:SS or MM:SS to seconds

        Args:
            time_str: Time string (e.g., "00:01:01" or "01:05")

        Returns:
            Time in seconds
        """
        parts = time_str.split(':')
        if len(parts) == 3:
            # HH:MM:SS format
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:
            # MM:SS format
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        else:
            return 0.0

    def _empty_result(self) -> Dict[str, Any]:
        """
        Return empty result structure when metrics cannot be extracted

        Returns:
            Dictionary with None values and found=False
        """
        return {
            'productivity': None,
            'fuel_burned': None,
            'time_swinging_left': None,
            'time_swinging_right': None,
            'found': False,
            'video_id': None
        }


"""HTML Report Analyzer - Main class for generating HTML training reports"""

import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from agents.report_orchestrator_agent import ReportOrchestrator


class HTMLReportAnalyzer:
    """Main analyzer class for generating HTML operator training reports"""

    def __init__(self, api_key: Optional[str] = None, reports_dir: str = "reports"):
        """
        Initialize the HTMLReportAnalyzer with Gemini API credentials

        Args:
            api_key: Gemini API key (optional, will try to load from .env)
            reports_dir: Directory to save generated reports
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("GENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Please provide it or set GENAI_API_KEY in .env file"
            )

        self.reports_dir = reports_dir
        self.console = Console()
        
        # Create reports directory if it doesn't exist
        Path(self.reports_dir).mkdir(parents=True, exist_ok=True)

        # Initialize orchestrator
        self.orchestrator = ReportOrchestrator()

    def generate_html_report(
        self,
        cycle_data: List[Dict[str, Any]],
        joystick_data_path: str,
        operator_info: Optional[Dict[str, Any]] = None,
        save_to_file: bool = True,
        filename: Optional[str] = None,
    ) -> str:
        """
        Generate an HTML training report from cycle data and joystick analytics

        Args:
            cycle_data: List of cycle dictionaries from video_analyzer.parse_cycle_data()
            joystick_data_path: Path to joystick data directory or stats.json file
            operator_info: Dictionary containing operator metadata:
                - operator_name: Name of the operator
                - equipment: Equipment model/type
                - exercise_date: Date of exercise
                - session_duration: Duration of session
            save_to_file: Whether to save the report to an HTML file
            filename: Custom filename for the report (without extension)

        Returns:
            HTML report string
        """
        self.console.print(
            "\n[bold cyan]Starting HTML Report Generation[/bold cyan]\n"
        )

        # Set default operator info if not provided
        if operator_info is None:
            operator_info = {}

        # Ensure required fields exist
        operator_info.setdefault("operator_name", "Unknown Operator")
        operator_info.setdefault("equipment", "Excavator")
        operator_info.setdefault("exercise_date", datetime.now().strftime("%Y-%m-%d"))
        operator_info.setdefault("session_duration", "N/A")

        try:
            # Run the report generation pipeline
            result = self.orchestrator.run_pipeline(
                cycle_data=cycle_data,
                joystick_data_path=joystick_data_path,
                operator_info=operator_info,
            )

            html_report = result["html_report"]

            # Save to file if requested
            if save_to_file:
                filepath = self._save_report(html_report, filename, operator_info)
                self.console.print(
                    f"\n[bold green]✓ Report saved to:[/bold green] {filepath}\n"
                )

            return html_report

        except Exception as e:
            self.console.print(f"[bold red]Error generating report: {e}[/bold red]")
            raise

    def _save_report(
        self,
        html_content: str,
        filename: Optional[str],
        operator_info: Dict[str, Any],
    ) -> str:
        """
        Save HTML report to file

        Args:
            html_content: HTML report content
            filename: Optional custom filename
            operator_info: Operator information for default filename

        Returns:
            Path to saved file
        """
        if filename:
            # Use custom filename
            if not filename.endswith(".html"):
                filename = f"{filename}.html"
        else:
            # Generate filename from operator name and timestamp
            operator_name = operator_info.get("operator_name", "unknown").replace(
                " ", "_"
            )
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"training_report_{operator_name}_{timestamp}.html"

        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        return filepath

    def get_pipeline_data(self) -> Dict[str, Any]:
        """
        Get intermediate pipeline data from the orchestrator

        Returns:
            Dictionary containing all pipeline stage outputs
        """
        return self.orchestrator.get_pipeline_data()

    def reset(self):
        """Reset the orchestrator pipeline"""
        self.orchestrator.reset()


def main():
    """Main entry point for testing the HTML report analyzer"""
    try:
        # Example usage
        analyzer = HTMLReportAnalyzer()

        # Example cycle data (this would normally come from video_analyzer.parse_cycle_data())
        example_cycle_data = [
            {
                "cycle_num": 1,
                "start_time": "00:10",
                "end_time": "00:28",
                "start_time_sec": 10,
                "end_time_sec": 28,
                "duration": 18,
                "notes": "Smooth operation",
            },
            {
                "cycle_num": 2,
                "start_time": "00:30",
                "end_time": "00:50",
                "start_time_sec": 30,
                "end_time_sec": 50,
                "duration": 20,
                "notes": "Good coordination",
            },
        ]

        # Path to joystick data
        joystick_data_path = "data/joystick_data"

        # Operator information
        operator_info = {
            "operator_name": "Test Operator",
            "equipment": "Excavator CAT 320",
            "exercise_date": "2025-12-03",
            "session_duration": "60 minutes",
        }

        # Generate report
        html_report = analyzer.generate_html_report(
            cycle_data=example_cycle_data,
            joystick_data_path=joystick_data_path,
            operator_info=operator_info,
            save_to_file=True,
        )

        print("\n" + "=" * 80)
        print("HTML Report Generated Successfully!")
        print("=" * 80)

    except Exception as e:
        console = Console()
        console.print(f"[bold red]An error occurred: {e}[/bold red]")


if __name__ == "__main__":
    main()


import os
from datetime import datetime
from pathlib import Path

from rich.console import Console


class ReportSaver:
    def __init__(self, reports_dir="reports"):
        """
        Initialize the ReportSaver with a directory for saving reports

        Args:
            reports_dir (str): Directory to save generated reports
        """
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        self.console = Console()

    def save_report(self, report_text, filename=None):
        """
        Save the report text to a markdown file

        Args:
            report_text (str): The report text to save
            filename (str, optional): Custom filename for the report

        Returns:
            Path: Path to the saved file
        """
        if not report_text:
            self.console.print("[bold red]No report text to save")
            return None

        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"excavator_report_{timestamp}.md"
            elif not filename.endswith(".md"):
                filename = f"{filename}.md"

            file_path = self.reports_dir / filename

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report_text)

            self.console.print(f"[bold green]Report saved to: {file_path}")
            return file_path
        except Exception as e:
            self.console.print(f"[bold red]Error saving report: {e}")
            return None

    def get_reports_dir(self):
        """
        Get the current reports directory

        Returns:
            Path: Path object for the reports directory
        """
        return self.reports_dir

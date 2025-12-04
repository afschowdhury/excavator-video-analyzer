import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types
from icecream import ic
from rich.console import Console
from rich.markdown import Markdown

from config import VIDEO_METADATA_CONFIG
from prompts import PromptManager
from .report_saver import ReportSaver

ic.configureOutput(includeContext=True, prefix="- DEBUG -")



class VideoAnalyzer:
    def __init__(self, api_key=None, reports_dir="reports"):
        """
        Initialize the VideoAnalyzer with Gemini API credentials

        Args:
            api_key (str, optional): Gemini API key. If not provided, will try to load from .env file
            reports_dir (str): Directory to save generated reports
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("GENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Please provide it or set GENAI_API_KEY in .env file"
            )

        self.client = genai.Client(api_key=self.api_key)
        self.report_saver = ReportSaver(reports_dir)
        self.prompt_manager = PromptManager()
        self.console = Console()

    def generate_report(
        self,
        video_url,
        model="gemini-2.5-pro",
        prompt_type="simple",
        save_to_file=True,
        filename=None,
        video_metadata_fps=None,
        video_metadata_start_offset=None,
        video_metadata_end_offset=None,
    ):
        """
        Generate a performance report from a video URL

        Args:
            video_url (str): URL of the video to analyze
            model (str): Gemini model to use
            prompt_type (str): Type of prompt to use ('simple' or 'detailed')
            save_to_file (bool): Whether to save the report to a markdown file
            filename (str, optional): Custom filename for the report
            video_metadata_fps (int, optional): Frame sampling rate (defaults to config value)
            video_metadata_start_offset (str, optional): Video start time offset (defaults to config value)
            video_metadata_end_offset (str, optional): Video end time offset (defaults to config value)

        Returns:
            str: Generated report in markdown format
        """
        system_instruction = self.prompt_manager.get_prompt(prompt_type)
        ic(system_instruction)
        prompt_config = self.prompt_manager.get_prompt_config(prompt_type)
        ic(prompt_config)

        # Use centralized config values with optional overrides
        fps = video_metadata_fps if video_metadata_fps is not None else VIDEO_METADATA_CONFIG["fps"]
        
        # Handle time offsets - empty string means full video (no time constraints)
        if video_metadata_start_offset == '' and video_metadata_end_offset == '':
            # Full video mode - don't specify time offsets
            start_offset = None
            end_offset = None
        else:
            start_offset = video_metadata_start_offset if video_metadata_start_offset is not None else VIDEO_METADATA_CONFIG["start_offset"]
            end_offset = video_metadata_end_offset if video_metadata_end_offset is not None else VIDEO_METADATA_CONFIG["end_offset"]

        with self.console.status("[bold green]Generating report...") as status:
            try:
                # Build video metadata based on whether we have time constraints
                if start_offset is None and end_offset is None:
                    # Full video - only specify fps
                    video_part = types.Part(
                        file_data=types.FileData(file_uri=video_url),
                        video_metadata=types.VideoMetadata(fps=fps)
                    )
                else:
                    # Time-constrained - specify fps and offsets
                    video_part = types.Part(
                        file_data=types.FileData(file_uri=video_url),
                        video_metadata=types.VideoMetadata(
                            fps=fps,
                            start_offset=start_offset,
                            end_offset=end_offset
                        )
                    )
                
                response = self.client.models.generate_content(
                    model=model,
                    contents=types.Content(
                        parts=[
                            video_part,
                            types.Part(text="Please extract the excavation cycle timestamps from the video"),
                        ]
                    ),
                    config=types.GenerateContentConfig(
                        temperature=prompt_config.get("temperature", 0.0),
                        system_instruction=system_instruction,
                    ),
                )
                ic(response)

                report_text = response.text

                if save_to_file:
                    self.report_saver.save_report(report_text, filename)

                return report_text
            except Exception as e:
                self.console.print(f"[bold red]Error generating report: {e}")
                return None

    def display_report(self, report_text):
        """
        Display the report text as formatted markdown

        Args:
            report_text (str): The report text to display
        """
        if report_text:
            self.console.print(Markdown(report_text))
        else:
            self.console.print("[bold red]No report to display")

    def list_available_prompts(self):
        """
        List all available prompt types and their descriptions

        Returns:
            Dict[str, str]: Dictionary of prompt types and their descriptions
        """
        return self.prompt_manager.list_prompts()

    @staticmethod
    def parse_cycle_data(report_text):
        """
        Parse cycle time data from a markdown report

        Args:
            report_text (str): The markdown report text containing cycle time table

        Returns:
            list: List of dictionaries with cycle data, each containing:
                  - cycle_num: Cycle number
                  - start_time: Start time in MM:SS format
                  - end_time: End time in MM:SS format
                  - duration: Duration in seconds
                  - notes: Brief observation notes
        """
        if not report_text:
            return []

        cycles = []
        
        # Look for table rows with cycle data
        # Pattern: | cycle_num | MM:SS | MM:SS | notes |
        pattern = r'\|\s*(\d+)\s*\|\s*(\d+):(\d+)\s*\|\s*(\d+):(\d+)\s*\|([^|]*)\|'
        
        matches = re.finditer(pattern, report_text)
        
        for match in matches:
            cycle_num = int(match.group(1))
            start_min = int(match.group(2))
            start_sec = int(match.group(3))
            end_min = int(match.group(4))
            end_sec = int(match.group(5))
            notes = match.group(6).strip()
            
            # Convert to seconds
            start_time_sec = start_min * 60 + start_sec
            end_time_sec = end_min * 60 + end_sec
            duration = end_time_sec - start_time_sec
            
            cycles.append({
                'cycle_num': cycle_num,
                'start_time': f"{start_min:02d}:{start_sec:02d}",
                'end_time': f"{end_min:02d}:{end_sec:02d}",
                'start_time_sec': start_time_sec,
                'end_time_sec': end_time_sec,
                'duration': duration,
                'notes': notes
            })
        
        return cycles


def main():
    """Main entry point for the video analyzer"""
    try:
        analyzer = VideoAnalyzer()
        video_url = "https://youtu.be/QdWnkH3TGDU"

        # Just call generate_report, don't wrap it in another status spinner
        report = analyzer.generate_report(
            video_url, prompt_type="simple", save_to_file=True
        )
        analyzer.display_report(report)

        improved_report = analyzer.generate_report(
            video_url,
            prompt_type="detailed",
            save_to_file=True,
            filename="detailed_analysis",
        )
        analyzer.display_report(improved_report)

    except Exception as e:
        console = Console()
        console.print(f"[bold red]An error occurred: {e}")


if __name__ == "__main__":
    main()

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from rich.console import Console
from rich.markdown import Markdown

from prompts import PromptManager
from report_saver import ReportSaver


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
        model="gemini-2.5-pro-exp-03-25",
        prompt_type="simple",
        save_to_file=True,
        filename=None,
    ):
        """
        Generate a performance report from a video URL

        Args:
            video_url (str): URL of the video to analyze
            model (str): Gemini model to use
            prompt_type (str): Type of prompt to use ('simple' or 'detailed')
            save_to_file (bool): Whether to save the report to a markdown file
            filename (str, optional): Custom filename for the report

        Returns:
            str: Generated report in markdown format
        """
        system_instruction = self.prompt_manager.get_prompt(prompt_type)
        prompt_config = self.prompt_manager.get_prompt_config(prompt_type)

        with self.console.status("[bold green]Generating report...") as status:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=types.Content(
                        parts=[
                            types.Part(file_data=types.FileData(file_uri=video_url)),
                            types.Part(text="Please generate report from this video"),
                        ]
                    ),
                    config=types.GenerateContentConfig(
                        temperature=prompt_config.get("temperature", 0.2),
                        top_p=prompt_config.get("top_p", 0.95),
                        system_instruction=system_instruction,
                    ),
                )

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

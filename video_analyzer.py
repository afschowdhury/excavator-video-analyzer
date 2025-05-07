import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from IPython.display import Markdown, display

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

    def generate_report(
        self,
        video_url,
        model="gemini-2.5-flash-preview-04-17",
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

        response = self.client.models.generate_content(
            model=model,
            contents=types.Content(
                parts=[
                    types.Part(file_data=types.FileData(file_uri=video_url)),
                    types.Part(text="Please generate report from this video"),
                ]
            ),
            config=types.GenerateContentConfig(
                temperature=0.2,
                top_p=0.95,
                system_instruction=system_instruction,
            ),
        )

        report_text = response.text

        if save_to_file:
            self.report_saver.save_report(report_text, filename)

        return report_text

    def display_report(self, report_text):
        """
        Display the report text as formatted markdown

        Args:
            report_text (str): The report text to display
        """
        display(Markdown(report_text))

    def list_available_prompts(self):
        """
        List all available prompt types and their descriptions

        Returns:
            Dict[str, str]: Dictionary of prompt types and their descriptions
        """
        return self.prompt_manager.list_prompts()


def main():
    # Example usage
    analyzer = VideoAnalyzer()
    video_url = "https://youtu.be/QdWnkH3TGDU"  # Example video URL

    # List available prompts
    print("Available prompts:")
    for prompt_type, description in analyzer.list_available_prompts().items():
        print(f"- {prompt_type}: {description}")

    # Generate report using simple prompt and save to file
    report = analyzer.generate_report(
        video_url, prompt_type="simple", save_to_file=True
    )
    analyzer.display_report(report)

    # Generate report using detailed prompt with custom filename
    improved_report = analyzer.generate_report(
        video_url,
        prompt_type="detailed",
        save_to_file=True,
        filename="detailed_analysis",
    )
    analyzer.display_report(improved_report)


if __name__ == "__main__":
    main()

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from rich.console import Console
from rich.markdown import Markdown

from agents.orchestrator_agent import OrchestratorAgent
from config.adk_config import ADKConfig
from cycle_time_report import CycleTimeReport
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

    def analyze_with_agents(
        self,
        video_url: str,
        include_cycle_times: bool = True,
        include_technique_analysis: bool = True,
        save_to_file: bool = True,
        filename: str = None,
        config: ADKConfig = None
    ):
        """
        Analyze video using multi-agent ADK system

        Args:
            video_url (str): URL of the video to analyze
            include_cycle_times (bool): Whether to detect cycle times
            include_technique_analysis (bool): Whether to evaluate technique
            save_to_file (bool): Whether to save the report
            filename (str, optional): Custom filename for the report
            config (ADKConfig, optional): Custom ADK configuration

        Returns:
            str: Generated comprehensive report
        """
        with self.console.status("[bold green]Initializing multi-agent analysis...") as status:
            try:
                # Initialize configuration
                if config is None:
                    config = ADKConfig()

                # Initialize orchestrator with agents
                orchestrator = OrchestratorAgent(
                    api_key=self.api_key,
                    model=config.default_model
                )

                # Run orchestrated analysis
                status.update("[bold green]Running multi-agent analysis...")
                results = orchestrator.process(
                    video_url=video_url,
                    include_cycle_times=include_cycle_times,
                    include_technique_analysis=include_technique_analysis
                )

                # Generate formatted report
                status.update("[bold green]Generating comprehensive report...")
                report_text = orchestrator.get_formatted_report()

                # Optionally generate detailed cycle time report
                if include_cycle_times and results.get('cycles'):
                    status.update("[bold green]Generating cycle time analysis...")
                    cycle_reporter = CycleTimeReport()
                    
                    cycles_data = results['cycles']
                    if 'cycles' in cycles_data and 'summary' in cycles_data:
                        cycle_report = cycle_reporter.generate_markdown_report(
                            cycles=cycles_data['cycles'],
                            summary=cycles_data.get('summary', {}),
                            metadata={'video_url': video_url}
                        )
                        
                        # Append cycle report to main report
                        report_text += "\n\n---\n\n" + cycle_report

                # Save report if requested
                if save_to_file:
                    if filename:
                        self.report_saver.save_report(report_text, filename)
                    else:
                        # Generate filename with timestamp
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        self.report_saver.save_report(
                            report_text,
                            f"adk_analysis_{timestamp}"
                        )

                return report_text

            except Exception as e:
                self.console.print(f"[bold red]Error in multi-agent analysis: {e}")
                return None


def main():
    """Main entry point for the video analyzer"""
    try:
        analyzer = VideoAnalyzer()
        video_url = "https://youtu.be/QdWnkH3TGDU"

        console = Console()
        console.print("\n[bold cyan]═══════════════════════════════════════════════════════")
        console.print("[bold cyan]  Excavator Video Analyzer with ADK Multi-Agent System")
        console.print("[bold cyan]═══════════════════════════════════════════════════════\n")

        # Option 1: Traditional single-model approach
        console.print("[bold yellow]Option 1: Traditional Analysis (Simple)")
        report = analyzer.generate_report(
            video_url, prompt_type="simple", save_to_file=True
        )
        analyzer.display_report(report)

        console.print("\n[bold yellow]Option 2: Traditional Analysis (Detailed)")
        improved_report = analyzer.generate_report(
            video_url,
            prompt_type="detailed",
            save_to_file=True,
            filename="detailed_analysis",
        )
        analyzer.display_report(improved_report)

        # Option 2: NEW Multi-agent ADK approach with cycle time analysis
        console.print("\n[bold green]═══════════════════════════════════════════════════════")
        console.print("[bold green]  Option 3: Multi-Agent ADK Analysis (RECOMMENDED)")
        console.print("[bold green]═══════════════════════════════════════════════════════\n")
        
        adk_report = analyzer.analyze_with_agents(
            video_url=video_url,
            include_cycle_times=True,
            include_technique_analysis=True,
            save_to_file=True,
            filename="adk_multi_agent_analysis"
        )
        
        if adk_report:
            analyzer.display_report(adk_report)
        
        console.print("\n[bold green]✓ All analyses complete!")
        console.print("[bold cyan]Check the 'reports/' directory for saved reports.\n")

    except Exception as e:
        console = Console()
        console.print(f"[bold red]An error occurred: {e}")


if __name__ == "__main__":
    main()

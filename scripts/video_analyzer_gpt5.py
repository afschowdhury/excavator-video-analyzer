"""GPT-5 based video analyzer using multi-agent architecture"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from agents.core.orchestrator import AgentOrchestrator
from .report_saver import ReportSaver


class VideoAnalyzerGPT5:
    """
    Video analyzer using GPT-5 multi-agent system for frame-by-frame analysis
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        reports_dir: str = "reports",
        fps: int = 3,
        model: str = "gpt-4o",
        max_frames: Optional[int] = None,
    ):
        """
        Initialize the GPT-5 Video Analyzer

        Args:
            api_key: OpenAI API key. If not provided, will try to load from .env
            reports_dir: Directory to save generated reports
            fps: Frame extraction rate (frames per second)
            model: GPT-5 model to use (gpt-4o, gpt-4o-mini, etc.)
            max_frames: Maximum number of frames to analyze (None for no limit)
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Please provide it or set OPENAI_API_KEY in .env file"
            )

        # Validate model
        valid_models = ["gpt-4o", "gpt-4o-mini", "gpt-5", "gpt-5-mini", "gpt-5-nano"]
        if model not in valid_models:
            raise ValueError(
                f"Invalid model '{model}'. Valid models: {', '.join(valid_models)}"
            )

        self.model = model
        self.fps = fps
        self.max_frames = max_frames
        self.report_saver = ReportSaver(reports_dir)
        self.console = Console()

        # Initialize orchestrator with configuration
        config = {
            "frame_extractor": {"fps": fps, "max_frames": max_frames},
            "frame_classifier": {"model": model, "temperature": 0.2},
            "report_generator": {"model": model, "temperature": 0.3},
        }

        self.orchestrator = AgentOrchestrator(config)

    def generate_report(
        self,
        video_path: str,
        fps: Optional[int] = None,
        max_frames: Optional[int] = None,
        save_to_file: bool = True,
        filename: Optional[str] = None,
    ) -> str:
        """
        Generate a performance report from a video file

        Args:
            video_path: Path to local video file
            fps: Frame extraction rate (overrides default)
            max_frames: Maximum frames to analyze (overrides default)
            save_to_file: Whether to save the report to a markdown file
            filename: Custom filename for the report

        Returns:
            Generated report in markdown format
        """
        # Validate video path
        video_file = Path(video_path)
        if not video_file.exists():
            self.console.print(f"[bold red]Error: Video file not found: {video_path}")
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Set FPS if provided
        if fps is not None:
            self.orchestrator.set_fps(fps)
        else:
            self.orchestrator.set_fps(self.fps)

        # Set max_frames if provided
        if max_frames is not None:
            self.orchestrator.set_max_frames(max_frames)
        elif self.max_frames is not None:
            self.orchestrator.set_max_frames(self.max_frames)

        try:
            # Run the multi-agent pipeline
            result = self.orchestrator.run_pipeline(str(video_file))

            report_text = result["report"]

            # Save report if requested
            if save_to_file:
                saved_path = self.report_saver.save_report(report_text, filename)
                self.console.print(
                    f"[green]Report saved to: {saved_path}[/green]"
                )

            return report_text

        except Exception as e:
            self.console.print(f"[bold red]Error generating report: {e}")
            raise

    def analyze_video(
        self, video_path: str, fps: Optional[int] = None, max_frames: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze video and return detailed results including intermediate data

        Args:
            video_path: Path to local video file
            fps: Frame extraction rate (overrides default)
            max_frames: Maximum frames to analyze (overrides default)

        Returns:
            Dictionary with report, cycles, events, and metadata
        """
        # Set FPS if provided
        if fps is not None:
            self.orchestrator.set_fps(fps)

        # Set max_frames if provided
        if max_frames is not None:
            self.orchestrator.set_max_frames(max_frames)

        video_file = Path(video_path)
        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        result = self.orchestrator.run_pipeline(str(video_file))
        return result

    def display_report(self, report_text: str):
        """
        Display the report text as formatted markdown

        Args:
            report_text: The report text to display
        """
        if report_text:
            self.console.print(Markdown(report_text))
        else:
            self.console.print("[bold red]No report to display")

    def get_pipeline_data(self) -> Dict[str, Any]:
        """
        Get intermediate pipeline data (frames, classifications, events, etc.)

        Returns:
            Dictionary with all pipeline stage outputs
        """
        return self.orchestrator.get_pipeline_data()

    def set_fps(self, fps: int):
        """
        Set the frame extraction rate

        Args:
            fps: Frames per second to extract
        """
        if fps < 1 or fps > 30:
            raise ValueError("FPS must be between 1 and 30")

        self.fps = fps
        self.orchestrator.set_fps(fps)
        self.console.print(f"[blue]Frame rate set to {fps} FPS[/blue]")

    def set_max_frames(self, max_frames: Optional[int]):
        """
        Set the maximum number of frames to analyze

        Args:
            max_frames: Maximum frames to extract (None for no limit)
        """
        if max_frames is not None and max_frames < 1:
            raise ValueError("max_frames must be at least 1")

        self.max_frames = max_frames
        self.orchestrator.set_max_frames(max_frames)
        if max_frames:
            self.console.print(f"[blue]Max frames set to {max_frames}[/blue]")
        else:
            self.console.print(f"[blue]Max frames limit removed[/blue]")

    def reset(self):
        """Reset the analyzer for a new video"""
        self.orchestrator.reset()


def main():
    """Main entry point for testing the GPT-5 video analyzer"""
    try:
        # Initialize analyzer
        analyzer = VideoAnalyzerGPT5(fps=3, model="gpt-4o")

        # Path to local video
        video_path = "videos/B2.mp4"

        # Generate report
        console = Console()
        console.print("[bold cyan]Starting GPT-5 Video Analysis...[/bold cyan]\n")

        report = analyzer.generate_report(
            video_path, fps=3, save_to_file=True, filename="gpt5_analysis"
        )

        # Display report
        analyzer.display_report(report)

        # Show pipeline statistics
        pipeline_data = analyzer.get_pipeline_data()
        console.print(f"\n[bold]Pipeline Statistics:[/bold]")
        console.print(f"  • Frames extracted: {len(pipeline_data.get('frames', []))}")
        console.print(f"  • Events detected: {len(pipeline_data.get('events', []))}")
        console.print(f"  • Cycles found: {len(pipeline_data.get('cycles', []))}")

    except Exception as e:
        console = Console()
        console.print(f"[bold red]An error occurred: {e}")


if __name__ == "__main__":
    main()


"""Orchestrator for coordinating all agents in the pipeline"""

from typing import Any, Dict, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from .frame_extractor import FrameExtractorAgent
from .frame_classifier import FrameClassifierAgent
from .action_detector import ActionDetectorAgent
from .cycle_assembler import CycleAssemblerAgent
from .report_generator import ReportGeneratorAgent


class AgentOrchestrator:
    """Orchestrates the multi-agent pipeline for video analysis"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the orchestrator with all agents

        Args:
            config: Configuration dictionary for agents
        """
        self.config = config or {}
        self.console = Console()

        # Initialize agents
        self.frame_extractor = FrameExtractorAgent(
            config=self.config.get("frame_extractor", {})
        )
        self.frame_classifier = FrameClassifierAgent(
            config=self.config.get("frame_classifier", {})
        )
        self.action_detector = ActionDetectorAgent(
            config=self.config.get("action_detector", {})
        )
        self.cycle_assembler = CycleAssemblerAgent(
            config=self.config.get("cycle_assembler", {})
        )
        self.report_generator = ReportGeneratorAgent(
            config=self.config.get("report_generator", {})
        )

        self.pipeline_data = {}

    def run_pipeline(
        self, video_path: str, progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Run the complete analysis pipeline

        Args:
            video_path: Path to video file
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary containing report and metadata
        """
        self.console.print(
            "\n[bold cyan]═══ GPT-5 Multi-Agent Video Analysis Pipeline ═══[/bold cyan]\n"
        )

        try:
            # Stage 1: Extract Frames
            if progress_callback:
                progress_callback("Extracting frames from video...", 0)
            self.console.print("\n[bold cyan]━━━ Stage 1/5: Frame Extraction ━━━[/bold cyan]")
            frames = self.frame_extractor.process(video_path)
            self.pipeline_data["frames"] = frames
            self.console.print(f"[green]✓[/green] Extracted {len(frames)} frames\n")

            # Stage 2: Classify Frames
            if progress_callback:
                progress_callback("Classifying frames with GPT-5...", 20)
            self.console.print(f"[bold cyan]━━━ Stage 2/5: Frame Classification ━━━[/bold cyan]")
            classified_frames = self.frame_classifier.process(frames)
            self.pipeline_data["classified_frames"] = classified_frames
            self.console.print(f"[green]✓[/green] Classified {len(classified_frames)} frames\n")

            # Stage 3: Detect Actions
            if progress_callback:
                progress_callback("Detecting actions and transitions...", 60)
            self.console.print(f"[bold cyan]━━━ Stage 3/5: Action Detection ━━━[/bold cyan]")
            events = self.action_detector.process(classified_frames)
            self.pipeline_data["events"] = events
            self.console.print(f"[green]✓[/green] Detected {len(events)} events\n")

            # Stage 4: Assemble Cycles
            if progress_callback:
                progress_callback("Assembling excavation cycles...", 80)
            self.console.print(f"[bold cyan]━━━ Stage 4/5: Cycle Assembly ━━━[/bold cyan]")
            cycles = self.cycle_assembler.process(events)
            self.pipeline_data["cycles"] = cycles
            self.console.print(f"[green]✓[/green] Assembled {len(cycles)} cycles\n")

            # Stage 5: Generate Report
            if progress_callback:
                progress_callback("Generating final report...", 90)
            self.console.print(f"[bold cyan]━━━ Stage 5/5: Report Generation ━━━[/bold cyan]")

            # Build context for report generation
            context = {
                "video_duration": self.frame_extractor.get_state("video_duration"),
                "total_frames": self.frame_extractor.get_state("total_frames"),
                "fps": self.frame_extractor.fps,
                "total_events": self.action_detector.get_state("total_events"),
                "total_cycles": self.cycle_assembler.get_state("total_cycles"),
            }

            report = self.report_generator.process(cycles, context)
            self.pipeline_data["report"] = report

            if progress_callback:
                progress_callback("Analysis complete!", 100)

            self.console.print(
                f"\n[bold green]✓ Analysis complete![/bold green] Found {len(cycles)} cycles.\n"
            )

            return {
                "report": report,
                "cycles": cycles,
                "events": events,
                "frames_analyzed": len(frames),
                "metadata": context,
            }

        except Exception as e:
            error_msg = f"Pipeline failed: {str(e)}"
            self.console.print(f"[bold red]✗ {error_msg}[/bold red]")
            if progress_callback:
                progress_callback(error_msg, -1)
            raise

    def set_fps(self, fps: int):
        """
        Set frame extraction rate

        Args:
            fps: Frames per second
        """
        self.frame_extractor.set_fps(fps)

    def set_max_frames(self, max_frames: Optional[int]):
        """
        Set maximum number of frames to extract

        Args:
            max_frames: Maximum frames to extract (None for no limit)
        """
        self.frame_extractor.set_max_frames(max_frames)

    def get_pipeline_data(self) -> Dict[str, Any]:
        """
        Get all intermediate pipeline data

        Returns:
            Dictionary with all pipeline stage outputs
        """
        return self.pipeline_data

    def reset(self):
        """Reset all agents and pipeline data"""
        self.frame_classifier.reset_context()
        self.pipeline_data = {}
        self.console.print("[yellow]Pipeline reset[/yellow]")


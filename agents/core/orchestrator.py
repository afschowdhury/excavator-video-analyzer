"""Orchestrator for coordinating all agents in the pipeline"""

from typing import Any, Dict, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from ..core.frame_extractor import FrameExtractorAgent
# from ..gpt.frame_classifier import FrameClassifierAgent
from ..gemini.behavior_analysis_agent import BehaviorAnalysisAgent
from ..core.action_detector import ActionDetectorAgent
from ..core.cycle_assembler import CycleAssemblerAgent
# from ..gpt.report_generator import ReportGeneratorAgent
from ..core.simulation_report_agent import SimulationReportAgent


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
        # self.frame_classifier = FrameClassifierAgent(
        #     config=self.config.get("frame_classifier", {})
        # )
        self.behavior_analyzer = BehaviorAnalysisAgent(
            config=self.config.get("behavior_analysis", {})
        )
        self.action_detector = ActionDetectorAgent(
            config=self.config.get("action_detector", {})
        )
        self.cycle_assembler = CycleAssemblerAgent(
            config=self.config.get("cycle_assembler", {})
        )
        # self.report_generator = ReportGeneratorAgent(
        #     config=self.config.get("report_generator", {})
        # )
        self.simulation_report_agent = SimulationReportAgent(
            config=self.config.get("simulation_report", {})
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
            "\n[bold cyan]═══ Multi-Agent Video Analysis Pipeline ═══[/bold cyan]\n"
        )

        try:
            # Stage 1: Extract Frames
            if progress_callback:
                progress_callback("Extracting frames from video...", 0)
            self.console.print("\n[bold cyan]━━━ Stage 1/6: Frame Extraction ━━━[/bold cyan]")
            frames = self.frame_extractor.process(video_path)
            self.pipeline_data["frames"] = frames
            self.console.print(f"[green]✓[/green] Extracted {len(frames)} frames\n")

            # Stage 2: Classify Frames (DISABLED - GPT Removed)
            # if progress_callback:
            #     progress_callback("Classifying frames...", 15)
            # self.console.print(f"[bold cyan]━━━ Stage 2/6: Frame Classification (SKIPPED) ━━━[/bold cyan]")
            # classified_frames = self.frame_classifier.process(frames)
            # self.pipeline_data["classified_frames"] = classified_frames
            # self.console.print(f"[green]✓[/green] Classified {len(classified_frames)} frames\n")
            
            # Placeholder for classified frames to prevent crashes in dependent agents if called
            classified_frames = [] 

            # Stage 3: Behavior Analysis
            if progress_callback:
                progress_callback("Analyzing operator behavior...", 30)
            self.console.print(f"[bold cyan]━━━ Stage 3/6: Behavior Analysis ━━━[/bold cyan]")
            behavior_analysis = self.behavior_analyzer.process(frames)
            self.pipeline_data["behavior_analysis"] = behavior_analysis
            behavior_events = behavior_analysis.get("behavior_events", [])
            self.console.print(f"[green]✓[/green] Analyzed behavior: {len(behavior_events)} events detected\n")

            # Stage 4: Detect Actions
            # if progress_callback:
            #     progress_callback("Detecting actions and transitions...", 50)
            # self.console.print(f"[bold cyan]━━━ Stage 4/6: Action Detection (SKIPPED) ━━━[/bold cyan]")
            # events = self.action_detector.process(classified_frames)
            # self.pipeline_data["events"] = events
            # self.console.print(f"[green]✓[/green] Detected {len(events)} events\n")
            events = []

            # Stage 5: Assemble Cycles
            # if progress_callback:
            #     progress_callback("Assembling excavation cycles...", 70)
            # self.console.print(f"[bold cyan]━━━ Stage 5/6: Cycle Assembly (SKIPPED) ━━━[/bold cyan]")
            # cycles = self.cycle_assembler.process(events)
            # self.pipeline_data["cycles"] = cycles
            # self.console.print(f"[green]✓[/green] Assembled {len(cycles)} cycles\n")
            cycles = []

            # Stage 5.5: Extract Simulation Report Metrics
            if progress_callback:
                progress_callback("Extracting simulation metrics...", 80)
            self.console.print(f"[bold cyan]━━━ Extracting Simulation Metrics ━━━[/bold cyan]")
            simulation_metrics = self.simulation_report_agent.process(video_path)
            self.pipeline_data["simulation_metrics"] = simulation_metrics
            if simulation_metrics.get('found'):
                self.console.print(f"[green]✓[/green] Extracted simulation metrics for ID: {simulation_metrics.get('video_id')}\n")
            else:
                self.console.print(f"[yellow]⚠[/yellow] No simulation report found for this video\n")

            # Stage 6: Generate Report (DISABLED - GPT Removed)
            # if progress_callback:
            #     progress_callback("Generating final report...", 85)
            # self.console.print(f"[bold cyan]━━━ Stage 6/6: Report Generation (SKIPPED) ━━━[/bold cyan]")

            # Build context for report generation
            context = {
                "video_duration": self.frame_extractor.get_state("video_duration"),
                "total_frames": self.frame_extractor.get_state("total_frames"),
                "fps": self.frame_extractor.fps,
                "total_events": self.action_detector.get_state("total_events"),
                "total_cycles": self.cycle_assembler.get_state("total_cycles"),
                "behavior_analysis": behavior_analysis,
                "simulation_metrics": simulation_metrics,
            }

            # report = self.report_generator.process(cycles, context)
            report = "Report generation disabled (GPT agents removed)."
            self.pipeline_data["report"] = report

            if progress_callback:
                progress_callback("Analysis complete!", 100)

            self.console.print(
                f"\n[bold green]✓ Analysis complete![/bold green] (Partial execution due to removed agents)\n"
            )

            return {
                "report": report,
                "cycles": cycles,
                "events": events,
                "behavior_analysis": behavior_analysis,
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
        # self.frame_classifier.reset_context()
        self.pipeline_data = {}
        self.console.print("[yellow]Pipeline reset[/yellow]")

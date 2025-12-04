"""Report orchestrator for coordinating all report generation agents"""

from typing import Any, Dict, Optional

from rich.console import Console

from ..core.cycle_metrics_agent import CycleMetricsAgent
from ..gemini.chart_analysis_agent import ChartAnalysisAgent
from ..gemini.html_assembler_agent import HTMLAssemblerAgent
from ..gemini.insights_generator_agent import InsightsGeneratorAgent
from ..gemini.joystick_analytics_agent import JoystickAnalyticsAgent
from ..gemini.performance_score_agent import PerformanceScoreAgent


class ReportOrchestrator:
    """Orchestrates the multi-agent pipeline for HTML report generation"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the orchestrator with all report agents

        Args:
            config: Configuration dictionary for agents
        """
        self.config = config or {}
        self.console = Console()

        # Initialize agents
        self.cycle_metrics_agent = CycleMetricsAgent(
            config=self.config.get("cycle_metrics", {})
        )
        self.joystick_analytics_agent = JoystickAnalyticsAgent(
            config=self.config.get("joystick_analytics", {})
        )
        self.chart_analysis_agent = ChartAnalysisAgent(
            config=self.config.get("chart_analysis", {})
        )
        self.performance_score_agent = PerformanceScoreAgent(
            config=self.config.get("performance_score", {})
        )
        self.insights_generator_agent = InsightsGeneratorAgent(
            config=self.config.get("insights_generator", {})
        )
        self.html_assembler_agent = HTMLAssemblerAgent(
            config=self.config.get("html_assembler", {})
        )

        self.pipeline_data = {}

    def run_pipeline(
        self,
        cycle_data: list,
        joystick_data_path: str,
        operator_info: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        Run the complete report generation pipeline

        Args:
            cycle_data: List of cycle dictionaries from video analysis
            joystick_data_path: Path to joystick data directory or stats.json
            operator_info: Dictionary containing operator metadata
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary containing HTML report and metadata
        """
        self.console.print(
            "\n[bold cyan]═══ HTML Report Generation Pipeline ═══[/bold cyan]\n"
        )

        try:
            # Stage 1: Calculate Cycle Metrics
            if progress_callback:
                progress_callback("Calculating cycle metrics...", 0)
            self.console.print("\n[bold cyan]━━━ Stage 1/5: Cycle Metrics Calculation ━━━[/bold cyan]")
            cycle_metrics = self.cycle_metrics_agent.process(cycle_data)
            self.pipeline_data["cycle_metrics"] = cycle_metrics
            self.console.print(
                f"[green]✓[/green] Metrics calculated for {cycle_metrics.get('total_cycles', 0)} cycles\n"
            )

            # Stage 2: Process Joystick Analytics
            if progress_callback:
                progress_callback("Processing joystick analytics...", 15)
            self.console.print(f"[bold cyan]━━━ Stage 2/6: Joystick Analytics ━━━[/bold cyan]")
            joystick_analytics = self.joystick_analytics_agent.process(joystick_data_path)
            self.pipeline_data["joystick_analytics"] = joystick_analytics
            self.console.print(f"[green]✓[/green] Analytics processed\n")

            # Stage 3: Analyze Charts Visually
            if progress_callback:
                progress_callback("Analyzing charts with vision AI...", 30)
            self.console.print(f"[bold cyan]━━━ Stage 3/6: Visual Chart Analysis ━━━[/bold cyan]")
            chart_analysis = self.chart_analysis_agent.process(joystick_data_path)
            self.pipeline_data["chart_analysis"] = chart_analysis
            self.console.print(f"[green]✓[/green] Chart analysis completed\n")

            # Stage 4: Generate Performance Scores
            if progress_callback:
                progress_callback("Generating performance scores...", 45)
            self.console.print(f"[bold cyan]━━━ Stage 4/6: Performance Scoring ━━━[/bold cyan]")
            performance_input = {
                "cycle_metrics": cycle_metrics,
                "joystick_analytics": joystick_analytics,
            }
            performance_scores = self.performance_score_agent.process(performance_input)
            self.pipeline_data["performance_scores"] = performance_scores
            self.console.print(f"[green]✓[/green] Performance scores calculated\n")

            # Stage 5: Generate AI Insights
            if progress_callback:
                progress_callback("Generating AI insights...", 60)
            self.console.print(f"[bold cyan]━━━ Stage 5/6: AI Insights Generation ━━━[/bold cyan]")
            insights_input = {
                "cycle_metrics": cycle_metrics,
                "joystick_analytics": joystick_analytics,
                "performance_scores": performance_scores,
            }
            insights = self.insights_generator_agent.process(insights_input)
            self.pipeline_data["insights"] = insights
            self.console.print(f"[green]✓[/green] AI insights generated\n")

            # Stage 6: Assemble HTML Report
            if progress_callback:
                progress_callback("Assembling HTML report...", 80)
            self.console.print(f"[bold cyan]━━━ Stage 6/6: HTML Report Assembly ━━━[/bold cyan]")
            assembly_input = {
                "cycle_metrics": cycle_metrics,
                "joystick_analytics": joystick_analytics,
                "chart_analysis": chart_analysis,
                "performance_scores": performance_scores,
                "insights": insights,
            }
            html_report = self.html_assembler_agent.process(
                assembly_input, context=operator_info
            )
            self.pipeline_data["html_report"] = html_report

            if progress_callback:
                progress_callback("Report generation complete!", 100)

            self.console.print(
                f"\n[bold green]✓ Report generation complete![/bold green]\n"
            )

            return {
                "html_report": html_report,
                "cycle_metrics": cycle_metrics,
                "joystick_analytics": joystick_analytics,
                "chart_analysis": chart_analysis,
                "performance_scores": performance_scores,
                "insights": insights,
                "metadata": {
                    "total_cycles": cycle_metrics.get("total_cycles", 0),
                    "average_cycle_time": cycle_metrics.get("average_cycle_time", 0),
                    "productivity_score": performance_scores.get("productivity_score", 0),
                    "control_skill_score": performance_scores.get("control_skill_score", 0),
                    "safety_score": performance_scores.get("safety_score", 0),
                    "proficiency_level": insights.get("proficiency_level", "Unknown"),
                },
            }

        except Exception as e:
            error_msg = f"Pipeline failed: {str(e)}"
            self.console.print(f"[bold red]✗ {error_msg}[/bold red]")
            if progress_callback:
                progress_callback(error_msg, -1)
            raise

    def get_pipeline_data(self) -> Dict[str, Any]:
        """
        Get all intermediate pipeline data

        Returns:
            Dictionary with all pipeline stage outputs
        """
        return self.pipeline_data

    def reset(self):
        """Reset all agents and pipeline data"""
        self.pipeline_data = {}
        self.console.print("[yellow]Pipeline reset[/yellow]")


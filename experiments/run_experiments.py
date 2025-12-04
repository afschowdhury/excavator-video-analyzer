"""
Experiment runner for testing GPT-5 video analysis with different FPS settings

This script runs the video analyzer with different frame rates and compares:
- Cycle detection accuracy
- Processing time
- Estimated API costs
- Cycle count consistency
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.video_analyzer_gpt5 import VideoAnalyzerGPT5
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn


class ExperimentRunner:
    """Runner for video analysis experiments with different configurations"""

    def __init__(self, video_path: str, output_dir: str = "experiments/results"):
        """
        Initialize experiment runner

        Args:
            video_path: Path to video file
            output_dir: Directory to save experiment results
        """
        self.video_path = video_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.console = Console()
        self.results = []

    def run_experiment(
        self, fps: int, model: str = "gpt-4o", run_number: int = 1
    ) -> Dict[str, Any]:
        """
        Run a single experiment with given configuration

        Args:
            fps: Frame rate to use
            model: GPT model to use
            run_number: Run number for this configuration

        Returns:
            Dictionary with experiment results
        """
        self.console.print(
            f"\n[bold cyan]{'═' * 60}[/bold cyan]"
        )
        self.console.print(
            f"[bold]Experiment Run #{run_number}: {fps} FPS with {model}[/bold]"
        )
        self.console.print(f"[bold cyan]{'═' * 60}[/bold cyan]\n")

        # Initialize analyzer
        analyzer = VideoAnalyzerGPT5(fps=fps, model=model)

        # Record start time
        start_time = time.time()

        try:
            # Run analysis
            result = analyzer.analyze_video(self.video_path, fps=fps)

            # Record end time
            end_time = time.time()
            processing_time = end_time - start_time

            # Extract results
            cycles = result.get("cycles", [])
            events = result.get("events", [])
            frames_analyzed = result.get("frames_analyzed", 0)
            metadata = result.get("metadata", {})

            # Calculate statistics
            cycle_count = len(cycles)
            complete_cycles = sum(1 for c in cycles if c.get("is_complete", False))
            avg_cycle_time = (
                sum(c["duration"] for c in cycles) / cycle_count if cycle_count > 0 else 0
            )

            # Estimate costs (approximate)
            # GPT-4o vision: ~$0.01 per image (rough estimate)
            estimated_cost = frames_analyzed * 0.01

            experiment_result = {
                "run_number": run_number,
                "timestamp": datetime.now().isoformat(),
                "configuration": {
                    "fps": fps,
                    "model": model,
                    "video_path": str(self.video_path),
                },
                "performance": {
                    "processing_time_seconds": round(processing_time, 2),
                    "frames_analyzed": frames_analyzed,
                    "events_detected": len(events),
                    "estimated_cost_usd": round(estimated_cost, 2),
                },
                "results": {
                    "total_cycles": cycle_count,
                    "complete_cycles": complete_cycles,
                    "incomplete_cycles": cycle_count - complete_cycles,
                    "average_cycle_time": round(avg_cycle_time, 2),
                    "video_duration": metadata.get("video_duration", 0),
                },
                "cycles": [
                    {
                        "cycle_number": c["cycle_number"],
                        "start_time": c["start_time_str"],
                        "end_time": c["end_time_str"],
                        "duration": c["duration"],
                        "is_complete": c["is_complete"],
                    }
                    for c in cycles
                ],
            }

            # Display results
            self._display_experiment_results(experiment_result)

            return experiment_result

        except Exception as e:
            self.console.print(f"[bold red]Experiment failed: {e}[/bold red]")
            return {
                "run_number": run_number,
                "timestamp": datetime.now().isoformat(),
                "configuration": {"fps": fps, "model": model},
                "error": str(e),
            }

    def run_fps_comparison(
        self, fps_list: List[int], model: str = "gpt-4o"
    ) -> List[Dict[str, Any]]:
        """
        Run experiments comparing different FPS settings

        Args:
            fps_list: List of FPS values to test
            model: GPT model to use

        Returns:
            List of experiment results
        """
        self.console.print(
            "\n[bold green]🚀 Starting FPS Comparison Experiments[/bold green]\n"
        )
        self.console.print(f"Testing FPS values: {fps_list}")
        self.console.print(f"Model: {model}")
        self.console.print(f"Video: {self.video_path}\n")

        results = []

        for i, fps in enumerate(fps_list, 1):
            result = self.run_experiment(fps, model, run_number=i)
            results.append(result)
            self.results.append(result)

            # Small delay between experiments
            if i < len(fps_list):
                self.console.print("\n[yellow]Waiting 5 seconds before next experiment...[/yellow]")
                time.sleep(5)

        # Display comparison table
        self._display_comparison_table(results)

        # Save results
        self._save_results(results)

        return results

    def _display_experiment_results(self, result: Dict[str, Any]):
        """Display results for a single experiment"""
        if "error" in result:
            return

        perf = result["performance"]
        res = result["results"]

        self.console.print("\n[bold]Results:[/bold]")
        self.console.print(f"  • Processing time: {perf['processing_time_seconds']}s")
        self.console.print(f"  • Frames analyzed: {perf['frames_analyzed']}")
        self.console.print(f"  • Events detected: {perf['events_detected']}")
        self.console.print(f"  • Estimated cost: ${perf['estimated_cost_usd']}")
        self.console.print(f"\n[bold]Cycle Detection:[/bold]")
        self.console.print(f"  • Total cycles: {res['total_cycles']}")
        self.console.print(f"  • Complete cycles: {res['complete_cycles']}")
        self.console.print(f"  • Average cycle time: {res['average_cycle_time']}s")

    def _display_comparison_table(self, results: List[Dict[str, Any]]):
        """Display comparison table for all experiments"""
        self.console.print("\n[bold green]═" * 70 + "[/bold green]")
        self.console.print("[bold green]EXPERIMENT COMPARISON SUMMARY[/bold green]")
        self.console.print("[bold green]═" * 70 + "[/bold green]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("FPS", style="cyan", justify="center")
        table.add_column("Time (s)", justify="right")
        table.add_column("Frames", justify="right")
        table.add_column("Cycles", justify="center")
        table.add_column("Complete", justify="center")
        table.add_column("Avg Duration", justify="right")
        table.add_column("Cost ($)", justify="right")

        for result in results:
            if "error" in result:
                fps = result["configuration"]["fps"]
                table.add_row(str(fps), "ERROR", "-", "-", "-", "-", "-")
            else:
                fps = result["configuration"]["fps"]
                time_taken = result["performance"]["processing_time_seconds"]
                frames = result["performance"]["frames_analyzed"]
                cycles = result["results"]["total_cycles"]
                complete = result["results"]["complete_cycles"]
                avg_duration = result["results"]["average_cycle_time"]
                cost = result["performance"]["estimated_cost_usd"]

                table.add_row(
                    str(fps),
                    f"{time_taken}",
                    str(frames),
                    str(cycles),
                    str(complete),
                    f"{avg_duration}s",
                    f"{cost:.2f}",
                )

        self.console.print(table)

        # Display recommendations
        self._display_recommendations(results)

    def _display_recommendations(self, results: List[Dict[str, Any]]):
        """Display recommendations based on experiment results"""
        self.console.print("\n[bold yellow]💡 Recommendations:[/bold yellow]\n")

        # Filter out errors
        valid_results = [r for r in results if "error" not in r]

        if not valid_results:
            self.console.print("[red]No valid results to analyze[/red]")
            return

        # Find best options
        fastest = min(valid_results, key=lambda r: r["performance"]["processing_time_seconds"])
        cheapest = min(valid_results, key=lambda r: r["performance"]["estimated_cost_usd"])
        most_cycles = max(valid_results, key=lambda r: r["results"]["total_cycles"])

        self.console.print(f"  🏃 [bold]Fastest:[/bold] {fastest['configuration']['fps']} FPS ({fastest['performance']['processing_time_seconds']}s)")
        self.console.print(f"  💰 [bold]Cheapest:[/bold] {cheapest['configuration']['fps']} FPS (${cheapest['performance']['estimated_cost_usd']})")
        self.console.print(f"  🎯 [bold]Most cycles detected:[/bold] {most_cycles['configuration']['fps']} FPS ({most_cycles['results']['total_cycles']} cycles)")

        # Check consistency
        cycle_counts = [r["results"]["total_cycles"] for r in valid_results]
        if len(set(cycle_counts)) == 1:
            self.console.print(f"\n  ✅ [green]All FPS settings detected the same number of cycles ({cycle_counts[0]})[/green]")
        else:
            self.console.print(f"\n  ⚠️  [yellow]Different FPS settings detected different cycle counts: {cycle_counts}[/yellow]")
            self.console.print("      Higher FPS may be needed for accuracy.")

    def _save_results(self, results: List[Dict[str, Any]]):
        """Save experiment results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"experiment_results_{timestamp}.json"

        output = {
            "experiment_date": datetime.now().isoformat(),
            "video_path": str(self.video_path),
            "results": results,
        }

        with open(filename, "w") as f:
            json.dump(output, f, indent=2)

        self.console.print(f"\n[green]✓ Results saved to: {filename}[/green]")


def main():
    """Main entry point for experiment runner"""
    console = Console()

    # Configuration
    video_path = "videos/B2.mp4"
    fps_list = [1, 3, 5, 10]  # Test all FPS options
    model = "gpt-4o"

    # Check if video exists
    if not Path(video_path).exists():
        console.print(f"[bold red]Error: Video file not found: {video_path}[/bold red]")
        return

    console.print("[bold cyan]═" * 70 + "[/bold cyan]")
    console.print("[bold cyan]GPT-5 Video Analysis - FPS Comparison Experiments[/bold cyan]")
    console.print("[bold cyan]═" * 70 + "[/bold cyan]")

    # Create runner
    runner = ExperimentRunner(video_path)

    # Run experiments
    try:
        results = runner.run_fps_comparison(fps_list, model=model)

        console.print("\n[bold green]✓ All experiments completed![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Experiments interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Experiment runner failed: {e}[/bold red]")


if __name__ == "__main__":
    main()


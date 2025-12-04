"""
Test script to demonstrate video_analyzer.py -> cycle_time_analyzer.py workflow
"""

import os
import sys

# Add parent directory to path to import from scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.video_analyzer import VideoAnalyzer
from scripts.cycle_time_analyzer import CycleTimeAnalyzer
from rich.console import Console


def main():
    """Test the complete workflow: video analysis -> cycle parsing -> statistical analysis"""
    
    console = Console()
    
    console.print("[bold blue]===== Excavation Cycle Time Analysis Demo =====\n")
    
    # Step 1: Initialize analyzers
    console.print("[bold green]Step 1:[/] Initializing analyzers...")
    video_analyzer = VideoAnalyzer()
    cycle_analyzer = CycleTimeAnalyzer()
    
    # Step 2: Analyze video for cycle times
    console.print("\n[bold green]Step 2:[/] Analyzing video for excavation cycles...")
    video_url = "https://youtu.be/QdWnkH3TGDU"
    
    console.print(f"  Video URL: {video_url}")
    console.print("  Prompt: cycle_time_simple")
    
    # Generate cycle time report from video
    report = video_analyzer.generate_report(
        video_url,
        prompt_type="cycle_time_simple",
        save_to_file=False
    )
    
    if not report:
        console.print("[bold red]Failed to generate video analysis report")
        return
    
    console.print("\n[bold cyan]--- Video Analysis Report ---")
    video_analyzer.display_report(report)
    
    # Step 3: Parse cycle data from report
    console.print("\n[bold green]Step 3:[/] Parsing cycle data from report...")
    cycle_data = VideoAnalyzer.parse_cycle_data(report)
    
    if not cycle_data:
        console.print("[bold red]No cycle data found in report")
        return
    
    console.print(f"  Found {len(cycle_data)} cycles")
    
    # Step 4: Calculate statistics
    console.print("\n[bold green]Step 4:[/] Calculating cycle time statistics...")
    statistics = cycle_analyzer.calculate_statistics(cycle_data)
    
    console.print(f"  Total cycles: {statistics['total_cycles']}")
    console.print(f"  Average duration: {statistics['average_duration']:.2f}s")
    
    # Step 5: Generate statistical analysis report
    console.print("\n[bold green]Step 5:[/] Generating statistical analysis report...")
    analysis_report = cycle_analyzer.generate_analysis_report(statistics, use_ai=False)
    
    console.print("\n[bold cyan]--- Cycle Time Statistical Analysis ---")
    cycle_analyzer.display_report(analysis_report)
    
    console.print("\n[bold blue]===== Analysis Complete =====")


if __name__ == "__main__":
    main()


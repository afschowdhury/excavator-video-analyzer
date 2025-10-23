"""
Example usage of the Excavator Video Analyzer with ADK Multi-Agent System
"""

from video_analyzer import VideoAnalyzer
from config.adk_config import ADKConfig
from rich.console import Console


def example_multi_agent_analysis():
    """
    Example: Multi-agent analysis with cycle time detection
    This is the RECOMMENDED approach for comprehensive analysis
    """
    console = Console()
    console.print("\n[bold cyan]Example 1: Multi-Agent Analysis with Cycle Time Detection[/]\n")
    
    # Initialize analyzer
    analyzer = VideoAnalyzer()
    
    # Your video URL
    video_url = "https://youtu.be/QdWnkH3TGDU"
    
    # Run multi-agent analysis
    report = analyzer.analyze_with_agents(
        video_url=video_url,
        include_cycle_times=True,
        include_technique_analysis=True,
        save_to_file=True,
        filename="example_adk_analysis"
    )
    
    # Display the report
    if report:
        analyzer.display_report(report)
        console.print("\n[green]✓ Report generated successfully![/]")


def example_custom_config():
    """
    Example: Using custom ADK configuration
    """
    console = Console()
    console.print("\n[bold cyan]Example 2: Custom Configuration[/]\n")
    
    # Create custom configuration
    config = ADKConfig(
        default_model="gemini-2.0-flash-exp",
        timeout=900,  # 15 minutes
        parallel_execution=False
    )
    
    # Customize cycle detector settings
    config.cycle_detector.model.temperature = 0.05  # More deterministic
    config.cycle_detector.model.max_tokens = 10000  # Allow more output
    
    # Customize technique evaluator settings
    config.technique_evaluator.model.temperature = 0.25
    
    # Initialize analyzer
    analyzer = VideoAnalyzer()
    video_url = "https://youtu.be/QdWnkH3TGDU"
    
    # Run with custom config
    report = analyzer.analyze_with_agents(
        video_url=video_url,
        config=config,
        save_to_file=True,
        filename="example_custom_config"
    )
    
    if report:
        console.print("[green]✓ Custom configuration analysis complete![/]")


def example_individual_agents():
    """
    Example: Using individual agents separately
    """
    console = Console()
    console.print("\n[bold cyan]Example 3: Using Individual Agents[/]\n")
    
    from agents import CycleDetectorAgent, TechniqueEvaluatorAgent
    
    video_url = "https://youtu.be/QdWnkH3TGDU"
    
    # Use cycle detector only
    console.print("[yellow]Running cycle detector...[/]")
    cycle_agent = CycleDetectorAgent()
    cycle_results = cycle_agent.process(video_url)
    
    console.print(f"[green]✓ Detected {cycle_results['cycle_count']} cycles[/]")
    console.print(f"[green]✓ Average cycle time: {cycle_agent.get_average_cycle_time():.1f}s[/]")
    
    # Use technique evaluator only
    console.print("\n[yellow]Running technique evaluator...[/]")
    technique_agent = TechniqueEvaluatorAgent()
    technique_results = technique_agent.process(
        video_url,
        cycle_context={'cycle_count': cycle_results['cycle_count']}
    )
    
    overall_score = technique_results.get('overall_score', {})
    console.print(f"[green]✓ Overall score: {overall_score.get('score', 'N/A')}[/]")
    console.print(f"[green]✓ Performance grade: {overall_score.get('grade', 'N/A')}[/]")


def example_cycle_time_report():
    """
    Example: Generating detailed cycle time report
    """
    console = Console()
    console.print("\n[bold cyan]Example 4: Detailed Cycle Time Report[/]\n")
    
    from agents import CycleDetectorAgent
    from cycle_time_report import CycleTimeReport
    
    video_url = "https://youtu.be/QdWnkH3TGDU"
    
    # Detect cycles
    console.print("[yellow]Detecting cycles...[/]")
    cycle_agent = CycleDetectorAgent()
    results = cycle_agent.process(video_url)
    
    # Generate report
    console.print("[yellow]Generating cycle time report...[/]")
    reporter = CycleTimeReport()
    
    # Display as table
    reporter.display_table(results['cycles'])
    
    # Generate markdown report
    report = reporter.generate_markdown_report(
        cycles=results['cycles'],
        summary=results.get('summary', {}),
        metadata={'video_url': video_url}
    )
    
    # Save report
    reporter.save_report(report, filename="example_cycle_time_report")
    
    console.print("[green]✓ Cycle time report generated![/]")


def example_traditional_analysis():
    """
    Example: Traditional single-model analysis (for comparison)
    """
    console = Console()
    console.print("\n[bold cyan]Example 5: Traditional Analysis (Single Model)[/]\n")
    
    analyzer = VideoAnalyzer()
    video_url = "https://youtu.be/QdWnkH3TGDU"
    
    # Simple analysis
    console.print("[yellow]Running simple analysis...[/]")
    report = analyzer.generate_report(
        video_url=video_url,
        prompt_type="simple",
        save_to_file=True,
        filename="example_simple"
    )
    
    # Detailed analysis with cycle focus
    console.print("\n[yellow]Running detailed analysis with cycle focus...[/]")
    detailed_report = analyzer.generate_report(
        video_url=video_url,
        prompt_type="detailed",
        save_to_file=True,
        filename="example_detailed"
    )
    
    console.print("[green]✓ Traditional analysis complete![/]")


def main():
    """Run all examples"""
    console = Console()
    
    console.print("\n[bold magenta]═══════════════════════════════════════════════════════")
    console.print("[bold magenta]  Excavator Video Analyzer - Example Usage")
    console.print("[bold magenta]  ADK Multi-Agent System Examples")
    console.print("[bold magenta]═══════════════════════════════════════════════════════[/]\n")
    
    console.print("[bold]Choose an example to run:[/]")
    console.print("1. Multi-Agent Analysis (Recommended)")
    console.print("2. Custom Configuration")
    console.print("3. Individual Agents")
    console.print("4. Cycle Time Report")
    console.print("5. Traditional Analysis")
    console.print("6. Run All Examples\n")
    
    choice = input("Enter your choice (1-6): ").strip()
    
    examples = {
        "1": example_multi_agent_analysis,
        "2": example_custom_config,
        "3": example_individual_agents,
        "4": example_cycle_time_report,
        "5": example_traditional_analysis,
    }
    
    if choice in examples:
        examples[choice]()
    elif choice == "6":
        for example_func in examples.values():
            example_func()
            console.print("\n[dim]─────────────────────────────────────────[/]\n")
    else:
        console.print("[red]Invalid choice. Please run again.[/]")
    
    console.print("\n[bold green]All examples completed![/]")
    console.print("[cyan]Check the 'reports/' directory for saved reports.[/]\n")


if __name__ == "__main__":
    main()


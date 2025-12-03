"""Quick test for HTML report generation using template (bypassing AI)"""

import os
import sys
from datetime import datetime
from rich.console import Console

# Set environment variable to disable AI generation in HTMLAssembler
os.environ['HTML_ASSEMBLER_USE_TEMPLATE'] = '1'

from html_report_analyzer import HTMLReportAnalyzer
from agents.report_orchestrator_agent import ReportOrchestrator

console = Console()

def test_template_generation():
    """Test HTML report with template-based generation (no AI)"""
    console.print("\n[bold cyan]Testing HTML Report with Template Generation[/bold cyan]\n")
    
    try:
        # Sample cycle data
        sample_cycle_data = [
            {
                "cycle_num": 1,
                "start_time": "00:10",
                "end_time": "00:28",
                "start_time_sec": 10,
                "end_time_sec": 28,
                "duration": 18,
                "notes": "Smooth operation, good coordination",
            },
            {
                "cycle_num": 2,
                "start_time": "00:30",
                "end_time": "00:50",
                "start_time_sec": 30,
                "end_time_sec": 50,
                "duration": 20,
                "notes": "Slight hesitation during swing phase",
            },
            {
                "cycle_num": 3,
                "start_time": "00:52",
                "end_time": "01:11",
                "start_time_sec": 52,
                "end_time_sec": 71,
                "duration": 19,
                "notes": "Good bucket fill, efficient dump",
            },
        ]
        
        # Initialize orchestrator with AI disabled for HTML assembler
        console.print("[bold]Step 1:[/bold] Initializing orchestrator (template mode)...")
        config = {
            "html_assembler": {"use_ai": False}  # Disable AI, use template
        }
        orchestrator = ReportOrchestrator(config=config)
        console.print("[green]✓[/green] Orchestrator initialized\n")
        
        # Prepare paths
        joystick_data_path = os.path.join(os.getcwd(), "data", "joystick_data")
        operator_info = {
            "operator_name": "Test Operator (Quick)",
            "equipment": "Excavator CAT 320",
            "exercise_date": datetime.now().strftime("%Y-%m-%d"),
            "session_duration": "1 minute 11 seconds",
        }
        
        console.print("[bold]Step 2:[/bold] Running report generation pipeline...\n")
        result = orchestrator.run_pipeline(
            cycle_data=sample_cycle_data,
            joystick_data_path=joystick_data_path,
            operator_info=operator_info,
        )
        
        # Save the report
        console.print("\n[bold]Step 3:[/bold] Saving report...")
        output_file = "reports/test_quick_template.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['html_report'])
        
        console.print(f"[green]✓[/green] Report saved to {output_file}\n")
        console.print("[bold green]✓ Template-based generation successful![/bold green]\n")
        
        return True
        
    except Exception as e:
        console.print(f"[bold red]✗ Test failed: {e}[/bold red]")
        import traceback
        console.print(f"\n[red]{traceback.format_exc()}[/red]")
        return False


if __name__ == "__main__":
    console.print("\n" + "="*70)
    console.print(" " * 15 + "[bold cyan]QUICK HTML TEMPLATE TEST[/bold cyan]")
    console.print("="*70)
    console.print("\n[yellow]This test uses template-based generation (no AI calls)[/yellow]")
    console.print("[yellow]This is much faster and good for testing the pipeline[/yellow]\n")
    
    success = test_template_generation()
    
    if success:
        console.print("[bold]Usage:[/bold]")
        console.print("  • Open reports/test_quick_template.html in browser")
        console.print("  • For AI-powered generation, use: python test_html_report.py\n")
        sys.exit(0)
    else:
        sys.exit(1)


"""Test script for HTML report generation system"""

import os
import sys
from datetime import datetime

from rich.console import Console

# Add parent directory to path to import from scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.html_report_analyzer import HTMLReportAnalyzer
from scripts.video_analyzer import VideoAnalyzer

# Default test video URL (YouTube)
DEFAULT_VIDEO_URL = "https://www.youtube.com/watch?v=8PAU1LNXYR0"


def test_html_report_with_sample_data(use_real_video=False, video_url=None):
    """Test HTML report generation with sample cycle data or real video analysis
    
    Args:
        use_real_video (bool): If True, analyze a real video; if False, use sample data
        video_url (str, optional): YouTube video URL to analyze (uses default if None)
    """
    console = Console()
    
    console.print("\n[bold cyan]═══ Testing HTML Report Generation System ═══[/bold cyan]\n")
    
    try:
        # Initialize the analyzer
        console.print("[bold]Step 1:[/bold] Initializing HTMLReportAnalyzer...")
        analyzer = HTMLReportAnalyzer(reports_dir="reports")
        console.print("[green]✓[/green] HTMLReportAnalyzer initialized\n")
        
        # Get cycle data - either from real video analysis or sample data
        if use_real_video:
            console.print("[bold]Step 2:[/bold] Analyzing video for cycle data...")
            
            # Initialize VideoAnalyzer
            video_analyzer = VideoAnalyzer()
            
            # Use provided video URL or default
            test_video_url = video_url or DEFAULT_VIDEO_URL
            console.print(f"  Video URL: {test_video_url}")
            
            # Generate report from video
            console.print("  [yellow]Analyzing video (this may take a moment)...[/yellow]")
            report = video_analyzer.generate_report(
                video_url=test_video_url,
                prompt_type="cycle_time_simple",
                save_to_file=False
            )
            
            if not report:
                console.print("[red]✗[/red] Failed to analyze video, falling back to sample data\n")
                use_real_video = False
            else:
                # Parse cycle data from report
                cycle_data = VideoAnalyzer.parse_cycle_data(report)
                
                if not cycle_data:
                    console.print("[red]✗[/red] No cycle data found in report, falling back to sample data\n")
                    use_real_video = False
                else:
                    console.print(f"[green]✓[/green] Analyzed video and extracted {len(cycle_data)} cycles\n")
        
        # Fall back to sample data if not using real video or if video analysis failed
        if not use_real_video:
            console.print("[bold]Step 2:[/bold] Preparing sample cycle data...")
            cycle_data = [
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
                {
                    "cycle_num": 4,
                    "start_time": "01:13",
                    "end_time": "01:34",
                    "start_time_sec": 73,
                    "end_time_sec": 94,
                    "duration": 21,
                    "notes": "Standard cycle time",
                },
                {
                    "cycle_num": 5,
                    "start_time": "01:36",
                    "end_time": "01:53",
                    "start_time_sec": 96,
                    "end_time_sec": 113,
                    "duration": 17,
                    "notes": "Fastest cycle, excellent coordination",
                },
            ]
            console.print(f"[green]✓[/green] Prepared {len(cycle_data)} sample cycles\n")
        
        # Path to joystick data
        console.print("[bold]Step 3:[/bold] Setting joystick data path...")
        joystick_data_path = os.path.join(os.getcwd(), "data", "joystick_data")
        
        if not os.path.exists(joystick_data_path):
            console.print(f"[yellow]Warning:[/yellow] Joystick data not found at {joystick_data_path}")
            console.print("[yellow]The report will be generated with fallback data[/yellow]\n")
        else:
            console.print(f"[green]✓[/green] Joystick data found at {joystick_data_path}\n")
        
        # Operator information
        console.print("[bold]Step 4:[/bold] Preparing operator information...")
        operator_info = {
            "operator_name": "Test Operator B8",
            "equipment": "Excavator CAT 320",
            "exercise_date": datetime.now().strftime("%Y-%m-%d"),
            "session_duration": "2 minutes 20 seconds",
        }
        console.print("[green]✓[/green] Operator info prepared\n")
        
        # Generate the HTML report
        console.print("[bold]Step 5:[/bold] Generating HTML report...\n")
        html_report = analyzer.generate_html_report(
            cycle_data=cycle_data,
            joystick_data_path=joystick_data_path,
            operator_info=operator_info,
            save_to_file=True,
            filename="test_html_report",
        )
        
        # Get pipeline data for verification
        pipeline_data = analyzer.get_pipeline_data()
        
        # Display summary
        console.print("\n[bold cyan]═══ Report Generation Summary ═══[/bold cyan]\n")
        
        cycle_metrics = pipeline_data.get("cycle_metrics", {})
        performance_scores = pipeline_data.get("performance_scores", {})
        insights = pipeline_data.get("insights", {})
        
        console.print(f"[bold]Cycle Metrics:[/bold]")
        console.print(f"  • Total Cycles: {cycle_metrics.get('total_cycles', 0)}")
        console.print(f"  • Average Cycle Time: {cycle_metrics.get('average_cycle_time', 0)}s")
        console.print(f"  • Consistency Score: {cycle_metrics.get('consistency_score', 0):.1f}%")
        console.print(f"  • Trend: {cycle_metrics.get('cycle_time_trend', 'Unknown')}\n")
        
        console.print(f"[bold]Performance Scores:[/bold]")
        console.print(f"  • Productivity: {performance_scores.get('productivity_score', 0)}/100 ({performance_scores.get('productivity_status', 'Unknown')})")
        console.print(f"  • Control Skill: {performance_scores.get('control_skill_score', 0)}/100 ({performance_scores.get('control_skill_status', 'Unknown')})")
        console.print(f"  • Safety: {performance_scores.get('safety_score', 0)}/100 ({performance_scores.get('safety_status', 'Unknown')})\n")
        
        console.print(f"[bold]AI Insights:[/bold]")
        console.print(f"  • Proficiency Level: {insights.get('proficiency_level', 'Unknown')}")
        console.print(f"  • Training Hours Needed: {insights.get('estimated_training_hours', 'N/A')}")
        console.print(f"  • Recommendations: {len(insights.get('training_recommendations', []))} provided\n")
        
        console.print("[bold green]✓ Test completed successfully![/bold green]")
        console.print(f"\n[bold]HTML Report saved to:[/bold] reports/test_html_report.html\n")
        
        return True
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed: {e}[/bold red]")
        import traceback
        console.print(f"\n[red]{traceback.format_exc()}[/red]")
        return False


def test_with_real_video_data(video_url=None):
    """Test HTML report generation with real video analysis
    
    Args:
        video_url (str, optional): YouTube video URL to analyze (uses default if None)
    """
    console = Console()
    
    console.print("\n[bold cyan]═══ Testing with Real Video Data (YouTube) ═══[/bold cyan]\n")
    
    try:
        # Use provided video URL or default
        test_video_url = video_url or DEFAULT_VIDEO_URL
        console.print(f"[bold]Video URL:[/bold] {test_video_url}\n")
        
        # Call the main test function with real video flag
        return test_html_report_with_sample_data(use_real_video=True, video_url=test_video_url)
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed: {e}[/bold red]")
        import traceback
        console.print(f"\n[red]{traceback.format_exc()}[/red]")
        return False


def main():
    """Main test runner"""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test HTML report generation system')
    parser.add_argument('--video-url', type=str, default=None,
                        help=f'YouTube video URL to analyze (default: {DEFAULT_VIDEO_URL})')
    parser.add_argument('--use-real-video', action='store_true',
                        help='Analyze a real video instead of using sample data')
    parser.add_argument('--sample-only', action='store_true',
                        help='Only test with sample data (skip video analysis)')
    args = parser.parse_args()
    
    console = Console()
    
    console.print("\n" + "="*80)
    console.print(" " * 20 + "[bold cyan]HTML REPORT GENERATOR TEST SUITE[/bold cyan]")
    console.print("="*80 + "\n")
    
    # Determine which test to run
    if args.sample_only:
        # Test 1: Sample data only
        console.print("\n[bold]TEST: Sample Cycle Data[/bold]")
        console.print("-" * 80)
        result1 = test_html_report_with_sample_data(use_real_video=False)
        result2 = None
    elif args.use_real_video or args.video_url:
        # Test with real video
        console.print("\n[bold]TEST: Real Video Analysis[/bold]")
        console.print("-" * 80)
        result1 = test_with_real_video_data(video_url=args.video_url)
        result2 = None
    else:
        # Run both tests
        console.print("\n[bold]TEST 1: Sample Cycle Data[/bold]")
        console.print("-" * 80)
        result1 = test_html_report_with_sample_data(use_real_video=False)
        
        console.print("\n[bold]TEST 2: Real Video Analysis[/bold]")
        console.print("-" * 80)
        console.print("[yellow]To run real video test, use: python test_html_report.py --use-real-video[/yellow]\n")
        result2 = None
    
    # Summary
    console.print("\n" + "="*80)
    console.print(" " * 30 + "[bold]TEST SUMMARY[/bold]")
    console.print("="*80 + "\n")
    
    if result1:
        console.print("[bold green]✓ Tests completed successfully![/bold green]\n")
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Open reports/test_html_report.html in a browser")
        console.print("  2. Verify all sections are populated correctly")
        console.print("  3. Run with --use-real-video to test video analysis")
        console.print("  4. Integrate with Flask app endpoints\n")
        console.print("[bold]Usage examples:[/bold]")
        console.print("  python test_html_report.py                    # Sample data test")
        console.print("  python test_html_report.py --use-real-video   # Real video test")
        console.print("  python test_html_report.py --video-url <URL>  # Custom video URL\n")
        return 0
    else:
        console.print("[bold red]✗ Some tests failed[/bold red]\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())


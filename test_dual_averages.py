"""
Test script for dual average cycle time calculations
"""

from cycle_time_analyzer import CycleTimeAnalyzer
from rich.console import Console
from rich.markdown import Markdown


def test_dual_averages():
    """Test both average calculation methods"""
    
    console = Console()
    console.print("[bold blue]Testing Dual Average Cycle Time Calculations[/]\n")
    
    # Sample cycle data with gaps between cycles
    # Cycle 1: 0:07 to 0:35 (28s work)
    # GAP: 7 seconds idle
    # Cycle 2: 0:42 to 1:07 (25s work)
    # GAP: 5 seconds idle  
    # Cycle 3: 1:12 to 1:42 (30s work)
    # GAP: 3 seconds idle
    # Cycle 4: 1:45 to 2:10 (25s work)
    # GAP: 5 seconds idle
    # Cycle 5: 2:15 to 2:45 (30s work)
    
    sample_cycles = [
        {
            'cycle_num': 1,
            'start_time': '00:07',
            'end_time': '00:35',
            'start_time_sec': 7,
            'end_time_sec': 35,
            'duration': 28,
            'notes': 'Good execution'
        },
        {
            'cycle_num': 2,
            'start_time': '00:42',
            'end_time': '01:07',
            'start_time_sec': 42,
            'end_time_sec': 67,
            'duration': 25,
            'notes': 'Faster'
        },
        {
            'cycle_num': 3,
            'start_time': '01:12',
            'end_time': '01:42',
            'start_time_sec': 72,
            'end_time_sec': 102,
            'duration': 30,
            'notes': 'Slower'
        },
        {
            'cycle_num': 4,
            'start_time': '01:45',
            'end_time': '02:10',
            'start_time_sec': 105,
            'end_time_sec': 130,
            'duration': 25,
            'notes': 'Good'
        },
        {
            'cycle_num': 5,
            'start_time': '02:15',
            'end_time': '02:45',
            'start_time_sec': 135,
            'end_time_sec': 165,
            'duration': 30,
            'notes': 'Normal'
        },
    ]

    analyzer = CycleTimeAnalyzer()
    
    # Calculate statistics
    console.print("[bold green]Step 1:[/] Calculating statistics...\n")
    stats = analyzer.calculate_statistics(sample_cycles)
    
    # Display raw statistics
    console.print("[bold cyan]Raw Statistics:[/]")
    console.print(f"Total Cycles: {stats['total_cycles']}")
    console.print(f"Durations: {stats['durations']}")
    console.print(f"\n[bold yellow]Approximate Average Duration:[/] {stats['approximate_average_duration']:.2f}s")
    console.print(f"  → Calculation: (last_end - first_start) / total_cycles")
    console.print(f"  → ({sample_cycles[-1]['end_time_sec']} - {sample_cycles[0]['start_time_sec']}) / {len(sample_cycles)}")
    console.print(f"  → ({165} - {7}) / {5} = {158 / 5}s")
    
    console.print(f"\n[bold yellow]Specific Average Duration:[/] {stats['specific_average_duration']:.2f}s")
    console.print(f"  → Calculation: sum(durations) / total_cycles")
    console.print(f"  → ({' + '.join(map(str, stats['durations']))}) / {len(sample_cycles)}")
    console.print(f"  → {sum(stats['durations'])} / {len(sample_cycles)} = {sum(stats['durations']) / len(sample_cycles)}s")
    
    console.print(f"\n[bold yellow]Idle Time per Cycle:[/] {stats['idle_time_per_cycle']:.2f}s")
    console.print(f"  → Calculation: approximate_avg - specific_avg")
    console.print(f"  → {stats['approximate_average_duration']:.2f} - {stats['specific_average_duration']:.2f} = {stats['idle_time_per_cycle']:.2f}s")
    
    console.print(f"\nMin: {stats['min_duration']}s")
    console.print(f"Max: {stats['max_duration']}s")
    console.print(f"Std Dev: {stats['std_deviation']:.2f}s")
    
    # Generate and display simple report
    console.print("\n[bold green]Step 2:[/] Generating Simple Mode report...\n")
    simple_report = analyzer.generate_analysis_report(stats, use_ai=False)
    
    console.print("[bold cyan]--- Simple Mode Report ---[/]")
    console.print(Markdown(simple_report))
    
    # Verify calculations manually
    console.print("\n[bold green]Step 3:[/] Verification\n")
    
    expected_approx = (165 - 7) / 5  # 31.6
    expected_specific = (28 + 25 + 30 + 25 + 30) / 5  # 27.6
    expected_idle = expected_approx - expected_specific  # 4.0
    
    console.print(f"✓ Approximate Average: Expected {expected_approx:.2f}s, Got {stats['approximate_average_duration']:.2f}s")
    console.print(f"✓ Specific Average: Expected {expected_specific:.2f}s, Got {stats['specific_average_duration']:.2f}s")
    console.print(f"✓ Idle Time: Expected {expected_idle:.2f}s, Got {stats['idle_time_per_cycle']:.2f}s")
    
    # Verify assertions
    assert abs(stats['approximate_average_duration'] - expected_approx) < 0.01, "Approximate average calculation is incorrect"
    assert abs(stats['specific_average_duration'] - expected_specific) < 0.01, "Specific average calculation is incorrect"
    assert abs(stats['idle_time_per_cycle'] - expected_idle) < 0.01, "Idle time calculation is incorrect"
    
    console.print("\n[bold green]✅ All tests passed![/]")
    
    # Interpretation
    console.print("\n[bold cyan]Interpretation:[/]")
    console.print("• Approximate avg (31.6s) includes the gaps between cycles")
    console.print("• Specific avg (27.6s) measures only the actual work time")
    console.print("• The difference (4.0s) shows idle time per cycle")
    console.print("• This means operators spend about 12.7% of time in transitions/idle")


if __name__ == "__main__":
    test_dual_averages()


"""
Cycle Time Report Generator - Formats and analyzes cycle time data
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table


class CycleTimeReport:
    """Generator for structured cycle time reports"""

    def __init__(self):
        """Initialize the cycle time report generator"""
        self.console = Console()

    def generate_markdown_report(
        self,
        cycles: List[Dict[str, Any]],
        summary: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a comprehensive markdown report from cycle data

        Args:
            cycles (List[Dict[str, Any]]): List of detected cycles
            summary (Dict[str, Any]): Summary statistics
            metadata (Dict[str, Any], optional): Additional metadata

        Returns:
            str: Formatted markdown report
        """
        report = "# Excavator Cycle Time Analysis Report\n\n"
        
        # Add metadata if provided
        if metadata:
            report += "## Report Information\n\n"
            report += f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            if 'video_url' in metadata:
                report += f"- **Video URL**: {metadata['video_url']}\n"
            if 'analysis_date' in metadata:
                report += f"- **Analysis Date**: {metadata['analysis_date']}\n"
            report += "\n"

        # Executive Summary
        report += "## Executive Summary\n\n"
        
        total_cycles = summary.get('total_cycles', len(cycles))
        report += f"- **Total Cycles Detected**: {total_cycles}\n"
        
        if 'average_cycle_time' in summary:
            avg_time = summary['average_cycle_time']
            report += f"- **Average Cycle Time**: {avg_time}\n"
        
        if 'video_duration' in summary:
            report += f"- **Video Duration**: {summary['video_duration']}\n"
        
        if 'fastest_cycle' in summary:
            fastest = summary['fastest_cycle']
            if isinstance(fastest, dict):
                report += f"- **Fastest Cycle**: Cycle {fastest.get('id', '?')} ({fastest.get('time', '?')})\n"
            else:
                report += f"- **Fastest Cycle**: {fastest}\n"
        
        if 'slowest_cycle' in summary:
            slowest = summary['slowest_cycle']
            if isinstance(slowest, dict):
                report += f"- **Slowest Cycle**: Cycle {slowest.get('id', '?')} ({slowest.get('time', '?')})\n"
            else:
                report += f"- **Slowest Cycle**: {slowest}\n"
        
        report += "\n---\n\n"

        # Detailed Cycle Breakdown
        if cycles:
            report += "## Detailed Cycle Breakdown\n\n"
            
            # Create table
            report += "| Cycle | Start | End | Total Duration | Dig | Swing to Dump | Dump | Return |\n"
            report += "|-------|-------|-----|----------------|-----|---------------|------|--------|\n"
            
            for cycle in cycles:
                cycle_id = cycle.get('id', '?')
                start = cycle.get('start', '?')
                end = cycle.get('end', '?')
                duration = cycle.get('total_duration', '?')
                
                phases = cycle.get('phases', {})
                dig_dur = phases.get('dig', {}).get('duration', '-')
                swing_dur = phases.get('swing_to_dump', {}).get('duration', '-')
                dump_dur = phases.get('dump', {}).get('duration', '-')
                return_dur = phases.get('return', {}).get('duration', '-')
                
                report += f"| {cycle_id} | {start} | {end} | {duration} | {dig_dur} | {swing_dur} | {dump_dur} | {return_dur} |\n"
            
            report += "\n"

        # Performance Metrics
        report += "## Performance Metrics\n\n"
        
        if cycles:
            metrics = self._calculate_metrics(cycles)
            
            report += "### Phase Duration Analysis\n\n"
            report += f"- **Average Dig Phase**: {metrics['avg_dig']:.1f}s\n"
            report += f"- **Average Swing to Dump**: {metrics['avg_swing_to_dump']:.1f}s\n"
            report += f"- **Average Dump Phase**: {metrics['avg_dump']:.1f}s\n"
            report += f"- **Average Return Swing**: {metrics['avg_return']:.1f}s\n\n"
            
            report += "### Efficiency Metrics\n\n"
            report += f"- **Productivity Rate**: {metrics['productivity_rate']:.1f} cycles/hour\n"
            report += f"- **Cycle Time Consistency**: {metrics['consistency_score']:.0f}%\n"
            
            # Benchmark comparison
            optimal_range = (35, 45)
            avg_cycle_time = metrics['avg_total']
            
            report += "\n### Benchmark Comparison\n\n"
            report += "**Industry Benchmarks:**\n"
            report += "- Optimal: 35-45 seconds\n"
            report += "- Acceptable: 45-60 seconds\n"
            report += "- Below Standard: >60 seconds\n\n"
            
            if optimal_range[0] <= avg_cycle_time <= optimal_range[1]:
                report += f"✅ **Status**: Performance is in the optimal range ({avg_cycle_time:.1f}s)\n"
            elif avg_cycle_time <= 60:
                report += f"⚠️ **Status**: Performance is acceptable but can be improved ({avg_cycle_time:.1f}s)\n"
            else:
                report += f"❌ **Status**: Performance needs improvement ({avg_cycle_time:.1f}s)\n"
        
        report += "\n---\n\n"

        # Recommendations
        if cycles:
            report += "## Recommendations\n\n"
            recommendations = self._generate_recommendations(cycles, metrics)
            
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
        
        return report

    def _calculate_metrics(self, cycles: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate performance metrics from cycle data

        Args:
            cycles (List[Dict[str, Any]]): List of cycles

        Returns:
            Dict[str, float]: Calculated metrics
        """
        metrics = {
            'avg_dig': 0.0,
            'avg_swing_to_dump': 0.0,
            'avg_dump': 0.0,
            'avg_return': 0.0,
            'avg_total': 0.0,
            'productivity_rate': 0.0,
            'consistency_score': 0.0
        }

        if not cycles:
            return metrics

        # Collect phase durations
        dig_times = []
        swing_times = []
        dump_times = []
        return_times = []
        total_times = []

        for cycle in cycles:
            phases = cycle.get('phases', {})
            
            # Parse duration strings
            if 'dig' in phases:
                dig_times.append(self._parse_duration(phases['dig'].get('duration', '0s')))
            if 'swing_to_dump' in phases:
                swing_times.append(self._parse_duration(phases['swing_to_dump'].get('duration', '0s')))
            if 'dump' in phases:
                dump_times.append(self._parse_duration(phases['dump'].get('duration', '0s')))
            if 'return' in phases:
                return_times.append(self._parse_duration(phases['return'].get('duration', '0s')))
            
            total_times.append(self._parse_duration(cycle.get('total_duration', '0s')))

        # Calculate averages
        if dig_times:
            metrics['avg_dig'] = sum(dig_times) / len(dig_times)
        if swing_times:
            metrics['avg_swing_to_dump'] = sum(swing_times) / len(swing_times)
        if dump_times:
            metrics['avg_dump'] = sum(dump_times) / len(dump_times)
        if return_times:
            metrics['avg_return'] = sum(return_times) / len(return_times)
        if total_times:
            metrics['avg_total'] = sum(total_times) / len(total_times)
            
            # Calculate productivity rate (cycles per hour)
            if metrics['avg_total'] > 0:
                metrics['productivity_rate'] = 3600 / metrics['avg_total']
            
            # Calculate consistency (100% - coefficient of variation)
            if len(total_times) > 1:
                import statistics
                mean = statistics.mean(total_times)
                stdev = statistics.stdev(total_times)
                cv = (stdev / mean) * 100 if mean > 0 else 100
                metrics['consistency_score'] = max(0, 100 - cv)

        return metrics

    def _parse_duration(self, duration_str: str) -> float:
        """
        Parse duration string to float seconds

        Args:
            duration_str (str): Duration string (e.g., "9.9s")

        Returns:
            float: Duration in seconds
        """
        try:
            return float(duration_str.replace('s', '').strip())
        except ValueError:
            return 0.0

    def _generate_recommendations(
        self,
        cycles: List[Dict[str, Any]],
        metrics: Dict[str, float]
    ) -> List[str]:
        """
        Generate recommendations based on cycle data

        Args:
            cycles (List[Dict[str, Any]]): Cycle data
            metrics (Dict[str, float]): Calculated metrics

        Returns:
            List[str]: List of recommendations
        """
        recommendations = []

        # Benchmark values
        optimal_dig = (8, 12)
        optimal_swing = (9, 13)
        optimal_dump = (3, 5)
        optimal_return = (8, 12)

        # Check dig phase
        if metrics['avg_dig'] > optimal_dig[1]:
            diff = metrics['avg_dig'] - optimal_dig[1]
            recommendations.append(
                f"Dig phase is {diff:.1f}s slower than optimal. Practice more aggressive digging technique and optimize bucket penetration angle."
            )
        
        # Check swing phase
        if metrics['avg_swing_to_dump'] > optimal_swing[1]:
            diff = metrics['avg_swing_to_dump'] - optimal_swing[1]
            recommendations.append(
                f"Swing to dump phase is {diff:.1f}s slower than optimal. Reduce swing arc by optimizing machine positioning and minimize wasted motion."
            )
        
        # Check dump phase
        if metrics['avg_dump'] > optimal_dump[1]:
            diff = metrics['avg_dump'] - optimal_dump[1]
            recommendations.append(
                f"Dump phase is {diff:.1f}s slower than optimal. Practice faster bucket opening and more decisive material release."
            )
        
        # Check return phase
        if metrics['avg_return'] > optimal_return[1]:
            diff = metrics['avg_return'] - optimal_return[1]
            recommendations.append(
                f"Return swing is {diff:.1f}s slower than optimal. Work on tighter return paths and maintain momentum between cycles."
            )
        
        # Check consistency
        if metrics['consistency_score'] < 80:
            recommendations.append(
                f"Cycle time consistency is {metrics['consistency_score']:.0f}%. Focus on maintaining a steady rhythm and reducing variation between cycles."
            )
        
        # Overall performance
        if metrics['avg_total'] > 60:
            potential_improvement = metrics['avg_total'] - 45
            recommendations.append(
                f"Overall cycle time can potentially be reduced by {potential_improvement:.1f}s through focused training on identified weaknesses."
            )
        
        if not recommendations:
            recommendations.append("Excellent performance! Continue maintaining current technique and consistency.")

        return recommendations

    def display_table(self, cycles: List[Dict[str, Any]]):
        """
        Display cycle data as a formatted table in the console

        Args:
            cycles (List[Dict[str, Any]]): List of cycles to display
        """
        table = Table(title="Cycle Time Analysis")
        
        table.add_column("Cycle", style="cyan", justify="center")
        table.add_column("Start", style="green")
        table.add_column("End", style="green")
        table.add_column("Duration", style="yellow")
        table.add_column("Dig", style="blue")
        table.add_column("Swing", style="blue")
        table.add_column("Dump", style="blue")
        table.add_column("Return", style="blue")
        
        for cycle in cycles:
            phases = cycle.get('phases', {})
            table.add_row(
                str(cycle.get('id', '?')),
                cycle.get('start', '?'),
                cycle.get('end', '?'),
                cycle.get('total_duration', '?'),
                phases.get('dig', {}).get('duration', '-'),
                phases.get('swing_to_dump', {}).get('duration', '-'),
                phases.get('dump', {}).get('duration', '-'),
                phases.get('return', {}).get('duration', '-'),
            )
        
        self.console.print(table)

    def save_report(
        self,
        report_text: str,
        filename: Optional[str] = None,
        reports_dir: str = "reports"
    ) -> Path:
        """
        Save report to file

        Args:
            report_text (str): Report content
            filename (str, optional): Custom filename
            reports_dir (str): Directory to save reports

        Returns:
            Path: Path to saved file
        """
        reports_path = Path(reports_dir)
        reports_path.mkdir(exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cycle_time_report_{timestamp}.md"
        elif not filename.endswith(".md"):
            filename = f"{filename}.md"
        
        file_path = reports_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        self.console.print(f"[bold green]Cycle time report saved to: {file_path}")
        return file_path


"""Cycle metrics calculation agent"""

from typing import Any, Dict, List, Optional
import statistics

from .base_agent import BaseAgent


class CycleMetricsAgent(BaseAgent):
    """Agent responsible for calculating cycle time metrics from video analysis data"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("CycleMetrics", config)

    def process(
        self, input_data: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process cycle data and calculate comprehensive metrics

        Args:
            input_data: List of cycle dictionaries from video_analyzer
            context: Optional context

        Returns:
            Dictionary containing calculated metrics
        """
        self.log(f"Calculating metrics for {len(input_data)} cycles", "info")

        if not input_data:
            self.log("No cycle data provided", "warning")
            return {
                "total_cycles": 0,
                "average_cycle_time": 0,
                "min_cycle_time": 0,
                "max_cycle_time": 0,
                "variance": 0,
                "std_deviation": 0,
                "cycle_time_trend": "No data",
                "consistency_score": 0,
            }

        # Extract durations
        durations = [cycle.get("duration", 0) for cycle in input_data]

        # Calculate statistics
        total_cycles = len(durations)
        avg_duration = statistics.mean(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        variance = statistics.variance(durations) if total_cycles > 1 else 0
        std_dev = statistics.stdev(durations) if total_cycles > 1 else 0

        # Calculate consistency score (0-100, higher is better)
        # Based on coefficient of variation (lower CV = more consistent)
        cv = (std_dev / avg_duration) if avg_duration > 0 else 0
        consistency_score = max(0, min(100, 100 - (cv * 100)))

        # Determine cycle time trend
        trend = self._calculate_trend(durations)

        # Calculate efficiency benchmark (assuming 20s is target)
        target_cycle_time = 20.0
        efficiency_percentage = (target_cycle_time / avg_duration * 100) if avg_duration > 0 else 0

        metrics = {
            "total_cycles": total_cycles,
            "average_cycle_time": round(avg_duration, 2),
            "min_cycle_time": round(min_duration, 2),
            "max_cycle_time": round(max_duration, 2),
            "variance": round(variance, 2),
            "std_deviation": round(std_dev, 2),
            "cycle_time_trend": trend,
            "consistency_score": round(consistency_score, 1),
            "efficiency_percentage": round(efficiency_percentage, 1),
            "target_cycle_time": target_cycle_time,
            "cycles_data": input_data,
        }

        self.log(
            f"✓ Metrics calculated: Avg={avg_duration:.1f}s, Consistency={consistency_score:.1f}%",
            "success",
        )
        return metrics

    def _calculate_trend(self, durations: List[float]) -> str:
        """
        Calculate trend in cycle times

        Args:
            durations: List of cycle durations

        Returns:
            Trend description
        """
        if len(durations) < 3:
            return "Insufficient data"

        # Simple trend: compare first half vs second half
        mid = len(durations) // 2
        first_half_avg = statistics.mean(durations[:mid])
        second_half_avg = statistics.mean(durations[mid:])

        diff_percentage = ((second_half_avg - first_half_avg) / first_half_avg) * 100

        if diff_percentage < -5:
            return "Improving (faster over time)"
        elif diff_percentage > 5:
            return "Declining (slower over time)"
        else:
            return "Stable"


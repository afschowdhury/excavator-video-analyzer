"""Cycle metrics calculation agent"""

from typing import Any, Dict, List, Optional
import statistics
import base64

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from ..base_agent import BaseAgent


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

        # Generate cycle trend chart
        cycle_trend_chart = self._generate_cycle_trend_chart(input_data, avg_duration, target_cycle_time)

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
            "cycle_trend_chart": cycle_trend_chart,
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

    def _generate_cycle_trend_chart(self, cycles_data: List[Dict[str, Any]], avg_time: float, target_time: float) -> str:
        """
        Generate cycle time trend chart matching Plotly style of existing charts
        
        Args:
            cycles_data: List of cycle dictionaries
            avg_time: Average cycle time
            target_time: Target cycle time (benchmark)
            
        Returns:
            Base64-encoded PNG image string with data URI prefix
        """
        if not PLOTLY_AVAILABLE:
            self.log("Plotly not available, skipping chart generation", "warning")
            return ""
        
        try:
            # Extract data
            cycle_numbers = [c.get('cycle_number', c.get('cycle_num', i+1)) 
                           for i, c in enumerate(cycles_data)]
            durations = [c['duration'] for c in cycles_data]
            
            # Create figure with cycle time line
            fig = go.Figure()
            
            # Main cycle time line (matching Control Usage blue)
            fig.add_trace(go.Scatter(
                x=cycle_numbers,
                y=durations,
                mode='lines+markers',
                name='Cycle Time',
                line=dict(color='#4361ee', width=3),
                marker=dict(size=8, color='#4361ee')
            ))
            
            # Target line (20s benchmark) - green dashed
            fig.add_hline(
                y=target_time,
                line=dict(color='#27ae60', width=2, dash='dash'),
                annotation_text=f'Target ({target_time}s)',
                annotation_position='right'
            )
            
            # Average line - red dotted
            fig.add_hline(
                y=avg_time,
                line=dict(color='#e74c3c', width=2, dash='dot'),
                annotation_text=f'Avg ({avg_time:.1f}s)',
                annotation_position='right'
            )
            
            # Layout matching existing charts
            fig.update_layout(
                title=dict(
                    text='Cycle Time Trend Analysis',
                    x=0.5,
                    font=dict(size=18, family='Arial', color='#333')
                ),
                xaxis=dict(
                    title='Cycle Number',
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.08)',
                    gridwidth=1
                ),
                yaxis=dict(
                    title='Time (seconds)',
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.08)',
                    gridwidth=1,
                    zeroline=False
                ),
                width=650,
                height=450,
                font=dict(size=14, family='Arial'),
                plot_bgcolor='#fff',
                paper_bgcolor='#fff',
                margin=dict(t=80, l=60, r=60, b=60),
                showlegend=False  # Using annotations instead
            )
            
            # Convert to base64 PNG
            img_bytes = fig.to_image(format='png', scale=2)
            image_base64 = base64.b64encode(img_bytes).decode()
            
            self.log("✓ Cycle trend chart generated", "success")
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            self.log(f"Failed to generate cycle trend chart: {e}", "error")
            return ""


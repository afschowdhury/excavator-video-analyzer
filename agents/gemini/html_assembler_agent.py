"""HTML report assembler agent"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from icecream import ic
from jinja2 import Environment, FileSystemLoader

from ..base_agent import BaseAgent

ic.configureOutput(includeContext=True, prefix="HTMLAssemblerAgent- ")


class HTMLAssemblerAgent(BaseAgent):
    """Agent responsible for assembling the final HTML report using Jinja2 templates"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("HTMLAssembler", config)
        load_dotenv()
        
        # Setup Jinja2 environment
        template_dir = Path(__file__).parent.parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.template_name = "report_template.html"
        
        ic(f"HTMLAssemblerAgent initialized with template: {self.template_name}")

    def process(
        self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Assemble final HTML report from all components using Jinja2 template

        Args:
            input_data: Dictionary containing all analysis data
            context: Optional context with operator info

        Returns:
            Complete HTML report string
        """
        self.log("Assembling HTML report with Jinja2 Template", "info")

        # Extract operator info from context
        operator_name = context.get("operator_name", "[Operator Name]") if context else "[Operator Name]"
        equipment = context.get("equipment", "[Equipment Model/Type]") if context else "[Equipment Model/Type]"
        exercise_date = context.get("exercise_date", datetime.now().strftime("%Y-%m-%d")) if context else datetime.now().strftime("%Y-%m-%d")
        session_duration = context.get("session_duration", "N/A") if context else "N/A"

        # Prepare data for template
        template_data = self._prepare_template_data(input_data, operator_name, equipment, exercise_date, session_duration)
        
        try:
            template = self.env.get_template(self.template_name)
            html = template.render(**template_data)
            self.log("✓ HTML report assembled successfully", "success")
            return html
        except Exception as e:
            self.log(f"Template rendering failed: {e}", "error")
            raise

    def _prepare_template_data(
        self, data: Dict[str, Any], operator_name: str, equipment: str, exercise_date: str, session_duration: str
    ) -> Dict[str, Any]:
        """Prepare and enrich data for the template"""
        
        cycle_metrics = data.get("cycle_metrics", {})
        simulation_metrics = data.get("simulation_metrics", {})
        joystick_analytics = data.get("joystick_analytics", {})
        chart_analysis = data.get("chart_analysis", {})
        insights = data.get("insights", {})
        behavior_analysis = data.get("behavior_analysis")

        # Enrich Cycle Metrics
        avg_cycle_time = cycle_metrics.get('average_cycle_time', 0)
        target_cycle_time = cycle_metrics.get('target_cycle_time', 20)
        variance = cycle_metrics.get('variance', 0)
        consistency = cycle_metrics.get('consistency_score', 0)

        enriched_cycle_metrics = {
            **cycle_metrics,
            'performance_class': self._get_performance_class(avg_cycle_time, target_cycle_time),
            'performance_text': self._get_performance_text(avg_cycle_time, target_cycle_time),
            'variance_status': self._get_variance_status(variance),
            'consistency_class': self._get_score_class(consistency),
            'consistency_status': self._get_status_from_score(consistency)
        }

        # Behavior Analysis - convert markdown summary if exists
        enriched_behavior = None
        if behavior_analysis:
            enriched_behavior = behavior_analysis.copy()
            if 'summary_report' in enriched_behavior:
                enriched_behavior['summary_html'] = self._markdown_to_html(enriched_behavior['summary_report'])

        # Chart Analysis - convert markdown if exists
        enriched_chart = chart_analysis.copy()
        if 'chart_analysis_markdown' in enriched_chart:
            enriched_chart['chart_analysis_html'] = self._markdown_to_html(enriched_chart['chart_analysis_markdown'])

        # Simulation Metrics - format for display
        enriched_simulation = None
        if simulation_metrics and simulation_metrics.get('found'):
            enriched_simulation = {
                'found': True,
                'video_id': simulation_metrics.get('video_id', 'Unknown'),
                'productivity': simulation_metrics.get('productivity'),
                'fuel_burned': simulation_metrics.get('fuel_burned'),
                'time_swinging_left': simulation_metrics.get('time_swinging_left'),
                'time_swinging_right': simulation_metrics.get('time_swinging_right'),
            }

        return {
            'operator_name': operator_name,
            'equipment': equipment,
            'exercise_date': exercise_date,
            'session_duration': session_duration,
            'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'cycle_metrics': enriched_cycle_metrics,
            'simulation_metrics': enriched_simulation,
            'joystick_analytics': joystick_analytics,
            'chart_analysis': enriched_chart,
            'insights': insights,
            'behavior_analysis': enriched_behavior
        }

    def _get_score_class(self, score: float) -> str:
        """Get CSS class based on score"""
        if score >= 85:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "satisfactory"
        else:
            return "needs-improvement"

    def _get_status_from_score(self, score: float) -> str:
        """Get status text from score"""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Satisfactory"
        else:
            return "Needs Improvement"

    def _get_performance_class(self, actual: float, target: float) -> str:
        """Get performance class based on actual vs target"""
        if target == 0:
            return "satisfactory"
        diff_pct = abs(actual - target) / target * 100
        if diff_pct < 5:
            return "excellent"
        elif diff_pct < 15:
            return "good"
        elif diff_pct < 25:
            return "satisfactory"
        else:
            return "needs-improvement"

    def _get_performance_text(self, actual: float, target: float) -> str:
        """Get performance text based on actual vs target"""
        if actual < target:
            return "Above Target"
        elif actual == target:
            return "On Target"
        else:
            return "Below Target"

    def _get_variance_status(self, variance: float) -> str:
        """Get variance status text"""
        if variance < 5:
            return "Excellent"
        elif variance < 15:
            return "Good"
        else:
            return "High Variance"

    def _markdown_to_html(self, markdown: str) -> str:
        """Convert markdown to HTML (robust line-by-line conversion)"""
        if not markdown:
            return ""
        
        import re
        
        lines = markdown.split('\n')
        result_lines = []
        in_list = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                # Close list if we were in one
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                result_lines.append('')
                continue
            
            # Handle horizontal rules
            if stripped in ['---', '***', '___']:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                result_lines.append('<hr>')
                continue
            
            # Handle headers (# to H3, ## to H4, ### to H5, #### to H6)
            if stripped.startswith('####'):
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                content = stripped[4:].strip()
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                result_lines.append(f'<h6>{content}</h6>')
                continue
            elif stripped.startswith('###'):
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                content = stripped[3:].strip()
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                result_lines.append(f'<h5>{content}</h5>')
                continue
            elif stripped.startswith('##'):
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                content = stripped[2:].strip()
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                result_lines.append(f'<h4>{content}</h4>')
                continue
            elif stripped.startswith('#'):
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                content = stripped[1:].strip()
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                result_lines.append(f'<h3>{content}</h3>')
                continue
            
            # Handle bullet points
            if stripped.startswith('- ') or stripped.startswith('* '):
                content = stripped[2:].strip()
                content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                result_lines.append(f'<li>{content}</li>')
                continue
            
            # Handle regular paragraphs
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            
            # Convert bold text
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
            result_lines.append(f'<p>{content}</p>')
        
        # Close list if still open
        if in_list:
            result_lines.append('</ul>')
        
        return '\n'.join(result_lines)

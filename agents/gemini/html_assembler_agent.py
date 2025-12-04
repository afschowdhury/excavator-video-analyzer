"""HTML report assembler agent"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from icecream import ic

from prompts import PromptManager

from ..base_agent import BaseAgent

ic.configureOutput(includeContext=True, prefix="HTMLAssemblerAgent- ")


class HTMLAssemblerAgent(BaseAgent):
    """Agent responsible for assembling the final HTML report"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("HTMLAssembler", config)
        load_dotenv()
        api_key = os.getenv("GENAI_API_KEY")
        if not api_key:
            raise ValueError("GENAI_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=api_key)
        
        # Load prompt and config from TOML
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "gemini"
        self.prompt_manager = PromptManager(templates_dir=str(prompt_path))
        
        # Get configuration from TOML file
        prompt_config = self.prompt_manager.get_prompt_config("html_assembler")
        self.model = self.config.get("model", prompt_config.get("model", "gemini-2.0-flash-exp"))
        self.temperature = self.config.get("temperature", prompt_config.get("temperature", 0.2))
        self.use_ai = self.config.get("use_ai", prompt_config.get("use_ai", True))  # Allow disabling AI generation
        
        # Get system prompt
        self.system_prompt = self.prompt_manager.get_prompt("html_assembler")
        ic(f"HTMLAssemblerAgent initialized with model: {self.model}, use_ai: {self.use_ai}")

    def process(
        self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Assemble final HTML report from all components

        Args:
            input_data: Dictionary containing all analysis data
            context: Optional context with operator info

        Returns:
            Complete HTML report string
        """
        self.log("Assembling HTML report with Gemini 2.5 Pro", "info")

        # Extract operator info from context
        operator_name = context.get("operator_name", "[Operator Name]") if context else "[Operator Name]"
        equipment = context.get("equipment", "[Equipment Model/Type]") if context else "[Equipment Model/Type]"
        exercise_date = context.get("exercise_date", datetime.now().strftime("%Y-%m-%d")) if context else datetime.now().strftime("%Y-%m-%d")
        session_duration = context.get("session_duration", "N/A") if context else "N/A"

        # Check if AI generation is enabled
        if not self.use_ai:
            self.log("AI generation disabled, using template-based approach", "info")
            return self._generate_with_template(input_data, operator_name, equipment, exercise_date, session_duration)
        
        # Try AI-powered assembly first
        try:
            ic(f"HTMLAssemblerAgent attempting AI generation with model: {self.model}")
            html = self._generate_with_ai(input_data, operator_name, equipment, exercise_date, session_duration)
            self.log("✓ HTML report assembled with AI", "success")
            return html
        except KeyboardInterrupt:
            self.log("AI generation interrupted by user", "warning")
            raise
        except Exception as e:
            self.log(f"AI assembly failed: {e}, using template-based approach", "warning")
            return self._generate_with_template(input_data, operator_name, equipment, exercise_date, session_duration)

    def _generate_with_ai(
        self, data: Dict[str, Any], operator_name: str, equipment: str, exercise_date: str, session_duration: str
    ) -> str:
        """
        Generate HTML using AI

        Args:
            data: All analysis data
            operator_name: Name of operator
            equipment: Equipment model
            exercise_date: Date of exercise
            session_duration: Duration of session

        Returns:
            HTML string
        """
        cycle_metrics = data.get("cycle_metrics", {})
        joystick_analytics = data.get("joystick_analytics", {})
        performance_scores = data.get("performance_scores", {})
        insights = data.get("insights", {})

        prompt = f"""{self.system_prompt}

**Report Metadata:**
- Operator Name: {operator_name}
- Equipment: {equipment}
- Exercise Date: {exercise_date}
- Session Duration: {session_duration}
- Analysis System: Gemini 2.5 Pro Multi-Agent System

**Performance Data:**
{self._format_data_for_prompt(cycle_metrics, joystick_analytics, performance_scores, insights)}"""

        ic(f"HTMLAssemblerAgent calling Gemini with model: {self.model}")
        self.log(f"Sending request to Gemini API (model: {self.model})...", "info")
        self.log(f"Prompt length: {len(prompt)} characters", "info")
        
        # Warn if prompt is very large
        if len(prompt) > 50000:
            self.log(f"Warning: Prompt is large ({len(prompt)} chars), this may take longer", "warning")
        
        try:
            self.log("Waiting for Gemini API response (this may take 30-60 seconds)...", "info")
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                ),
            )
            
            self.log("Received response from Gemini API", "success")
            ic(f"Response length: {len(response.text)} characters")
            
            return response.text
            
        except Exception as e:
            self.log(f"Gemini API call failed: {str(e)}", "error")
            self.log("Falling back to template-based generation", "warning")
            raise

    def _generate_with_template(
        self, data: Dict[str, Any], operator_name: str, equipment: str, exercise_date: str, session_duration: str
    ) -> str:
        """
        Generate HTML using template-based approach

        Args:
            data: All analysis data
            operator_name: Name of operator
            equipment: Equipment model
            exercise_date: Date of exercise
            session_duration: Duration of session

        Returns:
            HTML string
        """
        cycle_metrics = data.get("cycle_metrics", {})
        joystick_analytics = data.get("joystick_analytics", {})
        chart_analysis = data.get("chart_analysis", {})
        performance_scores = data.get("performance_scores", {})
        insights = data.get("insights", {})

        # Build HTML from template
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Operator Training Report - {operator_name}</title>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        <header class="report-header">
            <h1>OPERATOR TRAINING REPORT</h1>
            <p class="subtitle">Post-Exercise Performance Analysis with Advanced Control Analytics</p>
        </header>

        <section class="metadata">
            <table class="info-table">
                <tr><th>Operator Name:</th><td>{operator_name}</td></tr>
                <tr><th>Equipment:</th><td>{equipment}</td></tr>
                <tr><th>Exercise Date:</th><td>{exercise_date}</td></tr>
                <tr><th>Session Duration:</th><td>{session_duration}</td></tr>
                <tr><th>Analysis System:</th><td>Gemini 2.5 Pro Multi-Agent System</td></tr>
            </table>
        </section>

        {self._build_executive_summary(performance_scores)}
        {self._build_performance_metrics(cycle_metrics)}
        {self._build_control_analytics(joystick_analytics)}
        {self._build_visual_chart_analysis(chart_analysis)}
        {self._build_insights_section(insights)}
        {self._build_footer()}
    </div>
</body>
</html>"""

        return html

    def _build_executive_summary(self, scores: Dict[str, Any]) -> str:
        """Build executive summary section"""
        return f"""
        <section class="executive-summary">
            <h2>1. EXECUTIVE SUMMARY</h2>
            <div class="score-cards">
                <div class="score-card">
                    <h3>PRODUCTIVITY</h3>
                    <div class="score {self._get_score_class(scores.get('productivity_score', 0))}">{scores.get('productivity_score', 0)}/100</div>
                    <div class="status">{scores.get('productivity_status', 'Unknown')}</div>
                </div>
                <div class="score-card">
                    <h3>CONTROL SKILL</h3>
                    <div class="score {self._get_score_class(scores.get('control_skill_score', 0))}">{scores.get('control_skill_score', 0)}/100</div>
                    <div class="status">{scores.get('control_skill_status', 'Unknown')}</div>
                </div>
                <div class="score-card">
                    <h3>SAFETY</h3>
                    <div class="score {self._get_score_class(scores.get('safety_score', 0))}">{scores.get('safety_score', 0)}/100</div>
                    <div class="status">{scores.get('safety_status', 'Unknown')}</div>
                </div>
            </div>
            <p class="summary-text">
                This report provides comprehensive analysis of operator performance including productivity metrics, 
                advanced control coordination analytics, and safety compliance. Key findings and recommendations 
                are highlighted throughout.
            </p>
        </section>"""

    def _build_performance_metrics(self, metrics: Dict[str, Any]) -> str:
        """Build performance metrics section"""
        return f"""
        <section class="performance-metrics">
            <h2>2. PERFORMANCE METRICS</h2>
            <h3>2.1 Cycle Time Analysis</h3>
            <table class="metrics-table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                        <th>Benchmark</th>
                        <th>Performance</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Average Cycle Time</td>
                        <td>{metrics.get('average_cycle_time', 0)}s</td>
                        <td>{metrics.get('target_cycle_time', 20)}s</td>
                        <td class="{self._get_performance_class(metrics.get('average_cycle_time', 0), metrics.get('target_cycle_time', 20))}">{self._get_performance_text(metrics.get('average_cycle_time', 0), metrics.get('target_cycle_time', 20))}</td>
                    </tr>
                    <tr>
                        <td>Cycle Time Variance</td>
                        <td>{metrics.get('variance', 0):.2f}</td>
                        <td>&lt;15%</td>
                        <td>{self._get_variance_status(metrics.get('variance', 0))}</td>
                    </tr>
                    <tr>
                        <td>Consistency Score</td>
                        <td>{metrics.get('consistency_score', 0):.1f}%</td>
                        <td>&gt;70%</td>
                        <td class="{self._get_score_class(metrics.get('consistency_score', 0))}">{self._get_status_from_score(metrics.get('consistency_score', 0))}</td>
                    </tr>
                    <tr>
                        <td>Cycle Time Trend</td>
                        <td colspan="3">{metrics.get('cycle_time_trend', 'Unknown')}</td>
                    </tr>
                </tbody>
            </table>
        </section>"""

    def _build_control_analytics(self, analytics: Dict[str, Any]) -> str:
        """Build control analytics section"""
        # Check if we have a Gemini-generated markdown report
        if analytics.get('markdown_report'):
            return self._build_control_analytics_from_markdown(analytics)
        
        # Otherwise, use legacy structured data approach
        control_usage = analytics.get('control_usage', {})
        si_formatted = analytics.get('si_formatted', {})
        si_table = si_formatted.get('table', [])
        
        # Build SI matrix table
        si_table_html = """
            <table class="metrics-table">
                <thead>
                    <tr>
                        <th>Control Axis</th>
                        <th>Left X (Swing)</th>
                        <th>Right X (Arm)</th>
                        <th>Right Y (Bucket)</th>
                    </tr>
                </thead>
                <tbody>"""
        
        for row in si_table:
            si_table_html += f"""
                    <tr>
                        <td>Left Y ({row.get('control', '')})</td>
                        <td>{row.get('left_x', 0):.3f}</td>
                        <td>{row.get('right_x', 0):.3f}</td>
                        <td>{row.get('right_y', 0):.3f}</td>
                    </tr>"""
        
        si_table_html += """
                </tbody>
            </table>"""

        # Build control usage table
        control_usage_html = f"""
            <table class="metrics-table">
                <thead>
                    <tr>
                        <th>Control Configuration</th>
                        <th>% of Active Time</th>
                        <th>Expert Benchmark</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Single Control (≥1)</td>
                        <td>{control_usage.get('single_control', 100):.1f}%</td>
                        <td>100%</td>
                    </tr>
                    <tr>
                        <td>Dual Control (≥2)</td>
                        <td class="{self._get_score_class(control_usage.get('dual_control', 0))}">{control_usage.get('dual_control', 0):.1f}%</td>
                        <td>&gt;65%</td>
                    </tr>
                    <tr>
                        <td>Triple Control (≥3)</td>
                        <td class="{self._get_score_class(control_usage.get('triple_control', 0))}">{control_usage.get('triple_control', 0):.1f}%</td>
                        <td>&gt;35%</td>
                    </tr>
                    <tr>
                        <td>Full Control (4)</td>
                        <td class="{self._get_score_class(control_usage.get('full_control', 0))}">{control_usage.get('full_control', 0):.1f}%</td>
                        <td>&gt;10%</td>
                    </tr>
                </tbody>
            </table>"""

        # Add images if available
        images_html = ""
        if analytics.get('heatmap_image'):
            images_html += f'<img src="{analytics.get("heatmap_image")}" alt="SI Heatmap" class="chart-image">'
        if analytics.get('control_usage_image'):
            images_html += f'<img src="{analytics.get("control_usage_image")}" alt="Control Usage" class="chart-image">'

        return f"""
        <section class="control-analytics">
            <h2>3. ADVANCED CONTROL ANALYTICS</h2>
            
            <h3>3.1 Joystick Coordination Analysis</h3>
            
            <h4>Bimanual Coordination Score (BCS)</h4>
            <p class="bcs-score">Overall BCS: <strong>{analytics.get('bcs_score', 0):.3f}</strong> 
            (Target: &gt;0.25 - {'Good coordination' if analytics.get('bcs_score', 0) > 0.25 else 'Needs improvement'})</p>
            
            <h4>Simultaneity Index (SI) Matrix</h4>
            <p>The SI Matrix shows how frequently different controls are used together. Higher values indicate better coordination.</p>
            {si_table_html}
            
            <h4>Simultaneous Control Usage Distribution</h4>
            {control_usage_html}
            
            {images_html}
        </section>"""

    def _build_control_analytics_from_markdown(self, analytics: Dict[str, Any]) -> str:
        """Build control analytics section from Gemini-generated markdown report"""
        markdown_report = analytics.get('markdown_report', '')
        
        # Convert markdown to HTML (simple conversion)
        html_content = self._markdown_to_html(markdown_report)
        
        # Add images if available
        images_html = ""
        if analytics.get('heatmap_image'):
            images_html += f'<img src="{analytics.get("heatmap_image")}" alt="SI Heatmap" class="chart-image">'
        if analytics.get('control_usage_image'):
            images_html += f'<img src="{analytics.get("control_usage_image")}" alt="Control Usage" class="chart-image">'
        
        return f"""
        <section class="control-analytics">
            <h2>3. ADVANCED CONTROL ANALYTICS</h2>
            <div class="markdown-content">
                {html_content}
            </div>
            {images_html}
        </section>"""
    
    def _markdown_to_html(self, markdown: str) -> str:
        """Convert markdown to HTML (simple conversion)"""
        html = markdown
        
        # Convert headers
        html = html.replace('# ', '<h3>').replace('\n\n', '</h3>\n\n', 1)
        html = html.replace('## ', '<h4>').replace('\n', '</h4>\n')
        html = html.replace('### ', '<h5>').replace('\n', '</h5>\n')
        
        # Convert horizontal rules
        html = html.replace('\n---\n', '\n<hr>\n')
        
        # Convert tables - detect table blocks
        lines = html.split('\n')
        in_table = False
        result_lines = []
        
        for i, line in enumerate(lines):
            # Detect table start (lines with |)
            if '|' in line and not in_table:
                # Check if next line is separator (---|---|)
                if i + 1 < len(lines) and '---' in lines[i + 1]:
                    in_table = True
                    result_lines.append('<table class="metrics-table">')
                    result_lines.append('<thead><tr>')
                    # Parse header cells
                    cells = [c.strip() for c in line.split('|')[1:-1]]
                    for cell in cells:
                        result_lines.append(f'<th>{cell}</th>')
                    result_lines.append('</tr></thead>')
                    result_lines.append('<tbody>')
                    continue
            elif in_table:
                # Skip separator line
                if '---' in line:
                    continue
                # End of table
                elif '|' not in line:
                    result_lines.append('</tbody></table>')
                    result_lines.append(line)
                    in_table = False
                # Table data row
                else:
                    result_lines.append('<tr>')
                    cells = [c.strip() for c in line.split('|')[1:-1]]
                    for cell in cells:
                        # Check if cell contains ** for bold
                        if '**' in cell:
                            cell = cell.replace('**', '<strong>').replace('**', '</strong>')
                        result_lines.append(f'<td>{cell}</td>')
                    result_lines.append('</tr>')
            else:
                result_lines.append(line)
        
        # Close table if still open
        if in_table:
            result_lines.append('</tbody></table>')
        
        html = '\n'.join(result_lines)
        
        # Convert bold text
        import re
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Convert paragraphs (lines not in other tags)
        lines = html.split('\n')
        result_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('<') and not in_table:
                result_lines.append(f'<p>{line}</p>')
            else:
                result_lines.append(line)
        
        return '\n'.join(result_lines)

    def _build_visual_chart_analysis(self, chart_analysis: Dict[str, Any]) -> str:
        """Build visual chart analysis section with embedded images"""
        if not chart_analysis or not chart_analysis.get('chart_analysis_markdown'):
            return ""  # Skip if no chart analysis available
        
        markdown_html = self._markdown_to_html(chart_analysis.get('chart_analysis_markdown', ''))
        
        # Add embedded images
        images_html = ""
        if chart_analysis.get('heatmap_image_base64'):
            images_html += f'<img src="{chart_analysis.get("heatmap_image_base64")}" alt="SI Heatmap" class="chart-image">'
        if chart_analysis.get('control_usage_image_base64'):
            images_html += f'<img src="{chart_analysis.get("control_usage_image_base64")}" alt="Control Usage Chart" class="chart-image">'
        
        return f"""
        <section class="visual-analysis">
            <h2>4. VISUAL CHART ANALYSIS</h2>
            <div class="markdown-content">
                {markdown_html}
            </div>
            <div class="charts">
                {images_html}
            </div>
        </section>"""

    def _build_insights_section(self, insights: Dict[str, Any]) -> str:
        """Build AI insights section"""
        pattern_recognition = insights.get('pattern_recognition', {})
        recommendations = insights.get('training_recommendations', [])
        
        recommendations_html = "<ul>"
        for rec in recommendations:
            recommendations_html += f"<li>{rec}</li>"
        recommendations_html += "</ul>"
        
        focus_areas = insights.get('next_focus_areas', [])
        focus_html = "<ul>"
        for area in focus_areas:
            focus_html += f"<li>{area}</li>"
        focus_html += "</ul>"

        return f"""
        <section class="insights">
            <h2>5. AI-GENERATED INSIGHTS & RECOMMENDATIONS</h2>
            
            <h3>4.1 Pattern Recognition Analysis</h3>
            <ul>
                <li><strong>Control Pattern:</strong> {pattern_recognition.get('control_patterns', 'N/A')}</li>
                <li><strong>Timing Pattern:</strong> {pattern_recognition.get('timing_patterns', 'N/A')}</li>
                <li><strong>Efficiency Pattern:</strong> {pattern_recognition.get('efficiency_patterns', 'N/A')}</li>
            </ul>
            
            <h3>4.2 Personalized Training Recommendations</h3>
            {recommendations_html}
        </section>
        
        <section class="summary">
            <h2>6. SUMMARY & NEXT STEPS</h2>
            
            <h3>5.1 Overall Assessment</h3>
            <p>{insights.get('overall_assessment', 'Assessment not available')}</p>
            
            <h3>5.2 Certification Readiness</h3>
            <table class="info-table">
                <tr><th>Current Proficiency Level:</th><td>{insights.get('proficiency_level', 'Unknown')}</td></tr>
                <tr><th>Estimated Training Hours Required:</th><td>{insights.get('estimated_training_hours', 'N/A')} hours</td></tr>
            </table>
            
            <h3>5.3 Next Training Session Focus Areas</h3>
            {focus_html}
        </section>"""

    def _build_footer(self) -> str:
        """Build report footer"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""
        <footer class="report-footer">
            <p>Report Generated: {timestamp}</p>
            <p>Analysis System: Gemini 2.5 Pro Multi-Agent Training Analysis System v1.0</p>
            <p>Data Sources: Video analysis, joystick telemetry, performance metrics database</p>
        </footer>"""

    def _get_css(self) -> str:
        """Get CSS styles for the report"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        .report-header {
            text-align: center;
            border-bottom: 4px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .report-header h1 {
            font-size: 2.5em;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 1.2em;
            color: #7f8c8d;
        }
        
        h2 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin: 30px 0 20px 0;
        }
        
        h3 {
            color: #34495e;
            margin: 20px 0 10px 0;
        }
        
        h4 {
            color: #555;
            margin: 15px 0 10px 0;
        }
        
        .metadata {
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        
        .info-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .info-table th {
            text-align: left;
            padding: 8px;
            font-weight: 600;
            width: 30%;
        }
        
        .info-table td {
            padding: 8px;
        }
        
        .score-cards {
            display: flex;
            justify-content: space-around;
            gap: 20px;
            margin: 20px 0;
        }
        
        .score-card {
            flex: 1;
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            background: #f8f9fa;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .score-card h3 {
            margin: 0 0 15px 0;
            color: #555;
            font-size: 1em;
        }
        
        .score {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .score.excellent { color: #27ae60; }
        .score.good { color: #2ecc71; }
        .score.satisfactory { color: #f39c12; }
        .score.needs-improvement { color: #e74c3c; }
        
        .status {
            font-weight: 600;
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
        }
        
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        .metrics-table th,
        .metrics-table td {
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        
        .metrics-table thead {
            background: #34495e;
            color: white;
        }
        
        .metrics-table tbody tr:nth-child(even) {
            background: #f8f9fa;
        }
        
        .excellent { color: #27ae60; font-weight: 600; }
        .good { color: #2ecc71; font-weight: 600; }
        .satisfactory { color: #f39c12; font-weight: 600; }
        .needs-improvement { color: #e74c3c; font-weight: 600; }
        
        .bcs-score {
            background: #e8f4f8;
            padding: 15px;
            border-left: 4px solid #3498db;
            margin: 15px 0;
        }
        
        .chart-image {
            max-width: 100%;
            height: auto;
            margin: 20px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .insights ul {
            margin: 15px 0;
            padding-left: 30px;
        }
        
        .insights li {
            margin: 10px 0;
        }
        
        .summary-text {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
        }
        
        .report-footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        @media print {
            body { background: white; }
            .container { box-shadow: none; padding: 20px; }
            .score-cards { page-break-inside: avoid; }
        }
        
        @media (max-width: 768px) {
            .container { padding: 20px; }
            .score-cards { flex-direction: column; }
        }
        """

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

    def _format_data_for_prompt(
        self, cycle_metrics: Dict, joystick: Dict, scores: Dict, insights: Dict
    ) -> str:
        """Format all data for AI prompt in a concise way"""
        
        # Format cycle metrics concisely
        cm = cycle_metrics
        cycle_summary = f"""
**Cycle Metrics:**
- Total Cycles: {cm.get('total_cycles', 0)}
- Average Cycle Time: {cm.get('average_cycle_time', 0)}s
- Min/Max: {cm.get('min_cycle_time', 0)}s / {cm.get('max_cycle_time', 0)}s
- Consistency Score: {cm.get('consistency_score', 0):.1f}%
- Trend: {cm.get('cycle_time_trend', 'N/A')}
"""

        # Format joystick analytics concisely
        js = joystick
        # Use the Gemini-generated markdown report if available
        if js.get('markdown_report'):
            joystick_summary = f"""
**Joystick Analytics:**
{js.get('markdown_report')}

**Structured Data (for reference):**
- BCS Score: {js.get('bcs_score', 0)}
- Dual Control: {js.get('control_usage', {}).get('dual_control', 0):.1f}%
- Triple Control: {js.get('control_usage', {}).get('triple_control', 0):.1f}%
- Full Control: {js.get('control_usage', {}).get('full_control', 0):.1f}%
"""
        else:
            # Fallback to structured data if no markdown report
            joystick_summary = f"""
**Joystick Analytics:**
- BCS Score: {js.get('bcs_score', 0)}
- Dual Control Usage: {js.get('control_usage', {}).get('dual_control', 0):.1f}%
- Triple Control Usage: {js.get('control_usage', {}).get('triple_control', 0):.1f}%
- Full Control Usage: {js.get('control_usage', {}).get('full_control', 0):.1f}%
"""

        # Format performance scores concisely
        ps = scores
        scores_summary = f"""
**Performance Scores:**
- Productivity: {ps.get('productivity_score', 0)}/100 ({ps.get('productivity_status', 'N/A')})
- Control Skill: {ps.get('control_skill_score', 0)}/100 ({ps.get('control_skill_status', 'N/A')})
- Safety: {ps.get('safety_score', 0)}/100 ({ps.get('safety_status', 'N/A')})
- Overall: {ps.get('overall_score', 0)}/100
"""

        # Format insights concisely
        ins = insights
        recommendations = ins.get('training_recommendations', [])
        rec_text = '\n'.join([f"  {i+1}. {rec}" for i, rec in enumerate(recommendations[:5])])  # Limit to 5
        
        insights_summary = f"""
**AI Insights:**
- Proficiency Level: {ins.get('proficiency_level', 'N/A')}
- Training Hours: {ins.get('estimated_training_hours', 'N/A')}
- Key Recommendations:
{rec_text}
"""

        return cycle_summary + joystick_summary + scores_summary + insights_summary


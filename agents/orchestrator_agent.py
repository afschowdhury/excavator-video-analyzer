"""
Orchestrator Agent - Coordinates multiple agents for comprehensive video analysis
"""

from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent
from agents.cycle_detector_agent import CycleDetectorAgent
from agents.technique_evaluator_agent import TechniqueEvaluatorAgent


class OrchestratorAgent(BaseAgent):
    """Agent that orchestrates multiple specialized agents for comprehensive analysis"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash-exp"
    ):
        """
        Initialize the Orchestrator Agent

        Args:
            api_key (str, optional): Gemini API key
            model (str): Gemini model to use for agents
        """
        super().__init__(api_key=api_key, model=model, name="Orchestrator")
        
        # Initialize specialized agents
        self.cycle_detector = CycleDetectorAgent(api_key=api_key, model=model)
        self.technique_evaluator = TechniqueEvaluatorAgent(api_key=api_key, model=model)

    def process(
        self,
        video_url: str,
        include_cycle_times: bool = True,
        include_technique_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Orchestrate comprehensive video analysis

        Args:
            video_url (str): URL of the video to analyze
            include_cycle_times (bool): Whether to include cycle time detection
            include_technique_analysis (bool): Whether to include technique evaluation

        Returns:
            Dict[str, Any]: Comprehensive analysis results containing:
                - cycles: Cycle detection results (if enabled)
                - technique: Technique evaluation results (if enabled)
                - summary: Overall summary
        """
        self.log("Starting orchestrated analysis...", "info")
        
        results = {
            'video_url': video_url,
            'cycles': None,
            'technique': None,
            'summary': {}
        }

        # Step 1: Detect cycles
        if include_cycle_times:
            self.log("Phase 1: Cycle detection", "info")
            try:
                cycle_results = self.cycle_detector.process(video_url)
                results['cycles'] = cycle_results
                
                # Add cycle metrics to summary
                results['summary']['total_cycles'] = cycle_results.get('cycle_count', 0)
                results['summary']['average_cycle_time'] = self.cycle_detector.get_average_cycle_time()
                
            except Exception as e:
                self.log(f"Cycle detection failed: {e}", "error")
                results['cycles'] = {'error': str(e)}

        # Step 2: Evaluate technique (with cycle context if available)
        if include_technique_analysis:
            self.log("Phase 2: Technique evaluation", "info")
            try:
                # Prepare context from cycle detection
                cycle_context = None
                if results['cycles'] and 'error' not in results['cycles']:
                    cycle_context = {
                        'cycle_count': results['cycles'].get('cycle_count', 0),
                        'average_cycle_time': results['summary'].get('average_cycle_time', 0)
                    }
                
                technique_results = self.technique_evaluator.process(
                    video_url,
                    cycle_context=cycle_context
                )
                results['technique'] = technique_results
                
                # Add technique scores to summary
                if 'overall_score' in technique_results:
                    results['summary']['overall_score'] = technique_results['overall_score'].get('score', 'N/A')
                    results['summary']['performance_grade'] = technique_results['overall_score'].get('grade', 'N/A')
                
            except Exception as e:
                self.log(f"Technique evaluation failed: {e}", "error")
                results['technique'] = {'error': str(e)}

        # Step 3: Compile comprehensive summary
        self.log("Phase 3: Compiling results", "info")
        results['summary']['analysis_complete'] = True
        results['summary']['phases_completed'] = []
        
        if include_cycle_times:
            results['summary']['phases_completed'].append('cycle_detection')
        if include_technique_analysis:
            results['summary']['phases_completed'].append('technique_evaluation')

        self.results = results
        self.log("Orchestrated analysis complete!", "success")
        
        return results

    def get_formatted_report(self) -> str:
        """
        Get a formatted markdown report of the analysis

        Returns:
            str: Formatted markdown report
        """
        if not self.results:
            return "# No analysis results available\n\nPlease run process() first."

        report = "# Excavator Performance Analysis Report\n\n"
        
        # Summary section
        report += "## Summary\n\n"
        summary = self.results.get('summary', {})
        
        if 'total_cycles' in summary:
            report += f"- **Total Cycles Detected**: {summary['total_cycles']}\n"
        if 'average_cycle_time' in summary:
            report += f"- **Average Cycle Time**: {summary['average_cycle_time']:.1f} seconds\n"
        if 'overall_score' in summary:
            report += f"- **Overall Performance Score**: {summary['overall_score']}\n"
        if 'performance_grade' in summary:
            report += f"- **Performance Grade**: {summary['performance_grade']}\n"
        
        report += "\n---\n\n"

        # Cycle details
        cycles_data = self.results.get('cycles')
        if cycles_data and 'error' not in cycles_data:
            report += "## Cycle Time Analysis\n\n"
            
            cycles = cycles_data.get('cycles', [])
            if cycles:
                report += "### Detected Cycles\n\n"
                report += "| Cycle | Start Time | End Time | Duration | Phases |\n"
                report += "|-------|-----------|----------|----------|--------|\n"
                
                for cycle in cycles:
                    cycle_id = cycle.get('id', '?')
                    start = cycle.get('start', '?')
                    end = cycle.get('end', '?')
                    duration = cycle.get('total_duration', '?')
                    phases = cycle.get('phases', {})
                    phase_count = len(phases)
                    
                    report += f"| {cycle_id} | {start} | {end} | {duration} | {phase_count} phases |\n"
                
                report += "\n"
            
            # Include raw cycle analysis if available
            if 'raw_response' in cycles_data:
                report += "\n### Detailed Cycle Analysis\n\n"
                report += cycles_data['raw_response']
                report += "\n\n---\n\n"

        # Technique evaluation
        technique_data = self.results.get('technique')
        if technique_data and 'error' not in technique_data:
            report += "## Technique Evaluation\n\n"
            
            # Category scores
            evaluation = technique_data.get('evaluation', {})
            if evaluation:
                report += "### Performance Categories\n\n"
                for category, data in evaluation.items():
                    score = data.get('score', 'N/A')
                    report += f"- **{category.replace('_', ' ').title()}**: {score}\n"
                report += "\n"
            
            # Recommendations
            recommendations = technique_data.get('recommendations', {})
            if recommendations:
                report += "### Recommendations\n\n"
                
                if recommendations.get('high'):
                    report += "#### High Priority\n\n"
                    for rec in recommendations['high']:
                        report += f"- {rec}\n"
                    report += "\n"
                
                if recommendations.get('medium'):
                    report += "#### Medium Priority\n\n"
                    for rec in recommendations['medium']:
                        report += f"- {rec}\n"
                    report += "\n"
                
                if recommendations.get('low'):
                    report += "#### Low Priority\n\n"
                    for rec in recommendations['low']:
                        report += f"- {rec}\n"
                    report += "\n"
            
            # Overall assessment
            overall = technique_data.get('overall_score', {})
            if overall:
                report += "### Overall Assessment\n\n"
                report += f"**Score**: {overall.get('score', 'N/A')}\n\n"
                report += f"**Grade**: {overall.get('grade', 'N/A')}\n\n"
                if overall.get('summary'):
                    report += f"{overall['summary']}\n\n"
            
            # Include raw technique analysis if available
            if 'raw_response' in technique_data:
                report += "\n### Detailed Technique Analysis\n\n"
                report += technique_data['raw_response']

        return report

    def get_cycle_data(self) -> Dict[str, Any]:
        """
        Get cycle detection data

        Returns:
            Dict[str, Any]: Cycle data
        """
        return self.results.get('cycles', {})

    def get_technique_data(self) -> Dict[str, Any]:
        """
        Get technique evaluation data

        Returns:
            Dict[str, Any]: Technique data
        """
        return self.results.get('technique', {})


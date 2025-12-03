"""
Cycle Time Analyzer - Generates statistical analysis from excavation cycle data
"""

import os
import statistics
from typing import List, Dict, Any

from dotenv import load_dotenv
from google import genai
from google.genai import types
from rich.console import Console
from rich.markdown import Markdown
from icecream import ic


class CycleTimeAnalyzer:
    """Analyzes excavation cycle times and generates statistical reports using Gemini Flash"""

    def __init__(self, api_key=None):
        """
        Initialize the CycleTimeAnalyzer

        Args:
            api_key (str, optional): Gemini API key. If not provided, will try to load from .env file
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("GENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Please provide it or set GENAI_API_KEY in .env file"
            )

        self.client = genai.Client(api_key=self.api_key)
        self.console = Console()

        # Define calculator function tools
        self.calculator_tools = self._define_calculator_tools()

    def _define_calculator_tools(self):
        """Define calculator function tools for Gemini"""
        
        # Define calculator functions
        def add(a: float, b: float) -> float:
            """Add two numbers"""
            return a + b

        def subtract(a: float, b: float) -> float:
            """Subtract b from a"""
            return a - b

        def multiply(a: float, b: float) -> float:
            """Multiply two numbers"""
            return a * b

        def divide(a: float, b: float) -> float:
            """Divide a by b"""
            if b == 0:
                return float('inf')
            return a / b

        def average(numbers: List[float]) -> float:
            """Calculate the average of a list of numbers"""
            if not numbers:
                return 0.0
            return sum(numbers) / len(numbers)

        def std_dev(numbers: List[float]) -> float:
            """Calculate the standard deviation of a list of numbers"""
            if len(numbers) < 2:
                return 0.0
            return statistics.stdev(numbers)

        # Store functions for later invocation
        self.functions = {
            'add': add,
            'subtract': subtract,
            'multiply': multiply,
            'divide': divide,
            'average': average,
            'std_dev': std_dev
        }

        # Define function declarations for Gemini
        tool_declarations = [
            types.FunctionDeclaration(
                name='add',
                description='Add two numbers',
                parameters={
                    'type': 'object',
                    'properties': {
                        'a': {'type': 'number', 'description': 'First number'},
                        'b': {'type': 'number', 'description': 'Second number'}
                    },
                    'required': ['a', 'b']
                }
            ),
            types.FunctionDeclaration(
                name='subtract',
                description='Subtract b from a',
                parameters={
                    'type': 'object',
                    'properties': {
                        'a': {'type': 'number', 'description': 'Number to subtract from'},
                        'b': {'type': 'number', 'description': 'Number to subtract'}
                    },
                    'required': ['a', 'b']
                }
            ),
            types.FunctionDeclaration(
                name='multiply',
                description='Multiply two numbers',
                parameters={
                    'type': 'object',
                    'properties': {
                        'a': {'type': 'number', 'description': 'First number'},
                        'b': {'type': 'number', 'description': 'Second number'}
                    },
                    'required': ['a', 'b']
                }
            ),
            types.FunctionDeclaration(
                name='divide',
                description='Divide a by b',
                parameters={
                    'type': 'object',
                    'properties': {
                        'a': {'type': 'number', 'description': 'Numerator'},
                        'b': {'type': 'number', 'description': 'Denominator'}
                    },
                    'required': ['a', 'b']
                }
            ),
            types.FunctionDeclaration(
                name='average',
                description='Calculate the average of a list of numbers',
                parameters={
                    'type': 'object',
                    'properties': {
                        'numbers': {
                            'type': 'array',
                            'items': {'type': 'number'},
                            'description': 'List of numbers to average'
                        }
                    },
                    'required': ['numbers']
                }
            ),
            types.FunctionDeclaration(
                name='std_dev',
                description='Calculate the standard deviation of a list of numbers',
                parameters={
                    'type': 'object',
                    'properties': {
                        'numbers': {
                            'type': 'array',
                            'items': {'type': 'number'},
                            'description': 'List of numbers'
                        }
                    },
                    'required': ['numbers']
                }
            )
        ]

        return types.Tool(function_declarations=tool_declarations)

    def calculate_statistics(self, cycle_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate basic statistics from cycle data

        Args:
            cycle_data (list): List of cycle dictionaries with duration information

        Returns:
            dict: Dictionary containing statistical measures including:
                - specific_average_duration: Average of individual cycle durations (work time only)
                - approximate_average_duration: Total time span / number of cycles (includes gaps)
                - idle_time_per_cycle: Difference between approximate and specific averages
        """
        if not cycle_data:
            return {
                'total_cycles': 0,
                'durations': [],
                'specific_average_duration': 0,
                'approximate_average_duration': 0,
                'idle_time_per_cycle': 0,
                'min_duration': 0,
                'max_duration': 0,
                'std_deviation': 0
            }

        durations = [cycle['duration'] for cycle in cycle_data]
        
        # Specific average: average of individual cycle durations (work time only)
        specific_avg = statistics.mean(durations)
        
        # Approximate average: total time span from first start to last end divided by cycles
        first_start = cycle_data[0]['start_time_sec']
        last_end = cycle_data[-1]['end_time_sec']
        total_time_span = last_end - first_start
        approximate_avg = total_time_span / len(cycle_data)
        
        # Idle time per cycle: difference between approximate and specific
        idle_time = approximate_avg - specific_avg

        stats = {
            'total_cycles': len(cycle_data),
            'durations': durations,
            'specific_average_duration': specific_avg,
            'approximate_average_duration': approximate_avg,
            'idle_time_per_cycle': idle_time,
            'min_duration': min(durations),
            'max_duration': max(durations),
            'std_deviation': statistics.stdev(durations) if len(durations) > 1 else 0,
            'cycle_data': cycle_data
        }

        return stats

    def generate_analysis_report(
        self,
        statistics: Dict[str, Any],
        use_ai: bool = False
    ) -> str:
        """
        Generate a formatted analysis report from statistics

        Args:
            statistics (dict): Statistical data from calculate_statistics()
            use_ai (bool): Whether to use AI for generating insights (default: False)

        Returns:
            str: Markdown formatted analysis report
        """
        if statistics['total_cycles'] == 0:
            return "## Cycle Time Analysis\n\nNo cycle data available for analysis."

        if use_ai:
            return self._generate_ai_report(statistics)
        else:
            return self._generate_simple_report(statistics)

    def _generate_simple_report(self, statistics: Dict[str, Any]) -> str:
        """Generate a simple statistical report without AI"""
        
        # Format durations nicely
        durations_str = ", ".join([f"{d}s" for d in statistics['durations']])
        
        # Calculate idle percentage
        idle_percentage = (statistics['idle_time_per_cycle'] / statistics['approximate_average_duration'] * 100) if statistics['approximate_average_duration'] > 0 else 0
        
        report = f"""## Cycle Time Analysis

### Summary Statistics

- **Total Cycles**: {statistics['total_cycles']}
- **Approximate Average Cycle Time**: {statistics['approximate_average_duration']:.2f} seconds (includes idle time)
- **Specific Average Cycle Time**: {statistics['specific_average_duration']:.2f} seconds (work time only)
- **Idle Time per Cycle**: {statistics['idle_time_per_cycle']:.2f} seconds ({idle_percentage:.1f}% of total time)
- **Minimum Cycle Time**: {statistics['min_duration']} seconds
- **Maximum Cycle Time**: {statistics['max_duration']} seconds
- **Standard Deviation**: {statistics['std_deviation']:.2f} seconds

### Cycle Duration Details

{durations_str}

### Performance Insights

- **Fastest Cycle**: Cycle completed in {statistics['min_duration']} seconds
- **Slowest Cycle**: Cycle completed in {statistics['max_duration']} seconds
- **Time Variation**: {statistics['std_deviation']:.2f} seconds standard deviation
- **Consistency**: {'High' if statistics['std_deviation'] < statistics['specific_average_duration'] * 0.15 else 'Moderate' if statistics['std_deviation'] < statistics['specific_average_duration'] * 0.30 else 'Low'} (based on coefficient of variation)
- **Efficiency**: {'Excellent' if idle_percentage < 5 else 'Good' if idle_percentage < 15 else 'Fair' if idle_percentage < 30 else 'Needs Improvement'} (based on idle time percentage)
"""
        
        return report

    def _generate_ai_report(self, statistics: Dict[str, Any]) -> str:
        """Generate an AI-enhanced report with Gemini Flash"""
        
        idle_percentage = (statistics['idle_time_per_cycle'] / statistics['approximate_average_duration'] * 100) if statistics['approximate_average_duration'] > 0 else 0
        
        prompt = f"""Analyze the following excavation cycle time statistics and provide a brief performance summary:

Total Cycles: {statistics['total_cycles']}
Approximate Average (with gaps): {statistics['approximate_average_duration']:.2f} seconds
Specific Average (work only): {statistics['specific_average_duration']:.2f} seconds
Idle Time per Cycle: {statistics['idle_time_per_cycle']:.2f} seconds ({idle_percentage:.1f}%)
Min Duration: {statistics['min_duration']} seconds
Max Duration: {statistics['max_duration']} seconds
Standard Deviation: {statistics['std_deviation']:.2f} seconds

Individual cycle durations: {statistics['durations']}

Generate a concise markdown report with:
1. Summary statistics (including both average types)
2. Performance insights (explain the difference between approximate and specific averages)
3. Consistency assessment
4. Efficiency analysis (based on idle time)

Keep the report under 300 words."""

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    tools=[self.calculator_tools],
                    system_instruction="You are an excavation performance analyst. Provide clear, data-driven insights."
                )
            )
            
            return response.text
            
        except Exception as e:
            ic(f"AI report generation failed: {e}")
            # Fall back to simple report
            return self._generate_simple_report(statistics)

    def display_report(self, report_text: str):
        """
        Display the report text as formatted markdown

        Args:
            report_text (str): The report text to display
        """
        if report_text:
            self.console.print(Markdown(report_text))
        else:
            self.console.print("[bold red]No report to display")


def main():
    """Demo the cycle time analyzer"""
    # Sample cycle data
    sample_cycles = [
        {'cycle_num': 1, 'start_time': '00:07', 'end_time': '00:35', 'duration': 28, 'notes': 'Good execution'},
        {'cycle_num': 2, 'start_time': '00:35', 'end_time': '01:00', 'duration': 25, 'notes': 'Faster'},
        {'cycle_num': 3, 'start_time': '01:00', 'end_time': '01:30', 'duration': 30, 'notes': 'Slower'},
        {'cycle_num': 4, 'start_time': '01:30', 'end_time': '01:55', 'duration': 25, 'notes': 'Good'},
        {'cycle_num': 5, 'start_time': '01:55', 'end_time': '02:25', 'duration': 30, 'notes': 'Normal'},
    ]

    analyzer = CycleTimeAnalyzer()
    
    # Calculate statistics
    stats = analyzer.calculate_statistics(sample_cycles)
    
    # Generate and display report
    report = analyzer.generate_analysis_report(stats, use_ai=False)
    analyzer.display_report(report)


if __name__ == "__main__":
    main()


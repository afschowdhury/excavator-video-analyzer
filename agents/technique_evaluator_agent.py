"""
Technique Evaluator Agent - Analyzes operator technique and performance
"""

from typing import Any, Dict

from google.genai import types

from agents.base_agent import BaseAgent
from prompts import POMLParser, PromptManager


class TechniqueEvaluatorAgent(BaseAgent):
    """Agent specialized in evaluating excavator operator technique"""

    def __init__(self, api_key: str = None, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize the Technique Evaluator Agent

        Args:
            api_key (str, optional): Gemini API key
            model (str): Gemini model to use
        """
        super().__init__(api_key=api_key, model=model, name="TechniqueEvaluator")
        self.prompt_manager = PromptManager()
        self.poml_parser = POMLParser()

    def process(
        self,
        video_url: str,
        cycle_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process video to evaluate operator technique

        Args:
            video_url (str): URL of the video to analyze
            cycle_context (Dict[str, Any], optional): Context from cycle detection

        Returns:
            Dict[str, Any]: Dictionary containing:
                - evaluation: Structured evaluation by category
                - recommendations: Improvement recommendations
                - overall_score: Overall performance score
                - raw_response: Raw POML response
        """
        self.log("Starting technique evaluation...", "info")

        # Get POML technique evaluation prompt
        try:
            system_instruction = self.prompt_manager.get_prompt("poml_technique_evaluation")
            prompt_config = self.prompt_manager.get_prompt_config("poml_technique_evaluation")
        except KeyError:
            self.log("POML technique evaluation template not found, using detailed", "warning")
            system_instruction = self.prompt_manager.get_prompt("detailed")
            prompt_config = self.prompt_manager.get_prompt_config("detailed")

        # Build context-aware prompt
        prompt_text = "Analyze this excavator operator's technique throughout the video using POML markup."
        
        if cycle_context:
            cycle_count = cycle_context.get('cycle_count', 0)
            avg_time = cycle_context.get('average_cycle_time', 0)
            prompt_text += f"\n\nContext: The video contains {cycle_count} complete cycles with an average cycle time of {avg_time:.1f} seconds."

        # Prepare content parts
        content_parts = [
            types.Part(file_data=types.FileData(file_uri=video_url)),
            types.Part(text=prompt_text)
        ]

        # Generate analysis
        self.log("Evaluating operator technique...", "info")
        raw_response = self._generate_content(
            content_parts=content_parts,
            system_instruction=system_instruction,
            temperature=prompt_config.get("temperature", 0.3),
            top_p=prompt_config.get("top_p", 0.95),
            max_tokens=prompt_config.get("max_tokens", 4000)
        )

        # Parse POML response
        self.log("Parsing evaluation data from response...", "info")
        evaluation = self.poml_parser.parse_evaluation(raw_response)

        # Extract overall performance score
        overall_score = self._extract_overall_score(raw_response)
        recommendations = self._extract_recommendations(raw_response)

        # Store results
        self.results = {
            'evaluation': evaluation,
            'recommendations': recommendations,
            'overall_score': overall_score,
            'raw_response': raw_response
        }

        self.log(f"Evaluation complete - Score: {overall_score.get('score', 'N/A')}", "success")

        return self.results

    def _extract_overall_score(self, response_text: str) -> Dict[str, Any]:
        """
        Extract overall performance score from response

        Args:
            response_text (str): Response text

        Returns:
            Dict[str, Any]: Overall score data
        """
        import re
        
        score_pattern = r'<overall_performance>.*?<score>([^<]+)</score>.*?<grade>([^<]+)</grade>.*?<summary>([^<]+)</summary>.*?</overall_performance>'
        match = re.search(score_pattern, response_text, re.DOTALL)
        
        if match:
            return {
                'score': match.group(1).strip(),
                'grade': match.group(2).strip(),
                'summary': match.group(3).strip()
            }
        
        return {'score': 'N/A', 'grade': 'N/A', 'summary': ''}

    def _extract_recommendations(self, response_text: str) -> Dict[str, list]:
        """
        Extract recommendations from response

        Args:
            response_text (str): Response text

        Returns:
            Dict[str, list]: Recommendations by priority
        """
        import re
        
        recommendations = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        priority_pattern = r'<priority level="(high|medium|low)">(.*?)</priority>'
        priority_matches = re.finditer(priority_pattern, response_text, re.DOTALL)
        
        for match in priority_matches:
            priority_level = match.group(1)
            content = match.group(2)
            
            rec_pattern = r'<recommendation>([^<]+)</recommendation>'
            rec_matches = re.finditer(rec_pattern, content)
            
            for rec_match in rec_matches:
                recommendations[priority_level].append(rec_match.group(1).strip())
        
        return recommendations

    def get_category_scores(self) -> Dict[str, str]:
        """
        Get scores for each evaluation category

        Returns:
            Dict[str, str]: Category scores
        """
        if 'evaluation' not in self.results:
            return {}

        return {
            category: data.get('score', 'N/A')
            for category, data in self.results['evaluation'].items()
        }


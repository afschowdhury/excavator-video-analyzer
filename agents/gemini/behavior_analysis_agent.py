"""Behavior analysis agent using Gemini Vision and Flash for detection and reporting"""

import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from icecream import ic

from ..base_agent import BaseAgent
from prompts import PromptManager

ic.configureOutput(includeContext=True, prefix="BehaviorAnalysis- ")


class BehaviorAnalysisAgent(BaseAgent):
    """Agent responsible for analyzing operator behavior (smoothness, jerking, panic) using Gemini"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("BehaviorAnalysis", config)
        load_dotenv()
        api_key = os.getenv("GENAI_API_KEY")
        if not api_key:
            raise ValueError("GENAI_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=api_key)
        
        # Load prompt and config from TOML
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "gemini"
        self.prompt_manager = PromptManager(templates_dir=str(prompt_path))
        
        # Get configuration from TOML file
        prompt_config = self.prompt_manager.get_prompt_config("behavior_analysis")
        self.model = self.config.get("model", prompt_config.get("model", "gemini-2.0-flash-exp"))
        self.temperature = self.config.get("temperature", prompt_config.get("temperature", 0.3))
        self.response_mime_type = prompt_config.get("response_mime_type", "application/json")
        
        # Get system prompt
        self.system_prompt = self.prompt_manager.get_prompt("behavior_analysis")
        ic(f"BehaviorAnalysisAgent initialized with model: {self.model}")

    def process(
        self, input_data: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze frames for operator behavior
        
        Args:
            input_data: List of frames with base64-encoded image data
            context: Optional context
            
        Returns:
            Dictionary containing behavior events and summary report
        """
        self.log(f"Analyzing behavior in {len(input_data)} frames", "info")

        # Step 1: Detect behavior in frames
        behavior_events = self._detect_behavior_in_frames(input_data)
        
        # Step 2: Calculate statistics
        statistics = self._calculate_behavior_statistics(behavior_events)
        
        # Step 3: Generate AI-powered summary report
        summary_report = self._generate_summary_report(statistics, behavior_events)
        
        result = {
            "behavior_events": behavior_events,
            "statistics": statistics,
            "summary_report": summary_report,
        }
        
        self.log(f"Completed behavior analysis. Detected {len(behavior_events)} events.", "success")
        return result

    def _detect_behavior_in_frames(
        self, frames: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect behavior in video frames using Gemini Vision
        
        Args:
            frames: List of frame dictionaries with base64 encoded images
            
        Returns:
            List of behavior event dictionaries
        """
        behavior_events = []
        
        # Process frames in batches to reduce API calls
        # Analyze every 3rd frame to balance coverage and cost
        sample_rate = 3
        
        for i in range(0, len(frames), sample_rate):
            frame = frames[i]
            try:
                self.log(f"▸ Analyzing frame {i + 1}/{len(frames)}...", "info")
                analysis = self._analyze_single_frame(frame, i)
                
                behavior_entry = {
                    "timestamp": frame.get("timestamp", 0),
                    "timestamp_str": frame.get("timestamp_str", "00:00"),
                    "frame_index": i,
                    "behavior_type": analysis.get("behavior_type", "neutral"),
                    "description": analysis.get("description", ""),
                    "severity": analysis.get("severity", "low"),
                    "confidence": analysis.get("confidence", 0.0),
                    "specific_observations": analysis.get("specific_observations", []),
                }
                
                behavior_events.append(behavior_entry)
                
                # Log notable events
                if analysis.get("behavior_type") != "neutral":
                    log_level = "warning" if analysis["behavior_type"] in ["jerking", "panic"] else "success"
                    self.log(
                        f"  → Detected {analysis['behavior_type']} ({analysis['severity']}): {analysis['description']}",
                        log_level
                    )

                # Progress updates
                if (i + 1) % 10 == 0:
                    self.log(f"Progress: {i + 1}/{len(frames)} frames analyzed", "info")

            except Exception as e:
                self.log(f"Error analyzing frame {i}: {e}", "error")
                # Add neutral entry for failed frames
                behavior_events.append({
                    "timestamp": frame.get("timestamp", 0),
                    "timestamp_str": frame.get("timestamp_str", "00:00"),
                    "frame_index": i,
                    "behavior_type": "neutral",
                    "description": f"Analysis failed: {str(e)}",
                    "severity": "low",
                    "confidence": 0.0,
                    "specific_observations": [],
                })

        return behavior_events

    def _analyze_single_frame(
        self, frame: Dict[str, Any], frame_index: int
    ) -> Dict[str, Any]:
        """
        Analyze a single frame using Gemini Vision
        
        Args:
            frame: Frame dictionary with base64 encoded image
            frame_index: Index of the frame
            
        Returns:
            Dictionary with behavior analysis
        """
        try:
            # Decode base64 image
            frame_data = frame.get("frame_data", "")
            image_bytes = base64.b64decode(frame_data)
            
            # Build prompt
            user_prompt = f"""Analyze frame {frame_index + 1} at timestamp {frame.get('timestamp_str', '00:00')}.
            
Evaluate the operator's control quality and classify the behavior."""

            ic(f"Analyzing frame {frame_index} with Gemini Vision")
            
            # Call Gemini Vision API
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    self.system_prompt,
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg"
                    ),
                    user_prompt,
                ],
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    response_mime_type=self.response_mime_type,
                    response_schema={
                        "type": "object",
                        "properties": {
                            "behavior_type": {
                                "type": "string",
                                "enum": ["smooth", "jerking", "panic", "neutral"],
                            },
                            "description": {"type": "string"},
                            "severity": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                            },
                            "confidence": {"type": "number"},
                            "specific_observations": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["behavior_type", "description", "severity", "confidence"],
                    },
                ),
            )

            # Parse JSON response
            result = json.loads(response.text)
            return result

        except Exception as e:
            self.log(f"API call failed for frame {frame_index}: {e}", "error")
            return {
                "behavior_type": "neutral",
                "description": f"Analysis failed: {str(e)}",
                "severity": "low",
                "confidence": 0.0,
                "specific_observations": [],
            }

    def _calculate_behavior_statistics(
        self, behavior_events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate statistics from behavior events
        
        Args:
            behavior_events: List of behavior event dictionaries
            
        Returns:
            Dictionary with statistics
        """
        if not behavior_events:
            return {
                "total_frames_analyzed": 0,
                "behavior_counts": {},
                "percentages": {},
                "notable_events": [],
                "severity_counts": {},
            }

        # Count behavior types
        behavior_counts = {
            "smooth": 0,
            "neutral": 0,
            "jerking": 0,
            "panic": 0,
        }
        
        severity_counts = {
            "low": 0,
            "medium": 0,
            "high": 0,
        }
        
        notable_events = []
        
        for event in behavior_events:
            b_type = event.get("behavior_type", "neutral")
            if b_type in behavior_counts:
                behavior_counts[b_type] += 1
            else:
                behavior_counts["neutral"] += 1
            
            severity = event.get("severity", "low")
            if severity in severity_counts:
                severity_counts[severity] += 1
            
            # Collect notable events (non-neutral)
            if b_type in ["jerking", "panic", "smooth"]:
                notable_events.append({
                    "timestamp": event["timestamp_str"],
                    "type": b_type,
                    "severity": severity,
                    "description": event["description"],
                })

        # Calculate percentages
        total = len(behavior_events)
        percentages = {
            k: (v / total * 100) if total > 0 else 0
            for k, v in behavior_counts.items()
        }

        statistics = {
            "total_frames_analyzed": total,
            "behavior_counts": behavior_counts,
            "percentages": percentages,
            "notable_events": notable_events,
            "severity_counts": severity_counts,
            "smooth_percentage": percentages.get("smooth", 0),
            "problem_percentage": percentages.get("jerking", 0) + percentages.get("panic", 0),
        }

        return statistics

    def _generate_summary_report(
        self, statistics: Dict[str, Any], behavior_events: List[Dict[str, Any]]
    ) -> str:
        """
        Generate AI-powered summary report using Gemini
        
        Args:
            statistics: Behavior statistics
            behavior_events: List of behavior events
            
        Returns:
            Markdown formatted summary report
        """
        if statistics["total_frames_analyzed"] == 0:
            return "## Operator Behavior Analysis\n\nNo frames available for behavior analysis."

        try:
            # Build prompt for Gemini
            prompt = f"""Analyze the following operator behavior data from an excavator training session and provide a comprehensive assessment:

**Statistics:**
- Total Frames Analyzed: {statistics['total_frames_analyzed']}
- Smooth Control: {statistics['behavior_counts']['smooth']} frames ({statistics['percentages']['smooth']:.1f}%)
- Jerking/Unstable: {statistics['behavior_counts']['jerking']} frames ({statistics['percentages']['jerking']:.1f}%)
- Panic/Erratic: {statistics['behavior_counts']['panic']} frames ({statistics['percentages']['panic']:.1f}%)
- Neutral: {statistics['behavior_counts']['neutral']} frames ({statistics['percentages']['neutral']:.1f}%)

**Severity Distribution:**
- Low Severity: {statistics['severity_counts'].get('low', 0)} events
- Medium Severity: {statistics['severity_counts'].get('medium', 0)} events
- High Severity: {statistics['severity_counts'].get('high', 0)} events

**Notable Events:** {len(statistics['notable_events'])} significant behavior events detected

Generate a comprehensive markdown report with:
1. **Overall Assessment**: Summary of operator control quality (2-3 sentences)
2. **Control Smoothness Analysis**: Evaluate the smoothness percentage and what it indicates
3. **Problem Areas**: If jerking or panic detected, explain patterns and severity
4. **Strengths**: Highlight positive behaviors and good practices observed
5. **Safety Considerations**: Any safety concerns based on behavior patterns
6. **Recommendations**: 3-5 specific, actionable recommendations for improvement

Keep the report professional, data-driven, and constructive. Focus on helping the operator improve."""

            self.log("Generating AI summary report with Gemini", "info")
            ic(f"Generating summary with Gemini model: {self.model}")
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    system_instruction="You are an expert excavator training instructor providing constructive feedback on operator behavior and control quality."
                ),
            )

            return response.text

        except Exception as e:
            self.log(f"Failed to generate AI summary: {e}", "warning")
            return self._generate_fallback_report(statistics)

    def _generate_fallback_report(self, statistics: Dict[str, Any]) -> str:
        """
        Generate a basic fallback report without AI
        
        Args:
            statistics: Behavior statistics
            
        Returns:
            Markdown formatted basic report
        """
        self.log("Using fallback report generation", "warning")
        
        smooth_pct = statistics["percentages"]["smooth"]
        problem_pct = statistics["problem_percentage"]
        
        report = f"""## Operator Behavior Analysis

### Overall Assessment
The operator's performance was analyzed across {statistics['total_frames_analyzed']} video frames. 

### Control Quality Summary
- **Smooth Control**: {statistics['behavior_counts']['smooth']} frames ({smooth_pct:.1f}%)
- **Jerking/Unstable**: {statistics['behavior_counts']['jerking']} frames ({statistics['percentages']['jerking']:.1f}%)
- **Panic/Erratic**: {statistics['behavior_counts']['panic']} frames ({statistics['percentages']['panic']:.1f}%)
- **Neutral**: {statistics['behavior_counts']['neutral']} frames ({statistics['percentages']['neutral']:.1f}%)

### Performance Assessment
"""

        if smooth_pct > 60:
            report += "The operator demonstrates **good control smoothness** with consistent, fluid movements.\n\n"
        elif smooth_pct > 30:
            report += "The operator shows **moderate control smoothness** with room for improvement.\n\n"
        else:
            report += "The operator needs significant improvement in **control smoothness**.\n\n"

        if problem_pct > 30:
            report += f"**⚠️ Concern**: {problem_pct:.1f}% of analyzed frames showed problematic behaviors (jerking or panic). This indicates significant control issues that should be addressed in training.\n\n"
        elif problem_pct > 10:
            report += f"**Note**: {problem_pct:.1f}% of frames showed some control challenges. Focus on smoothness and coordination.\n\n"

        report += f"""### Notable Events
{len(statistics['notable_events'])} significant behavior events were detected during the session.

### Recommendations
1. **Practice Smooth Control**: Focus on fluid, continuous movements without abrupt changes
2. **Coordination Training**: Work on simultaneous control usage to improve efficiency
3. **Stress Management**: If panic behaviors detected, practice calm decision-making under pressure
4. **Repetitive Drills**: Build muscle memory through consistent practice of basic operations
"""

        return report

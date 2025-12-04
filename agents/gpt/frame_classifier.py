"""Frame classification agent using GPT-5 vision"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

from ..base_agent import BaseAgent
from prompts import PromptManager

from icecream import ic
ic.configureOutput(includeContext=True, prefix="FrameClassifier- ")


class FrameClassifierAgent(BaseAgent):
    """Agent responsible for classifying video frames into excavation states"""

    STATES = ["digging", "swing_to_dump", "dumping", "swing_to_dig", "idle"]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("FrameClassifier", config)
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=api_key)
        
        # Load prompt and config from TOML
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "gpt"
        self.prompt_manager = PromptManager(templates_dir=str(prompt_path))
        
        # Get configuration from TOML file
        prompt_config = self.prompt_manager.get_prompt_config("frame_classifier")
        self.model = self.config.get("model", prompt_config.get("model", "gpt-4o"))
        self.temperature = self.config.get("temperature", prompt_config.get("temperature", 0.2))
        self.max_tokens = prompt_config.get("max_tokens", 200)
        self.response_format_type = prompt_config.get("response_format_type", "json_object")
        
        # Get system prompt
        self.system_prompt = self.prompt_manager.get_prompt("frame_classifier")
        self.previous_states = []

    def process(
        self, input_data: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Classify frames into excavation states

        Args:
            input_data: List of frame dictionaries from FrameExtractorAgent
            context: Optional context

        Returns:
            List of classified frames with state information
        """
        self.log(f"Classifying {len(input_data)} frames", "info")

        classified_frames = []
        for i, frame in enumerate(input_data):
            try:
                self.log(f"▸ Classifying frame {i + 1}/{len(input_data)} at {frame['timestamp_str']}...", "info")
                classification = self._classify_frame(frame, i)
                
                classified_frames.append(
                    {
                        **frame,
                        "state": classification["state"],
                        "confidence": classification["confidence"],
                        "reasoning": classification["reasoning"],
                    }
                )

                # Store state for context in next frame
                self.previous_states.append(classification["state"])

                # Show classification result
                self.log(
                    f"  → State: {classification['state']} (confidence: {classification['confidence']:.2f})",
                    "success"
                )

                # Progress summary every 10 frames
                if (i + 1) % 10 == 0:
                    self.log(f"Progress: {i + 1}/{len(input_data)} frames classified", "info")

            except Exception as e:
                self.log(f"Error classifying frame {i}: {e}", "error")
                # Add a fallback classification
                classified_frames.append(
                    {
                        **frame,
                        "state": "idle",
                        "confidence": 0.0,
                        "reasoning": f"Error during classification: {str(e)}",
                    }
                )

        self.log(f"Successfully classified {len(classified_frames)} frames", "success")
        return classified_frames

    def _classify_frame(
        self, frame: Dict[str, Any], frame_index: int
    ) -> Dict[str, str]:
        """
        Classify a single frame using GPT-5 vision

        Args:
            frame: Frame dictionary with base64 encoded image
            frame_index: Index of the frame in sequence

        Returns:
            Dictionary with state, confidence, and reasoning
        """
        # Build context from previous frames
        context_text = self._build_context(frame_index)

        # Use system prompt from TOML
        user_prompt = f"""Frame {frame_index + 1} at timestamp {frame['timestamp_str']}.
{context_text}

Classify this frame into one of the excavation states."""

        try:
            # Determine which token parameter to use based on model
            # GPT-5 models use max_completion_tokens, GPT-4 models use max_tokens
            token_params = {}
            if self.model.startswith("gpt-5"):
                token_params["max_completion_tokens"] = 200
            else:
                token_params["max_tokens"] = 200

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{frame['frame_data']}"
                                },
                            },
                        ],
                    },
                ],
                temperature=self.temperature,
                response_format={"type": self.response_format_type},
                **token_params
            )
            ic(self.system_prompt)
            ic(user_prompt)
            ic(response)

            # Parse response
            result = eval(response.choices[0].message.content)
            
            # Validate state
            if result["state"] not in self.STATES:
                self.log(
                    f"Invalid state '{result['state']}' returned, defaulting to 'idle'",
                    "warning",
                )
                result["state"] = "idle"

            return result

        except Exception as e:
            self.log(f"API call failed for frame {frame_index}: {e}", "error")
            return {
                "state": "idle",
                "confidence": 0.0,
                "reasoning": f"Classification failed: {str(e)}",
            }

    def _build_context(self, frame_index: int) -> str:
        """
        Build context string from previous frame states

        Args:
            frame_index: Current frame index

        Returns:
            Context string describing recent states
        """
        if not self.previous_states:
            return "This is the first frame."

        # Get last 3 states for context
        recent_states = self.previous_states[-3:]
        context = f"Previous states: {' -> '.join(recent_states)}"
        return context

    def reset_context(self):
        """Reset the context for a new video"""
        self.previous_states = []
        self.reset_state()


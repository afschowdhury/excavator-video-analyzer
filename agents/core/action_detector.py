"""Action detection agent for identifying state transitions"""

from typing import Any, Dict, List, Optional

from ..base_agent import BaseAgent


class ActionDetectorAgent(BaseAgent):
    """Agent responsible for detecting state transitions and key events"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ActionDetector", config)
        self.events = []

    def process(
        self, input_data: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect state transitions and key events from classified frames

        Args:
            input_data: List of classified frames from FrameClassifierAgent
            context: Optional context

        Returns:
            List of detected events with timestamps
        """
        self.log(f"Detecting actions from {len(input_data)} classified frames", "info")

        events = []
        previous_state = None

        self.log("Analyzing state transitions...", "info")
        
        for i, frame in enumerate(input_data):
            current_state = frame["state"]

            # Detect state transitions
            if previous_state and previous_state != current_state:
                event = self._create_transition_event(
                    previous_state, current_state, frame, i
                )
                if event:
                    events.append(event)
                    self.log(
                        f"▸ Event #{len(events)} at {frame['timestamp_str']}: {event['event_type']} ({previous_state} → {current_state})",
                        "success",
                    )

            previous_state = current_state

        self.log(f"✓ Detected {len(events)} significant events", "success")
        self.update_state("total_events", len(events))
        return events

    def _create_transition_event(
        self,
        from_state: str,
        to_state: str,
        frame: Dict[str, Any],
        frame_index: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Create an event for a state transition

        Args:
            from_state: Previous state
            to_state: Current state
            frame: Frame data
            frame_index: Frame index

        Returns:
            Event dictionary or None if not a significant transition
        """
        # Define significant transitions
        transitions = {
            ("idle", "digging"): "dig_start",
            ("digging", "swing_to_dump"): "dig_end",
            ("swing_to_dump", "dumping"): "dump_start",
            ("dumping", "swing_to_dig"): "dump_end",
            ("swing_to_dig", "digging"): "return_to_dig",
            ("swing_to_dig", "idle"): "cycle_pause",
        }

        event_type = transitions.get((from_state, to_state))

        if event_type:
            return {
                "event_type": event_type,
                "from_state": from_state,
                "to_state": to_state,
                "timestamp": frame["timestamp"],
                "timestamp_str": frame["timestamp_str"],
                "frame_number": frame["frame_number"],
                "frame_index": frame_index,
                "confidence": frame.get("confidence", 0.0),
            }

        return None

    def get_event_sequence(self, events: List[Dict[str, Any]]) -> List[str]:
        """
        Get a sequence of event types

        Args:
            events: List of event dictionaries

        Returns:
            List of event type strings
        """
        return [event["event_type"] for event in events]


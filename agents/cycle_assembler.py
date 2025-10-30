"""Cycle assembly agent for identifying complete excavation cycles"""

from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent


class CycleAssemblerAgent(BaseAgent):
    """Agent responsible for assembling complete excavation cycles from events"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("CycleAssembler", config)

    def process(
        self, input_data: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Assemble complete excavation cycles from detected events

        Args:
            input_data: List of events from ActionDetectorAgent
            context: Optional context containing classified frames

        Returns:
            List of complete cycles with metadata
        """
        self.log(f"Assembling cycles from {len(input_data)} events", "info")
        self.log("Looking for complete excavation cycles...", "info")

        cycles = []
        current_cycle = None

        for event in input_data:
            event_type = event["event_type"]

            # Start a new cycle on dig_start
            if event_type == "dig_start":
                if current_cycle:
                    # Previous cycle was incomplete, try to save it
                    if self._is_valid_partial_cycle(current_cycle):
                        cycles.append(self._finalize_cycle(current_cycle, len(cycles)))
                        self.log(
                            f"Saved partial cycle {len(cycles)}", "warning"
                        )

                # Start new cycle
                current_cycle = {
                    "start_event": event,
                    "events": [event],
                    "start_time": event["timestamp"],
                    "start_time_str": event["timestamp_str"],
                }

            elif current_cycle:
                # Add event to current cycle
                current_cycle["events"].append(event)

                # Check if cycle is complete
                if event_type in ["return_to_dig", "cycle_pause"]:
                    # Cycle is complete
                    current_cycle["end_event"] = event
                    current_cycle["end_time"] = event["timestamp"]
                    current_cycle["end_time_str"] = event["timestamp_str"]

                    # Validate and save cycle
                    if self._is_valid_cycle(current_cycle):
                        cycle_duration = current_cycle["end_time"] - current_cycle["start_time"]
                        cycles.append(self._finalize_cycle(current_cycle, len(cycles)))
                        self.log(
                            f"▸ Cycle #{len(cycles)}: {current_cycle['start_time_str']} → {current_cycle['end_time_str']} (duration: {cycle_duration:.1f}s)",
                            "success",
                        )
                    else:
                        self.log(
                            f"⚠ Incomplete cycle at {current_cycle['start_time_str']}, skipping",
                            "warning",
                        )

                    current_cycle = None

        # Handle incomplete cycle at end of video
        if current_cycle and self._is_valid_partial_cycle(current_cycle):
            cycles.append(self._finalize_cycle(current_cycle, len(cycles)))
            self.log(f"Saved final partial cycle {len(cycles)}", "warning")

        self.log(f"✓ Successfully assembled {len(cycles)} complete cycles", "success")
        self.update_state("total_cycles", len(cycles))
        return cycles

    def _is_valid_cycle(self, cycle: Dict[str, Any]) -> bool:
        """
        Validate if a cycle has all required phases

        Args:
            cycle: Cycle dictionary

        Returns:
            True if cycle is valid
        """
        event_types = [e["event_type"] for e in cycle["events"]]

        # A complete cycle should have: dig_start -> dig_end -> dump_start -> dump_end -> return_to_dig
        required_events = ["dig_start", "dig_end", "dump_start", "dump_end"]

        # Check if all required events are present
        has_required = all(event in event_types for event in required_events)

        # Check minimum duration (at least 5 seconds)
        duration = cycle.get("end_time", cycle["start_time"]) - cycle["start_time"]
        has_min_duration = duration >= 5.0

        return has_required and has_min_duration

    def _is_valid_partial_cycle(self, cycle: Dict[str, Any]) -> bool:
        """
        Validate if a partial cycle is worth keeping

        Args:
            cycle: Cycle dictionary

        Returns:
            True if partial cycle is valid
        """
        event_types = [e["event_type"] for e in cycle["events"]]

        # At least have dig_start and dig_end
        min_events = ["dig_start", "dig_end"]
        has_min_events = all(event in event_types for event in min_events)

        # Check minimum duration (at least 3 seconds)
        current_time = cycle["events"][-1]["timestamp"]
        duration = current_time - cycle["start_time"]
        has_min_duration = duration >= 3.0

        return has_min_events and has_min_duration

    def _finalize_cycle(
        self, cycle: Dict[str, Any], cycle_number: int
    ) -> Dict[str, Any]:
        """
        Finalize cycle with computed metadata

        Args:
            cycle: Cycle dictionary
            cycle_number: Cycle number (0-indexed)

        Returns:
            Finalized cycle dictionary
        """
        # Calculate duration
        end_time = cycle.get("end_time", cycle["events"][-1]["timestamp"])
        duration = end_time - cycle["start_time"]

        # Get end time string
        end_time_str = cycle.get("end_time_str", cycle["events"][-1]["timestamp_str"])

        # Create phase breakdown
        phases = self._extract_phases(cycle["events"])

        # Determine if complete or partial
        is_complete = "end_event" in cycle

        # Generate observations
        observations = self._generate_observations(cycle, phases, is_complete)

        return {
            "cycle_number": cycle_number + 1,
            "start_time": cycle["start_time"],
            "start_time_str": cycle["start_time_str"],
            "end_time": end_time,
            "end_time_str": end_time_str,
            "duration": duration,
            "duration_str": f"{duration:.1f}s",
            "is_complete": is_complete,
            "events": cycle["events"],
            "phases": phases,
            "observations": observations,
        }

    def _extract_phases(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract phase durations from events

        Args:
            events: List of events in cycle

        Returns:
            Dictionary of phase durations
        """
        phases = {}
        phase_starts = {}

        for event in events:
            event_type = event["event_type"]

            # Map events to phases
            if event_type == "dig_start":
                phase_starts["digging"] = event["timestamp"]
            elif event_type == "dig_end":
                if "digging" in phase_starts:
                    phases["digging"] = event["timestamp"] - phase_starts["digging"]
                phase_starts["swing_to_dump"] = event["timestamp"]
            elif event_type == "dump_start":
                if "swing_to_dump" in phase_starts:
                    phases["swing_to_dump"] = (
                        event["timestamp"] - phase_starts["swing_to_dump"]
                    )
                phase_starts["dumping"] = event["timestamp"]
            elif event_type == "dump_end":
                if "dumping" in phase_starts:
                    phases["dumping"] = event["timestamp"] - phase_starts["dumping"]
                phase_starts["swing_to_dig"] = event["timestamp"]
            elif event_type in ["return_to_dig", "cycle_pause"]:
                if "swing_to_dig" in phase_starts:
                    phases["swing_to_dig"] = (
                        event["timestamp"] - phase_starts["swing_to_dig"]
                    )

        return phases

    def _generate_observations(
        self, cycle: Dict[str, Any], phases: Dict[str, Any], is_complete: bool
    ) -> str:
        """
        Generate observations about the cycle

        Args:
            cycle: Cycle dictionary
            phases: Phase durations
            is_complete: Whether cycle is complete

        Returns:
            Observation string
        """
        observations = []

        if not is_complete:
            observations.append("Incomplete cycle")

        # Comment on phase durations
        if "digging" in phases:
            if phases["digging"] < 3:
                observations.append("Quick dig")
            elif phases["digging"] > 8:
                observations.append("Extended dig")

        if len(phases) < 4:
            observations.append("Missing phases")

        if not observations:
            observations.append("Normal cycle")

        return ", ".join(observations)


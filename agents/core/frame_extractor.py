"""Frame extraction agent using OpenCV"""

import base64
import cv2
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image
import io

from ..base_agent import BaseAgent


class FrameExtractorAgent(BaseAgent):
    """Agent responsible for extracting frames from video files"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("FrameExtractor", config)
        self.fps = self.config.get("fps", 3)
        self.max_frames = self.config.get("max_frames", None)  # None means no limit

    def process(
        self, input_data: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract frames from video file

        Args:
            input_data: Path to video file
            context: Optional context (unused)

        Returns:
            List of frame dictionaries with metadata
        """
        video_path = Path(input_data)
        if not video_path.exists():
            self.log(f"Video file not found: {video_path}", "error")
            raise FileNotFoundError(f"Video file not found: {video_path}")

        max_frames_msg = f" (max {self.max_frames} frames)" if self.max_frames else ""
        self.log(f"Extracting frames from {video_path.name} at {self.fps} FPS{max_frames_msg}", "info")

        frames = []
        cap = cv2.VideoCapture(str(video_path))

        try:
            # Get video properties
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / original_fps if original_fps > 0 else 0

            self.log(
                f"Video: {duration:.2f}s, {original_fps:.2f} FPS, {total_frames} total frames",
                "info",
            )

            # Calculate frame interval
            frame_interval = int(original_fps / self.fps) if original_fps > 0 else 1
            frame_count = 0
            extracted_count = 0

            # Calculate estimated frames to extract
            estimated_frames = int((total_frames / frame_interval))
            if self.max_frames:
                estimated_frames = min(estimated_frames, self.max_frames)
            self.log(f"Estimated frames to extract: ~{estimated_frames}", "info")

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Check if we've reached max_frames limit
                if self.max_frames and extracted_count >= self.max_frames:
                    self.log(f"Reached max frames limit ({self.max_frames}), stopping extraction", "info")
                    break

                # Extract frame at specified interval
                if frame_count % frame_interval == 0:
                    # Convert frame to base64
                    frame_data = self._frame_to_base64(frame)

                    # Calculate timestamp
                    timestamp = frame_count / original_fps if original_fps > 0 else 0
                    timestamp_str = self._format_timestamp(timestamp)

                    frames.append(
                        {
                            "frame_number": frame_count,
                            "extracted_index": extracted_count,
                            "timestamp": timestamp,
                            "timestamp_str": timestamp_str,
                            "frame_data": frame_data,
                        }
                    )
                    extracted_count += 1

                    # Show progress every 20 frames
                    if extracted_count % 20 == 0:
                        self.log(f"Progress: Extracted {extracted_count} frames...", "info")

                frame_count += 1

            self.log(f"✓ Successfully extracted {extracted_count} frames", "success")
            self.update_state("total_frames", extracted_count)
            self.update_state("video_duration", duration)

        finally:
            cap.release()

        return frames

    def _frame_to_base64(self, frame) -> str:
        """
        Convert OpenCV frame to base64 encoded string

        Args:
            frame: OpenCV frame (numpy array)

        Returns:
            Base64 encoded image string
        """
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert to PIL Image
        pil_image = Image.fromarray(frame_rgb)

        # Resize if too large (max 2048px on longest side for GPT-5)
        max_size = 2048
        if max(pil_image.size) > max_size:
            ratio = max_size / max(pil_image.size)
            new_size = tuple(int(dim * ratio) for dim in pil_image.size)
            pil_image = pil_image.resize(new_size, Image.LANCZOS)

        # Convert to base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=85)
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        return img_base64

    def _format_timestamp(self, seconds: float) -> str:
        """
        Format timestamp in MM:SS format

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def set_fps(self, fps: int):
        """
        Set the frame extraction rate

        Args:
            fps: Frames per second to extract
        """
        self.fps = fps
        self.config["fps"] = fps
        self.log(f"Frame rate set to {fps} FPS", "info")

    def set_max_frames(self, max_frames: Optional[int]):
        """
        Set the maximum number of frames to extract

        Args:
            max_frames: Maximum frames to extract (None for no limit)
        """
        self.max_frames = max_frames
        self.config["max_frames"] = max_frames
        if max_frames:
            self.log(f"Max frames set to {max_frames}", "info")
        else:
            self.log("Max frames limit removed", "info")


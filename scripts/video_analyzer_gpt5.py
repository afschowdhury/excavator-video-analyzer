
from agents.core.orchestrator import AgentOrchestrator

class VideoAnalyzerGPT5:
    def __init__(self, fps=None, model=None):
        self.fps = fps
        self.model = model
        self.orchestrator = AgentOrchestrator()
    
    def analyze_video(self, video_path, fps=None, max_frames=None):
        """
        Analyze video using the orchestrator pipeline.
        
        Args:
            video_path (str): Path to the video file.
            fps (int, optional): Frames per second to extract.
            max_frames (int, optional): Maximum number of frames to extract.
            
        Returns:
            dict: Analysis results.
        """
        if fps:
            self.orchestrator.set_fps(fps)
        if max_frames:
            self.orchestrator.set_max_frames(max_frames)
            
        return self.orchestrator.run_pipeline(video_path)


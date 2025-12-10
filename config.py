"""Configuration for the Video Analyzer Web Application"""

import json
import os
import re
from pathlib import Path


def extract_youtube_video_id(url):
    """
    Extract YouTube video ID from various URL formats
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: Video ID or None if not found
    """
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def load_preset_videos_from_json():
    """
    Load preset videos from selected_trials.json
    
    Returns:
        list: List of video dictionaries with url, title, thumbnail, video_id, and trial_id
    """
    json_path = Path(__file__).parent / "data" / "joystick_data" / "selected_trials.json"
    
    if not json_path.exists():
        print(f"Warning: {json_path} not found. Using empty preset videos list.")
        return []
    
    try:
        with open(json_path, 'r') as f:
            trials_data = json.load(f)
        
        preset_videos = []
        for trial in trials_data:
            trial_id = trial.get("ID")
            url = trial.get("URL")
            
            if not trial_id or not url:
                continue
            
            # Extract YouTube video ID from URL
            video_id = extract_youtube_video_id(url)
            
            if not video_id:
                print(f"Warning: Could not extract video ID from URL: {url}")
                continue
            
            # Generate thumbnail URL
            thumbnail = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
            
            preset_videos.append({
                "trial_id": trial_id,
                "url": url,
                "title": f"Trial {trial_id}",
                "thumbnail": thumbnail,
                "video_id": video_id
            })
        
        return preset_videos
    
    except Exception as e:
        print(f"Error loading selected_trials.json: {e}")
        return []


# Preset video URLs with metadata (loaded from selected_trials.json)
PRESET_VIDEOS = load_preset_videos_from_json()


def get_trial_id_from_url(url):
    """
    Get trial ID from YouTube URL by matching against selected_trials.json
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: Trial ID or None if not found
    """
    video_id = extract_youtube_video_id(url)
    if not video_id:
        return None
    
    for video in PRESET_VIDEOS:
        if video["video_id"] == video_id:
            return video["trial_id"]
    
    return None


def get_trial_data_by_id(trial_id):
    """
    Get full trial data from selected_trials.json by trial ID
    
    Args:
        trial_id (str): Trial ID (e.g., "2", "B8", "A9")
        
    Returns:
        dict: Trial data including SI, BCS, control_usage, and URL, or None if not found
    """
    json_path = Path(__file__).parent / "data" / "joystick_data" / "selected_trials.json"
    
    if not json_path.exists():
        return None
    
    try:
        with open(json_path, 'r') as f:
            trials_data = json.load(f)
        
        for trial in trials_data:
            if trial.get("ID") == trial_id:
                return trial
        
        return None
    
    except Exception as e:
        print(f"Error loading trial data: {e}")
        return None


# Application settings
APP_CONFIG = {
    "debug": True,
    "host": "0.0.0.0",
    "port": 8005,
}

# GPT-5 Analyzer Configuration
# Note: GPT-5 models use 'max_completion_tokens' parameter
# GPT-4 models use 'max_tokens' parameter
# The code automatically detects and uses the correct parameter
GPT5_CONFIG = {
    "models": [
        {"id": "gpt-4o", "name": "GPT-4o", "description": "Best quality for analysis"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "Faster, cost-efficient"},
        {"id": "gpt-5", "name": "GPT-5", "description": "Latest model (if available)"},
        {"id": "gpt-5-mini", "name": "GPT-5 Mini", "description": "Efficient GPT-5 variant"},
        {"id": "gpt-5-nano", "name": "GPT-5 Nano", "description": "Fastest, most cost-efficient"},
    ],
    "default_model": "gpt-5-nano",
    "fps_options": [1, 3, 5, 10],
    "default_fps": 3,
    "max_frames_options": [
        {"value": None, "label": "All frames (no limit)"},
        {"value": 10, "label": "10 frames (quick test)"},
        {"value": 30, "label": "30 frames (~10s)"},
        {"value": 50, "label": "50 frames (~15-20s)"},
        {"value": 100, "label": "100 frames (~30s)"},
        {"value": 200, "label": "200 frames (~1 min)"},
    ],
    "default_max_frames": None,
}

# Local video files
LOCAL_VIDEOS = [
    {
        "path": "videos/B2.mp4",
        "title": "Local Excavator Video",
        "type": "local"
    }
]

# Analyzer types
ANALYZER_TYPES = [
    {"id": "gemini", "name": "Gemini (Native Video)", "description": "Google Gemini with native video support"},
    {"id": "gpt5", "name": "GPT-5 (Multi-Agent)", "description": "OpenAI GPT-5 with frame-by-frame analysis"},
]

# Video Metadata Configuration
# Used by VideoAnalyzer (Gemini) for video processing parameters
VIDEO_METADATA_CONFIG = {
    "fps": 1,  # Frame sampling rate (frames per second to extract)
    "start_offset": "0s",  # Video start time offset
    "end_offset": "120s",  # Video end time offset (2 minutes)
}


"""Configuration for the Video Analyzer Web Application"""

# Preset video URLs with metadata
PRESET_VIDEOS = [
    {
        "url": "https://youtu.be/QdWnkH3TGDU",
        "title": "Excavator Demo",
        "thumbnail": "https://img.youtube.com/vi/QdWnkH3TGDU/mqdefault.jpg",
        "video_id": "QdWnkH3TGDU"
    },
    # Add more preset videos here as needed
]

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


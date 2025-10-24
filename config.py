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


import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

# Import config directly
try:
    import config
    print("Successfully imported config")
    
    print(f"PRESET_VIDEOS count: {len(config.PRESET_VIDEOS)}")
    
    for i, video in enumerate(config.PRESET_VIDEOS):
        print(f"Video {i+1}: ID={video.get('video_id')}, TrialID={video.get('trial_id')}")
        
    # Test lookup
    test_url = "https://youtu.be/xHUW79Q_0ok"
    trial_id = config.get_trial_id_from_url(test_url)
    print(f"Lookup for {test_url}: {trial_id}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

"""Flask application for Video Analyzer Web UI"""

import os
import re
import argparse
from flask import Flask, render_template, jsonify, request
from video_analyzer import VideoAnalyzer
from config import PRESET_VIDEOS, APP_CONFIG

app = Flask(__name__)

# Initialize VideoAnalyzer
try:
    analyzer = VideoAnalyzer()
except Exception as e:
    print(f"Warning: Could not initialize VideoAnalyzer: {e}")
    analyzer = None


def extract_video_id(url):
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


@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html', preset_videos=PRESET_VIDEOS)


@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    """Get available prompt templates"""
    try:
        if analyzer is None:
            return jsonify({'error': 'VideoAnalyzer not initialized'}), 500
            
        prompts = analyzer.list_available_prompts()
        
        # Format prompts for frontend
        prompt_list = [
            {
                'id': prompt_id,
                'name': prompt_id.replace('_', ' ').title(),
                'description': description
            }
            for prompt_id, description in prompts.items()
        ]
        
        return jsonify({'prompts': prompt_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    """Analyze video with selected prompt"""
    try:
        if analyzer is None:
            return jsonify({'error': 'VideoAnalyzer not initialized. Please check your API key.'}), 500
            
        data = request.get_json()
        video_url = data.get('video_url')
        prompt_type = data.get('prompt_type')
        
        if not video_url:
            return jsonify({'error': 'Video URL is required'}), 400
        
        if not prompt_type:
            return jsonify({'error': 'Prompt type is required'}), 400
        
        # Validate video URL
        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        # Generate report (without saving to file)
        report = analyzer.generate_report(
            video_url=video_url,
            prompt_type=prompt_type,
            save_to_file=False
        )
        
        if report is None:
            return jsonify({'error': 'Failed to generate report'}), 500
        
        return jsonify({
            'success': True,
            'report': report,
            'video_id': video_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/presets', methods=['GET'])
def get_presets():
    """Get preset video configurations"""
    return jsonify({'presets': PRESET_VIDEOS})


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Excavator Video Analyzer Web Application')
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=APP_CONFIG['port'],
        help=f'Port to run the server on (default: {APP_CONFIG["port"]})'
    )
    parser.add_argument(
        '--host',
        type=str,
        default=APP_CONFIG['host'],
        help=f'Host to bind the server to (default: {APP_CONFIG["host"]})'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        default=APP_CONFIG['debug'],
        help='Run in debug mode'
    )
    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Disable debug mode'
    )
    
    args = parser.parse_args()
    
    # Determine debug mode
    debug_mode = args.debug
    if args.no_debug:
        debug_mode = False
    
    print(f"🚀 Starting Excavator Video Analyzer on http://{args.host}:{args.port}")
    print(f"📝 Debug mode: {'enabled' if debug_mode else 'disabled'}")
    
    app.run(
        debug=debug_mode,
        host=args.host,
        port=args.port
    )


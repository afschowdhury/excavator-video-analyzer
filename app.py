"""Flask application for Video Analyzer Web UI"""

import os
import re
import argparse
from flask import Flask, render_template, jsonify, request
from video_analyzer import VideoAnalyzer
from video_analyzer_gpt5 import VideoAnalyzerGPT5
from config import PRESET_VIDEOS, APP_CONFIG, GPT5_CONFIG, LOCAL_VIDEOS, ANALYZER_TYPES

app = Flask(__name__)

# Initialize VideoAnalyzer (Gemini)
try:
    analyzer_gemini = VideoAnalyzer()
except Exception as e:
    print(f"Warning: Could not initialize Gemini VideoAnalyzer: {e}")
    analyzer_gemini = None

# Initialize GPT-5 VideoAnalyzer
try:
    analyzer_gpt5 = VideoAnalyzerGPT5(fps=GPT5_CONFIG["default_fps"], model=GPT5_CONFIG["default_model"])
except Exception as e:
    print(f"Warning: Could not initialize GPT-5 VideoAnalyzer: {e}")
    analyzer_gpt5 = None

# Keep backward compatibility
analyzer = analyzer_gemini


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
    return render_template(
        'index.html',
        preset_videos=PRESET_VIDEOS,
        local_videos=LOCAL_VIDEOS,
        analyzer_types=ANALYZER_TYPES,
        gpt5_config=GPT5_CONFIG
    )


@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    """Get available prompt templates"""
    try:
        analyzer_type = request.args.get('analyzer_type', 'gemini')
        
        if analyzer_type == 'gpt5':
            # GPT-5 uses different prompts
            return jsonify({'prompts': [], 'message': 'GPT-5 uses multi-agent system with predefined prompts'})
        
        if analyzer_gemini is None:
            return jsonify({'error': 'Gemini VideoAnalyzer not initialized'}), 500
            
        prompts = analyzer_gemini.list_available_prompts()
        
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
    """Analyze video with selected analyzer and configuration"""
    try:
        data = request.get_json()
        analyzer_type = data.get('analyzer_type', 'gemini')
        video_url = data.get('video_url')
        video_path = data.get('video_path')  # For local videos
        prompt_type = data.get('prompt_type')
        fps = data.get('fps', GPT5_CONFIG['default_fps'])  # For GPT-5
        gpt5_model = data.get('gpt5_model', GPT5_CONFIG['default_model'])  # For GPT-5
        max_frames = data.get('max_frames', GPT5_CONFIG['default_max_frames'])  # For GPT-5
        
        # Determine which analyzer to use
        if analyzer_type == 'gpt5':
            if analyzer_gpt5 is None:
                return jsonify({'error': 'GPT-5 VideoAnalyzer not initialized. Please check your OpenAI API key.'}), 500
            
            # GPT-5 requires local video file
            if not video_path:
                return jsonify({'error': 'Local video path is required for GPT-5 analysis'}), 400
            
            # Update model if different from default
            if gpt5_model != analyzer_gpt5.model:
                analyzer_gpt5.model = gpt5_model
                analyzer_gpt5.orchestrator.frame_classifier.model = gpt5_model
                analyzer_gpt5.orchestrator.report_generator.model = gpt5_model
            
            # Generate report using GPT-5
            max_frames_int = None if max_frames is None or max_frames == "null" else int(max_frames)
            report = analyzer_gpt5.generate_report(
                video_path=video_path,
                fps=int(fps),
                max_frames=max_frames_int,
                save_to_file=False
            )
            
            if report is None:
                return jsonify({'error': 'Failed to generate report'}), 500
            
            # Get pipeline data for additional info
            pipeline_data = analyzer_gpt5.get_pipeline_data()
            
            return jsonify({
                'success': True,
                'report': report,
                'analyzer_type': 'gpt5',
                'metadata': {
                    'frames_analyzed': len(pipeline_data.get('frames', [])),
                    'events_detected': len(pipeline_data.get('events', [])),
                    'cycles_found': len(pipeline_data.get('cycles', [])),
                    'fps': fps,
                    'model': gpt5_model,
                    'max_frames': max_frames_int if max_frames_int else 'No limit'
                }
            })
        
        else:  # Gemini analyzer
            if analyzer_gemini is None:
                return jsonify({'error': 'Gemini VideoAnalyzer not initialized. Please check your API key.'}), 500
                
            if not video_url:
                return jsonify({'error': 'Video URL is required'}), 400
            
            if not prompt_type:
                return jsonify({'error': 'Prompt type is required'}), 400
            
            # Validate video URL
            video_id = extract_video_id(video_url)
            if not video_id:
                return jsonify({'error': 'Invalid YouTube URL'}), 400
            
            # Generate report (without saving to file)
            report = analyzer_gemini.generate_report(
                video_url=video_url,
                prompt_type=prompt_type,
                save_to_file=False
            )
            
            if report is None:
                return jsonify({'error': 'Failed to generate report'}), 500
            
            return jsonify({
                'success': True,
                'report': report,
                'video_id': video_id,
                'analyzer_type': 'gemini'
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


"""Flask application for Video Analyzer Web UI"""

import argparse
import os
import re

from flask import Flask, jsonify, make_response, render_template, request

from config import ANALYZER_TYPES, APP_CONFIG, GPT5_CONFIG, LOCAL_VIDEOS, PRESET_VIDEOS
from cycle_time_analyzer import CycleTimeAnalyzer
from html_report_analyzer import HTMLReportAnalyzer
from video_analyzer import VideoAnalyzer
from video_analyzer_gpt5 import VideoAnalyzerGPT5

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

# Initialize CycleTimeAnalyzer
try:
    cycle_analyzer = CycleTimeAnalyzer()
except Exception as e:
    print(f"Warning: Could not initialize CycleTimeAnalyzer: {e}")
    cycle_analyzer = None

# Initialize HTMLReportAnalyzer
try:
    html_report_analyzer = HTMLReportAnalyzer()
except Exception as e:
    print(f"Warning: Could not initialize HTMLReportAnalyzer: {e}")
    html_report_analyzer = None

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
        generate_html_report_flag = data.get('generate_html_report', False)  # For HTML report generation
        joystick_data_path = data.get('joystick_data_path', 'data/joystick_data')  # For HTML report
        
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
            
            # Get cycle mode (default to 'simple')
            cycle_mode = data.get('cycle_mode', 'simple')
            
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
            
            # Try to generate cycle time analysis if this is a cycle time prompt
            cycle_analysis = None
            if 'cycle' in prompt_type.lower() and cycle_analyzer is not None:
                try:
                    # Parse cycle data from report
                    cycle_data = VideoAnalyzer.parse_cycle_data(report)
                    
                    if cycle_data:
                        # Calculate statistics
                        statistics = cycle_analyzer.calculate_statistics(cycle_data)
                        
                        # Determine if AI mode should be used
                        use_ai = (cycle_mode == 'ai')
                        
                        # Generate analysis report
                        cycle_analysis_report = cycle_analyzer.generate_analysis_report(
                            statistics, 
                            use_ai=use_ai
                        )
                        
                        cycle_analysis = {
                            'report': cycle_analysis_report,
                            'mode': cycle_mode,
                            'statistics': {
                                'total_cycles': statistics['total_cycles'],
                                'approximate_average_duration': round(statistics['approximate_average_duration'], 2),
                                'specific_average_duration': round(statistics['specific_average_duration'], 2),
                                'idle_time_per_cycle': round(statistics['idle_time_per_cycle'], 2),
                                'min_duration': statistics['min_duration'],
                                'max_duration': statistics['max_duration'],
                                'std_deviation': round(statistics['std_deviation'], 2)
                            }
                        }
                except Exception as e:
                    print(f"Warning: Could not generate cycle analysis: {e}")
            
            # Check if HTML report generation is requested
            if generate_html_report_flag and html_report_analyzer is not None:
                try:
                    # Parse cycle data from report
                    cycle_data = VideoAnalyzer.parse_cycle_data(report)
                    
                    if not cycle_data:
                        return jsonify({'error': 'No cycle data found in video analysis. HTML report requires cycle time data.'}), 400
                    
                    # Ensure joystick data path is absolute
                    if not os.path.isabs(joystick_data_path):
                        joystick_data_path = os.path.join(os.getcwd(), joystick_data_path)
                    
                    # Prepare operator info with defaults
                    operator_info = {
                        'operator_name': f'Operator (Video: {video_id})',
                        'equipment': 'Excavator',
                        'exercise_date': __import__('datetime').datetime.now().strftime('%Y-%m-%d'),
                        'session_duration': 'N/A'
                    }
                    
                    # Generate HTML report
                    html_content = html_report_analyzer.generate_html_report(
                        cycle_data=cycle_data,
                        joystick_data_path=joystick_data_path,
                        operator_info=operator_info,
                        save_to_file=False,
                    )
                    
                    # Return HTML file for download
                    response = make_response(html_content)
                    response.headers['Content-Type'] = 'text/html'
                    response.headers['Content-Disposition'] = f'attachment; filename=training_report_{video_id}_{__import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
                    return response
                    
                except Exception as e:
                    import traceback
                    print(f"Error generating HTML report: {e}")
                    print(traceback.format_exc())
                    return jsonify({'error': f'Failed to generate HTML report: {str(e)}'}), 500
            
            response_data = {
                'success': True,
                'report': report,
                'video_id': video_id,
                'analyzer_type': 'gemini'
            }
            
            if cycle_analysis:
                response_data['cycle_analysis'] = cycle_analysis
            
            return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/presets', methods=['GET'])
def get_presets():
    """Get preset video configurations"""
    return jsonify({'presets': PRESET_VIDEOS})


@app.route('/api/generate_html_report', methods=['POST'])
def generate_html_report():
    """Generate HTML training report from cycle data and joystick analytics"""
    try:
        if html_report_analyzer is None:
            return jsonify({'error': 'HTMLReportAnalyzer not initialized. Please check your API key.'}), 500
        
        data = request.get_json()
        
        # Extract required data
        cycle_data = data.get('cycle_data')
        joystick_data_path = data.get('joystick_data_path', 'data/joystick_data')
        operator_info = data.get('operator_info', {})
        save_to_file = data.get('save_to_file', True)
        return_html = data.get('return_html', False)
        
        # Validate inputs
        if not cycle_data:
            return jsonify({'error': 'cycle_data is required'}), 400
        
        # Ensure joystick data path is absolute
        if not os.path.isabs(joystick_data_path):
            joystick_data_path = os.path.join(os.getcwd(), joystick_data_path)
        
        # Set default operator info
        operator_info.setdefault('operator_name', 'Unknown Operator')
        operator_info.setdefault('equipment', 'Excavator')
        operator_info.setdefault('exercise_date', 
                                 __import__('datetime').datetime.now().strftime('%Y-%m-%d'))
        operator_info.setdefault('session_duration', 'N/A')
        
        # Generate HTML report
        html_content = html_report_analyzer.generate_html_report(
            cycle_data=cycle_data,
            joystick_data_path=joystick_data_path,
            operator_info=operator_info,
            save_to_file=save_to_file,
        )
        
        # Get pipeline data for metadata
        pipeline_data = html_report_analyzer.get_pipeline_data()
        
        response_data = {
            'success': True,
            'message': 'HTML report generated successfully',
            'metadata': {
                'total_cycles': pipeline_data.get('cycle_metrics', {}).get('total_cycles', 0),
                'productivity_score': pipeline_data.get('performance_scores', {}).get('productivity_score', 0),
                'control_skill_score': pipeline_data.get('performance_scores', {}).get('control_skill_score', 0),
                'safety_score': pipeline_data.get('performance_scores', {}).get('safety_score', 0),
                'proficiency_level': pipeline_data.get('insights', {}).get('proficiency_level', 'Unknown'),
            }
        }
        
        # Include HTML content if requested
        if return_html:
            response_data['html_content'] = html_content
        
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        print(f"Error generating HTML report: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate_html_report_from_video', methods=['POST'])
def generate_html_report_from_video():
    """Generate HTML report directly from video analysis results"""
    try:
        if html_report_analyzer is None:
            return jsonify({'error': 'HTMLReportAnalyzer not initialized'}), 500
        
        if analyzer_gemini is None:
            return jsonify({'error': 'Video analyzer not initialized'}), 500
        
        data = request.get_json()
        
        # Get video analysis results
        video_url = data.get('video_url')
        prompt_type = data.get('prompt_type', 'cycle_time_simple')
        joystick_data_path = data.get('joystick_data_path', 'data/joystick_data')
        operator_info = data.get('operator_info', {})
        
        if not video_url:
            return jsonify({'error': 'video_url is required'}), 400
        
        # First, analyze the video to get cycle data
        report = analyzer_gemini.generate_report(
            video_url=video_url,
            prompt_type=prompt_type,
            save_to_file=False
        )
        
        if report is None:
            return jsonify({'error': 'Failed to analyze video'}), 500
        
        # Parse cycle data from report
        cycle_data = VideoAnalyzer.parse_cycle_data(report)
        
        if not cycle_data:
            return jsonify({'error': 'No cycle data found in video analysis'}), 400
        
        # Ensure joystick data path is absolute
        if not os.path.isabs(joystick_data_path):
            joystick_data_path = os.path.join(os.getcwd(), joystick_data_path)
        
        # Generate HTML report
        html_content = html_report_analyzer.generate_html_report(
            cycle_data=cycle_data,
            joystick_data_path=joystick_data_path,
            operator_info=operator_info,
            save_to_file=True,
        )
        
        # Get pipeline data
        pipeline_data = html_report_analyzer.get_pipeline_data()
        
        return jsonify({
            'success': True,
            'message': 'HTML report generated from video analysis',
            'video_analysis_report': report,
            'metadata': {
                'total_cycles': len(cycle_data),
                'productivity_score': pipeline_data.get('performance_scores', {}).get('productivity_score', 0),
                'control_skill_score': pipeline_data.get('performance_scores', {}).get('control_skill_score', 0),
                'safety_score': pipeline_data.get('performance_scores', {}).get('safety_score', 0),
                'proficiency_level': pipeline_data.get('insights', {}).get('proficiency_level', 'Unknown'),
            }
        })
        
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


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


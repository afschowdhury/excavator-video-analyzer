import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from agents.core.report_orchestrator_agent import ReportOrchestrator
from scripts.html_report_analyzer import HTMLReportAnalyzer

# Mock data
cycle_data = [
    {'cycle_num': 1, 'start_time': '00:10', 'end_time': '00:25', 'duration': 15},
    {'cycle_num': 2, 'start_time': '00:30', 'end_time': '00:48', 'duration': 18}
]

operator_info = {
    'operator_name': 'Test Operator',
    'equipment': 'Excavator',
    'exercise_date': '2025-12-10',
    'session_duration': '5 min'
}

# Run analyzer
try:
    print("Initializing HTMLReportAnalyzer...")
    analyzer = HTMLReportAnalyzer()
    
    print("Generating report for trial B8...")
    # joystick_data_path points to the folder containing selected_trials.json
    joystick_data_path = os.path.join(os.getcwd(), 'data', 'joystick_data')
    
    html = analyzer.generate_html_report(
        cycle_data=cycle_data,
        joystick_data_path=joystick_data_path,
        operator_info=operator_info,
        trial_id='B8',
        save_to_file=True,
        filename='debug_report_B8'
    )
    
    print("Report generated successfully!")
    
    # Check if images are in the HTML
    if "data:image/png;base64" in html:
        print("✅ SUCCESS: Base64 images found in HTML report!")
        # Count occurrences
        count = html.count("data:image/png;base64")
        print(f"Found {count} images embedded.")
    else:
        print("❌ FAILURE: No base64 images found in HTML report.")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

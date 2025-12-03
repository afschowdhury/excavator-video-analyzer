# HTML Report Generator - Multi-Agent System

A comprehensive multi-agent system built with Gemini 2.5 Pro for generating professional HTML training reports from excavator video analysis and joystick telemetry data.

## Overview

The HTML Report Generator is a sophisticated multi-agent pipeline that analyzes excavator operator performance and produces detailed, actionable training reports. It integrates seamlessly with the existing video analysis system and joystick analytics.

## Architecture

### Multi-Agent Pipeline

The system consists of 5 specialized agents coordinated by a central orchestrator:

1. **CycleMetricsAgent** - Calculates cycle time statistics and efficiency metrics
2. **JoystickAnalyticsAgent** - Processes joystick telemetry and control coordination data
3. **PerformanceScoreAgent** - Generates AI-powered performance scores using Gemini 2.0 Flash
4. **InsightsGeneratorAgent** - Creates personalized training recommendations using Gemini 2.5 Pro
5. **HTMLAssemblerAgent** - Assembles the final professional HTML report using Gemini 2.5 Pro

### Data Flow

```
Video Analysis (cycle_data) + Joystick Data (stats.json)
    ↓
HTMLReportAnalyzer
    ↓
ReportOrchestrator
    ├→ CycleMetricsAgent → Cycle statistics
    ├→ JoystickAnalyticsAgent → Control analytics
    ├→ PerformanceScoreAgent → Productivity/Control/Safety scores
    ├→ InsightsGeneratorAgent → AI-powered insights & recommendations
    └→ HTMLAssemblerAgent → Final HTML report
```

## Installation & Setup

### Prerequisites

```bash
# Already installed in the main project
pip install google-genai python-dotenv rich
```

### Environment Variables

Ensure your `.env` file contains:

```bash
GENAI_API_KEY=your_gemini_api_key_here
```

## Usage

### 1. Standalone Script

```python
from html_report_analyzer import HTMLReportAnalyzer
from video_analyzer import VideoAnalyzer

# Initialize analyzers
video_analyzer = VideoAnalyzer()
html_analyzer = HTMLReportAnalyzer()

# First, analyze video to get cycle data
video_url = "https://youtube.com/watch?v=..."
report = video_analyzer.generate_report(video_url, prompt_type="cycle_time_simple")
cycle_data = VideoAnalyzer.parse_cycle_data(report)

# Generate HTML report
operator_info = {
    "operator_name": "John Doe",
    "equipment": "CAT 320 Excavator",
    "exercise_date": "2025-12-03",
    "session_duration": "5 minutes"
}

html_report = html_analyzer.generate_html_report(
    cycle_data=cycle_data,
    joystick_data_path="data/joystick_data",
    operator_info=operator_info,
    save_to_file=True
)
```

### 2. Flask API Endpoints

#### Generate HTML Report from Cycle Data

```bash
POST /api/generate_html_report

{
    "cycle_data": [
        {
            "cycle_num": 1,
            "start_time": "00:10",
            "end_time": "00:28",
            "duration": 18,
            "notes": "Smooth operation"
        },
        ...
    ],
    "joystick_data_path": "data/joystick_data",
    "operator_info": {
        "operator_name": "Test Operator",
        "equipment": "CAT 320",
        "exercise_date": "2025-12-03",
        "session_duration": "5 minutes"
    },
    "save_to_file": true,
    "return_html": false
}
```

#### Generate HTML Report Directly from Video

```bash
POST /api/generate_html_report_from_video

{
    "video_url": "https://youtube.com/watch?v=...",
    "prompt_type": "cycle_time_simple",
    "joystick_data_path": "data/joystick_data",
    "operator_info": {
        "operator_name": "Test Operator",
        "equipment": "CAT 320"
    }
}
```

### 3. Testing

Run the comprehensive test suite:

```bash
python test_html_report.py
```

This will:
- Test HTML report generation with sample data
- Verify all pipeline stages
- Create a test report at `reports/test_html_report.html`
- Display detailed metrics and scores

## Report Structure

The generated HTML report includes:

### 1. Executive Summary
- **Productivity Score** (0-100) with status
- **Control Skill Score** (0-100) with status  
- **Safety Score** (0-100) with status
- Color-coded visual indicators

### 2. Performance Metrics
- Average cycle time vs. benchmark
- Cycle time variance and consistency
- Efficiency trends over time
- Statistical analysis

### 3. Advanced Control Analytics
- **Bimanual Coordination Score (BCS)**
- **Simultaneity Index (SI) Matrix** - Shows control coordination
- **Multi-Control Usage Distribution** - Dual/triple/full control percentages
- Embedded heatmap visualizations (if available)

### 4. AI-Generated Insights
- **Pattern Recognition**: Control patterns, timing patterns, efficiency patterns
- **Personalized Training Recommendations**: 3-5 specific, actionable recommendations
- Professional, encouraging feedback

### 5. Summary & Next Steps
- Overall performance assessment (2-3 paragraphs)
- Proficiency level classification (Beginner/Intermediate/Advanced/Expert)
- Estimated training hours to next level
- 3 priority focus areas for next session

## File Structure

```
bnk/
├── html_report_analyzer.py          # Main analyzer class
├── test_html_report.py               # Test suite
├── agents/
│   ├── cycle_metrics_agent.py        # Cycle statistics
│   ├── joystick_analytics_agent.py   # Joystick data processing
│   ├── performance_score_agent.py    # AI-powered scoring
│   ├── insights_generator_agent.py   # AI insights & recommendations
│   ├── html_assembler_agent.py       # HTML generation
│   └── report_orchestrator_agent.py  # Pipeline coordinator
├── prompt_templates/
│   ├── report_performance_scoring.toml
│   ├── report_insights_generation.toml
│   └── report_html_assembly.toml
└── reports/                          # Generated HTML reports saved here
```

## Configuration

### Agent Configuration

Each agent can be configured via the orchestrator:

```python
config = {
    "performance_score": {
        "model": "gemini-2.0-flash-exp",
        "temperature": 0.3
    },
    "insights_generator": {
        "model": "gemini-2.5-pro",
        "temperature": 0.4
    },
    "html_assembler": {
        "model": "gemini-2.5-pro",
        "temperature": 0.2
    }
}

orchestrator = ReportOrchestrator(config=config)
```

### Scoring Thresholds

Performance scores are calculated based on:

**Productivity (0-100):**
- Cycle time efficiency vs. target (20s)
- Consistency and variance
- Improvement trend

**Control Skill (0-100):**
- BCS score (target: >0.25)
- Dual control usage (target: >65%)
- Triple control usage (target: >35%)

**Safety (0-100):**
- Consistency score
- Operation smoothness
- Predictability

**Status Labels:**
- 85-100: "Excellent"
- 70-84: "Good"
- 50-69: "Satisfactory"
- 0-49: "Needs Improvement"

## Customization

### Custom HTML Styling

Modify the CSS in `html_assembler_agent.py` → `_get_css()` method

### Custom Scoring Logic

Modify the scoring algorithms in:
- `performance_score_agent.py` → `_generate_fallback_scores()`
- Or adjust the AI prompts in `prompt_templates/report_performance_scoring.toml`

### Custom Insights

Modify the insights generation prompts in:
- `prompt_templates/report_insights_generation.toml`

## Integration with Existing System

The HTML Report Generator integrates seamlessly with:

1. **video_analyzer.py** - Uses `parse_cycle_data()` output directly
2. **Joystick data** - Reads from `data/joystick_data/stats.json`
3. **Flask app** - Two new endpoints for report generation
4. **Existing agents** - Follows the same `BaseAgent` pattern

## Troubleshooting

### Common Issues

**1. API Key Error**
```
ValueError: GENAI_API_KEY not found
```
Solution: Ensure `.env` file contains valid Gemini API key

**2. Joystick Data Not Found**
```
Warning: Joystick data not found at ...
```
Solution: Report will use fallback data. Place `stats.json` in `data/joystick_data/`

**3. Import Errors**
```
ModuleNotFoundError: No module named 'agents.cycle_metrics_agent'
```
Solution: Ensure all agent files are in the `agents/` directory

### Debugging

Enable detailed logging:

```python
from icecream import ic
ic.enable()
```

Check pipeline data:

```python
pipeline_data = html_analyzer.get_pipeline_data()
print(pipeline_data)
```

## Performance

- **Average generation time**: 30-60 seconds
- **API calls**: 3-4 Gemini API calls per report
- **Token usage**: ~5,000-10,000 tokens per report
- **Cost**: ~$0.05-0.15 per report (Gemini 2.5 Pro pricing)

## Future Enhancements

Potential improvements:

1. **Subcycle Analysis** - Add detailed phase-by-phase analysis (digging, swinging, dumping)
2. **Video Snapshots** - Embed annotated video frames at key timestamps
3. **Comparison Reports** - Compare multiple sessions for trend analysis
4. **Interactive Dashboards** - Add JavaScript charts and interactivity
5. **PDF Export** - Generate PDF versions of reports
6. **Email Integration** - Automatically email reports to operators/trainers

## License

Part of the Excavator Video Analyzer project.

## Support

For issues or questions:
1. Check this README
2. Review test script: `test_html_report.py`
3. Examine example reports in `reports/` directory
4. Check agent logs in console output


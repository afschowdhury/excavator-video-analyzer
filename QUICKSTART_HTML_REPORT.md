# HTML Report Generator - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Run the Test Suite

```bash
cd /Users/achowd6/.cursor/worktrees/excavator-video-analyzer/bnk
python test_html_report.py
```

This will:
- Generate a sample HTML report
- Save it to `reports/test_html_report.html`
- Display metrics in the console

### Step 2: View the Report

Open the generated report in your browser:

```bash
open reports/test_html_report.html
# or
# Your browser → File → Open → reports/test_html_report.html
```

### Step 3: Generate Your Own Report

```python
from html_report_analyzer import HTMLReportAnalyzer
from video_analyzer import VideoAnalyzer

# Analyze video
video_analyzer = VideoAnalyzer()
report = video_analyzer.generate_report(
    video_url="YOUR_YOUTUBE_URL",
    prompt_type="cycle_time_simple"
)
cycle_data = VideoAnalyzer.parse_cycle_data(report)

# Generate HTML report
html_analyzer = HTMLReportAnalyzer()
html_report = html_analyzer.generate_html_report(
    cycle_data=cycle_data,
    joystick_data_path="data/joystick_data",
    operator_info={
        "operator_name": "Your Name",
        "equipment": "CAT 320",
        "exercise_date": "2025-12-03",
        "session_duration": "5 minutes"
    }
)

print("Report saved to reports/")
```

## 📋 What Gets Generated

Your HTML report includes:

1. **Executive Summary**
   - Productivity Score (0-100)
   - Control Skill Score (0-100)
   - Safety Score (0-100)

2. **Performance Metrics**
   - Cycle time statistics
   - Consistency scores
   - Efficiency trends

3. **Control Analytics**
   - Bimanual Coordination Score
   - Control usage distribution
   - SI Matrix heatmap

4. **AI Insights**
   - Pattern recognition
   - Training recommendations
   - Next focus areas

5. **Summary**
   - Proficiency level
   - Training hours needed
   - Next steps

## 🌐 Using the API

### Start the Flask Server

```bash
python app.py
```

### Generate Report from Cycle Data

```bash
curl -X POST http://localhost:5000/api/generate_html_report \
  -H "Content-Type: application/json" \
  -d '{
    "cycle_data": [
      {
        "cycle_num": 1,
        "duration": 18,
        "start_time": "00:10",
        "end_time": "00:28",
        "notes": "Good coordination"
      }
    ],
    "joystick_data_path": "data/joystick_data",
    "operator_info": {
      "operator_name": "Test User",
      "equipment": "CAT 320"
    }
  }'
```

### Generate Report from Video URL

```bash
curl -X POST http://localhost:5000/api/generate_html_report_from_video \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://youtube.com/watch?v=...",
    "prompt_type": "cycle_time_simple",
    "joystick_data_path": "data/joystick_data",
    "operator_info": {
      "operator_name": "Test User",
      "equipment": "CAT 320"
    }
  }'
```

## 📁 File Locations

| Item | Location |
|------|----------|
| Generated Reports | `reports/*.html` |
| Joystick Data | `data/joystick_data/stats.json` |
| Test Script | `test_html_report.py` |
| Main Analyzer | `html_report_analyzer.py` |
| Full Documentation | `HTML_REPORT_GENERATOR_README.md` |

## 🔧 Configuration

Edit `agents/report_orchestrator_agent.py` to customize:

```python
config = {
    "performance_score": {
        "model": "gemini-2.0-flash-exp",  # Fast scoring
        "temperature": 0.3
    },
    "insights_generator": {
        "model": "gemini-2.5-pro",  # High-quality insights
        "temperature": 0.4
    },
    "html_assembler": {
        "model": "gemini-2.5-pro",  # Professional HTML
        "temperature": 0.2
    }
}
```

## ❓ Troubleshooting

### API Key Error
```bash
# Add to .env file:
GENAI_API_KEY=your_key_here
```

### Joystick Data Missing
```bash
# Create directory and add stats.json:
mkdir -p data/joystick_data
# Copy your stats.json there
```

### Import Error
```bash
# Make sure you're in the right directory:
cd /Users/achowd6/.cursor/worktrees/excavator-video-analyzer/bnk
```

## 📊 Sample Output

The generated report shows:

```
═══════════════════════════════════════════
        OPERATOR TRAINING REPORT
Post-Exercise Performance Analysis
═══════════════════════════════════════════

EXECUTIVE SUMMARY
┌─────────────┬──────────────┬─────────┐
│ PRODUCTIVITY│ CONTROL SKILL│  SAFETY │
│   78/100    │    65/100    │  82/100 │
│    Good     │ Satisfactory │   Good  │
└─────────────┴──────────────┴─────────┘

PERFORMANCE METRICS
• Average Cycle Time: 19.2s (Target: 20s)
• Consistency Score: 85.3%
• Trend: Stable

CONTROL ANALYTICS
• BCS: 0.291 (Target: >0.25)
• Dual Control: 78.8%
• Triple Control: 28.8%

AI INSIGHTS
• Pattern: Good timing, coordination needs work
• Recommendations: 
  - Practice simultaneous control exercises
  - Focus on bimanual coordination
  - Work on consistency training

PROFICIENCY: Intermediate
TRAINING HOURS: 30-40 hours to Advanced
```

## 🎯 Next Steps

1. ✅ Run test: `python test_html_report.py`
2. ✅ View report: `open reports/test_html_report.html`
3. ✅ Try with your video data
4. ✅ Customize styling if needed
5. ✅ Integrate with your workflow

## 📚 More Information

- Full Documentation: `HTML_REPORT_GENERATOR_README.md`
- Implementation Details: `IMPLEMENTATION_SUMMARY_HTML_REPORT.md`
- Architecture: See the README for pipeline diagrams

## ✨ Features

- ✅ AI-Powered Analysis (Gemini 2.5 Pro)
- ✅ Professional HTML Design
- ✅ Responsive & Print-Friendly
- ✅ Color-Coded Metrics
- ✅ Personalized Recommendations
- ✅ Embedded Images
- ✅ Flask API Integration
- ✅ Easy to Use

---

**Ready to generate your first report?**

```bash
python test_html_report.py
```

🎉 Enjoy your professional training reports!


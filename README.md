# Video Analyzer

This Python module provides functionality to analyze excavator operation videos using Google's Gemini API. It generates detailed performance reports with actionable feedback.

## Project Structure

```
.
├── video_analyzer.py    # Main analyzer class
├── report_saver.py      # Report saving functionality
├── prompts.py          # Prompt management system
├── requirements.txt     # Project dependencies
└── reports/            # Default directory for saved reports
```

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root directory and add your Gemini API key:
```
GENAI_API_KEY=your_api_key_here
```

## Usage

```python
from video_analyzer import VideoAnalyzer

# Initialize the analyzer with custom reports directory (optional)
analyzer = VideoAnalyzer(reports_dir="my_reports")

# List available prompt types
print("Available prompts:")
for prompt_type, description in analyzer.list_available_prompts().items():
    print(f"- {prompt_type}: {description}")

# Generate a report using the simple prompt
video_url = "https://youtu.be/your_video_url"
report = analyzer.generate_report(
    video_url,
    prompt_type="simple",  # or "detailed" for more comprehensive analysis
    save_to_file=True,
    filename="my_report"  # Optional custom filename
)
analyzer.display_report(report)
```

## Features

- Analyzes excavator operation videos using Gemini AI
- Generates detailed performance reports with timestamps
- Provides both simple and comprehensive analysis options
- Includes strengths identification and areas for improvement
- Gives personalized improvement tips
- Assigns an overall performance score with justification
- Automatically saves reports as markdown files
- Supports custom filenames and report directories
- Flexible prompt management system

## Prompt Management

The system includes a flexible prompt management system that allows you to:
- Use different types of analysis prompts
- Add new custom prompts
- Version control your prompts
- Get information about available prompts

Available default prompts:
- `simple`: Basic analysis focusing on key performance metrics
- `detailed`: Comprehensive analysis with detailed breakdowns

You can add custom prompts using the `PromptManager`:

```python
from prompts import PromptManager

manager = PromptManager()
manager.add_prompt(
    prompt_type="custom",
    template="Your custom prompt template here...",
    description="Description of what your prompt does",
    version="1.0"
)
```

## File Saving

Reports are automatically saved as markdown files in the specified reports directory (default: `reports/`). The files are named using:
- Custom filename if provided (e.g., `my_report.md`)
- Timestamp-based name if no custom filename is provided (e.g., `excavator_report_20240321_143022.md`)

The file saving functionality is handled by the `ReportSaver` class in `report_saver.py`, which can be used independently if needed:

```python
from report_saver import ReportSaver

saver = ReportSaver(reports_dir="my_reports")
file_path = saver.save_report(report_text, filename="custom_report")
```

## Requirements

- Python 3.7+
- Google Gemini API key
- Internet connection for API access

## Note

The video URLs must be publicly accessible for the Gemini API to analyze them. 
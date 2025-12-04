# Scripts

This folder contains standalone scripts and utilities for the excavator video analyzer.

## Available Scripts

### Analysis Scripts

- **`video_analyzer_gpt5.py`** - GPT-5 based video analyzer for excavation cycle detection
  - Uses multi-agent system to analyze video frames
  - Generates markdown reports with cycle time analysis
  
- **`cycle_time_analyzer.py`** - Cycle time analysis script
  - Analyzes excavation cycle patterns
  - Calculates performance metrics

- **`html_report_analyzer.py`** - HTML report generation script
  - Creates comprehensive HTML reports
  - Includes joystick analytics and performance scoring

### Utilities

- **`report_saver.py`** - Utility for saving analysis reports
  - Handles report formatting and storage
  - Creates timestamped report files

## Usage

Run any script from the project root directory:

```bash
# From project root
python scripts/video_analyzer_gpt5.py

# Or
python scripts/html_report_analyzer.py
```

## Note

These scripts import from the main `agents/` module, so they must be run from the project root directory.


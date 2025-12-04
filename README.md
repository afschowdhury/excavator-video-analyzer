# Excavator Video Analyzer

## Overview

The Excavator Video Analyzer is a Python tool that generates detailed performance reports from excavator operation videos using Google Gemini AI. It leverages prompt templates and provides clear, markdown-formatted reports directly in your terminal, with interactive progress spinners and robust error handling.

## Features

- **Automated Video Analysis:** Generate performance reports from YouTube or video URLs.
- **Prompt Templates:** Easily switch between different analysis styles (simple, detailed) using TOML-based prompt templates.
- **Rich Terminal Output:** Uses the [rich](https://github.com/Textualize/rich) library for colored, markdown-formatted output and interactive spinners.
- **Robust Error Handling:** Clear, color-coded error messages for a smooth user experience.
- **Easy Report Saving:** Automatically saves reports as markdown files in a specified directory.

## Installation

1. **Clone the repository:**
   ```bash
   git clone git@github.com:afschowdhury/excavator-video-analyzer.git
   cd excavator-video-analyzer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment:**
   - Create a `.env` file in the project root with your Google Gemini API key:
     ```env
     GENAI_API_KEY=your_gemini_api_key_here
     ```

## Usage

### Web UI (Recommended)

Run the Flask web application for an interactive, visual experience:

```bash
python app.py
```

Then open your browser and navigate to `http://localhost:5000`

**Features:**
- Select from available prompt templates via dropdown
- Input custom YouTube URLs or choose from preset videos
- Embedded video preview
- Real-time analysis with loading indicators
- Beautifully formatted markdown output

### Command Line Interface

Run the analyzer scripts from your terminal:

```bash
# GPT-5 based video analysis
python scripts/video_analyzer_gpt5.py

# HTML report generation
python scripts/html_report_analyzer.py

# Cycle time analysis
python scripts/cycle_time_analyzer.py
```

- Scripts analyze videos and generate reports
- Reports are saved in the `reports/` directory by default
- See `scripts/README.md` for more details

## Project Structure

```
excavator-video-analyzer/
├── agents/                      # Multi-agent system
│   ├── base_agent.py           # Base agent class
│   ├── gpt/                    # OpenAI GPT agents
│   │   ├── frame_classifier.py # Frame classification
│   │   └── report_generator.py # Report generation
│   ├── gemini/                 # Google Gemini agents
│   │   ├── html_assembler_agent.py
│   │   ├── insights_generator_agent.py
│   │   └── performance_score_agent.py
│   └── core/                   # Non-LLM logic agents
│       ├── action_detector.py
│       ├── cycle_assembler.py
│       ├── cycle_metrics_agent.py
│       ├── frame_extractor.py
│       ├── joystick_analytics_agent.py
│       ├── orchestrator.py
│       └── report_orchestrator_agent.py
├── prompts/                    # Prompt templates
│   ├── gpt/                    # GPT model prompts
│   │   ├── frame_classifier.toml
│   │   └── report_generator.toml
│   ├── gemini/                 # Gemini model prompts
│   │   ├── html_assembler.toml
│   │   ├── insights_generator.toml
│   │   └── performance_score.toml
│   └── *.toml                  # Other prompt templates
├── docs/                       # User-facing documentation
│   ├── QUICKSTART_GPT5.md
│   ├── QUICKSTART_HTML_REPORT.md
│   └── ...
├── implementation_details/     # Technical documentation
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── ...
├── scripts/                    # Analysis and utility scripts
│   ├── video_analyzer_gpt5.py
│   ├── html_report_analyzer.py
│   ├── cycle_time_analyzer.py
│   └── report_saver.py
├── tests/                      # Test files
│   ├── test_cycle_analyzer.py
│   ├── test_html_report.py
│   └── ...
├── data/                       # Sample data and videos
├── reports/                    # Generated reports
├── experiments/                # Experimental notebooks and scripts
├── static/                     # Web UI assets
├── templates/                  # Web UI templates
├── app.py                      # Flask web application
├── prompts.py                  # Prompt management
├── config.py                   # Configuration
└── requirements.txt            # Dependencies
```

## Configuration

- **Prompt Templates:**
  - Located in the `prompts/` directory as TOML files organized by model type (`prompts/gpt/`, `prompts/gemini/`).
  - Each TOML file contains the prompt content, model configuration (temperature, max_tokens, etc.), and metadata.
  - You can add or modify templates to change the analysis style.
- **Reports Directory:**
  - By default, reports are saved in the `reports/` folder. You can change this in the `VideoAnalyzer` constructor.

## Documentation

- **[docs/](docs/)** - User guides and quick start documentation
- **[implementation_details/](implementation_details/)** - Technical implementation notes and design decisions

## Example Output

```
Generating report...
# Excavator Simulator Performance Report

1. Detailed Action Analysis:
...

Report saved to: reports/excavator_report_20250507_122111.md
```


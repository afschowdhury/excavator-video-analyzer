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

Run the analyzer script from your terminal:

```bash
python video_analyzer.py
```

- The script will prompt the Gemini model to analyze a sample video and display the report in your terminal.
- Reports are saved in the `reports/` directory by default.
- You can customize the video URL and prompt type by editing the `main()` function in `video_analyzer.py`.

## Configuration

- **Prompt Templates:**
  - Located in the `prompt_templates/` directory as TOML files (e.g., `simple.toml`, `detailed.toml`).
  - You can add or modify templates to change the analysis style.
- **Reports Directory:**
  - By default, reports are saved in the `reports/` folder. You can change this in the `VideoAnalyzer` constructor.

## Example Output

```
Generating report...
# Excavator Simulator Performance Report

1. Detailed Action Analysis:
...

Report saved to: reports/excavator_report_20250507_122111.md
```


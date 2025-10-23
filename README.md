# Excavator Video Analyzer

## Overview

The Excavator Video Analyzer is an advanced Python tool that generates detailed performance reports from excavator operation videos using Google Gemini AI and multi-agent architecture. It features:

- **Multi-Agent Analysis**: Uses specialized AI agents for cycle detection and technique evaluation
- **Cycle Time Analysis**: Precise detection and timing of all dig-dump cycles with timestamps
- **POML Integration**: Structured prompt markup for consistent, parseable outputs
- **Comprehensive Reporting**: Detailed markdown reports with benchmarks and recommendations
- **Flexible Architecture**: Support for both traditional single-model and advanced multi-agent analysis

## Features

### Core Functionality
- **Automated Video Analysis:** Generate performance reports from YouTube or video URLs
- **Multi-Agent Architecture:** Specialized agents for cycle detection and technique evaluation
- **Cycle Time Detection:** Identifies ALL dig-dump cycles with precise timestamps
- **POML Structured Output:** Parseable, structured markup language for consistent results
- **Benchmark Comparisons:** Compares performance against industry standards

### Analysis Capabilities
- **Comprehensive Cycle Analysis:**
  - Start/end timestamps for each cycle
  - Phase breakdown (Dig → Swing → Dump → Return)
  - Duration tracking for each phase
  - Average, fastest, and slowest cycle identification
  - Productivity metrics (cycles/hour)
  
- **Technique Evaluation:**
  - Control & precision assessment
  - Efficiency & workflow analysis
  - Safety awareness evaluation
  - Prioritized improvement recommendations

### Technical Features
- **Prompt Templates:** TOML-based templates for different analysis styles
- **Rich Terminal Output:** Colored, markdown-formatted output with progress indicators
- **Flexible Configuration:** Customize models, temperatures, and agent behavior
- **Report Generation:** Automatic markdown reports with tables and visualizations
- **Robust Error Handling:** Graceful degradation and detailed error messages

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

### Quick Start

Run the analyzer script from your terminal:

```bash
python video_analyzer.py
```

This will run three types of analysis:
1. Traditional simple analysis
2. Traditional detailed analysis
3. **NEW: Multi-agent ADK analysis with cycle time detection** (Recommended)

### Using Multi-Agent Analysis (Recommended)

```python
from video_analyzer import VideoAnalyzer

analyzer = VideoAnalyzer()

# Multi-agent analysis with cycle time detection
report = analyzer.analyze_with_agents(
    video_url="https://youtu.be/your-video-url",
    include_cycle_times=True,
    include_technique_analysis=True,
    save_to_file=True
)

analyzer.display_report(report)
```

### Traditional Single-Model Analysis

```python
# Simple analysis
report = analyzer.generate_report(
    video_url="https://youtu.be/your-video-url",
    prompt_type="simple",
    save_to_file=True
)

# Detailed analysis
detailed_report = analyzer.generate_report(
    video_url="https://youtu.be/your-video-url",
    prompt_type="detailed",
    save_to_file=True
)
```

### Using Individual Agents

```python
from agents import CycleDetectorAgent, TechniqueEvaluatorAgent

# Detect cycles only
cycle_agent = CycleDetectorAgent()
results = cycle_agent.process("https://youtu.be/your-video-url")
print(f"Found {results['cycle_count']} cycles")

# Evaluate technique only
technique_agent = TechniqueEvaluatorAgent()
results = technique_agent.process("https://youtu.be/your-video-url")
print(f"Overall score: {results['overall_score']['score']}")
```

## Configuration

### Prompt Templates

Located in the `prompt_templates/` directory:

- **simple.toml** - Basic performance analysis
- **detailed.toml** - Comprehensive analysis with cycle time focus
- **poml_cycle_detection.toml** - POML-structured cycle detection
- **poml_technique_evaluation.toml** - POML-structured technique evaluation
- **cycle_time_analysis.toml** - Cycle analysis with benchmark comparisons

### ADK Configuration

Customize agent behavior:

```python
from config.adk_config import ADKConfig

config = ADKConfig(
    default_model="gemini-2.0-flash-exp",
    timeout=600,
    parallel_execution=False
)

# Customize individual agents
config.cycle_detector.model.temperature = 0.05
config.technique_evaluator.model.max_tokens = 6000

report = analyzer.analyze_with_agents(video_url, config=config)
```

### Reports Directory

- Default: `reports/` folder
- Customize in `VideoAnalyzer` constructor
- Reports include timestamps in filenames

## Example Output

### Multi-Agent ADK Analysis Output

```
[Orchestrator] Starting orchestrated analysis...
[Orchestrator] Phase 1: Cycle detection
[CycleDetector] Starting cycle detection analysis...
[CycleDetector] Successfully detected 12 cycles

[Orchestrator] Phase 2: Technique evaluation
[TechniqueEvaluator] Starting technique evaluation...
[TechniqueEvaluator] Evaluation complete - Score: 82/100

[Orchestrator] Phase 3: Compiling results
[Orchestrator] Orchestrated analysis complete!

# Excavator Performance Analysis Report

## Summary
- Total Cycles Detected: 12
- Average Cycle Time: 38.5 seconds
- Overall Performance Score: 82/100
- Performance Grade: B+

## Cycle Time Analysis

| Cycle | Start | End | Duration | Phases |
|-------|-------|-----|----------|--------|
| 1 | 00:15.2 | 00:47.8 | 32.6s | 4 phases |
| 2 | 00:48.0 | 01:19.5 | 31.5s | 4 phases |
...

Report saved to: reports/adk_multi_agent_analysis.md
```

## Advanced Features

### Cycle Time Benchmarks

The system compares performance against industry standards:
- **Optimal**: 35-45 seconds (skilled operator)
- **Acceptable**: 45-60 seconds (average operator)
- **Below Standard**: >60 seconds (needs improvement)

### Phase-Specific Analysis

Each cycle is broken down into phases:
- **Dig Phase**: Bucket descends and fills (Benchmark: 8-12s)
- **Swing to Dump**: Loaded swing to dump location (Benchmark: 9-13s)
- **Dump Phase**: Material release (Benchmark: 3-5s)
- **Return Swing**: Empty return to dig position (Benchmark: 8-12s)

## Documentation

- **[ADK Integration Guide](ADK_INTEGRATION.md)** - Detailed documentation on multi-agent architecture
- **[Prompt Templates](prompt_templates/)** - TOML template files
- **[API Reference](docs/API.md)** - Coming soon


# ADK Multi-Agent Integration Guide

## Overview

This document describes the integration of Google's Agent Development Kit (ADK) and POML (Prompt-Oriented Markup Language) into the Excavator Video Analyzer system.

## Architecture

### Multi-Agent System

The system uses a multi-agent architecture with specialized agents coordinated by an orchestrator:

```
┌─────────────────────────────────────────────────────────┐
│                  OrchestratorAgent                      │
│  (Coordinates multi-agent workflow)                     │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼──────────┐  ┌──────▼────────────────┐
│CycleDetectorAgent│  │TechniqueEvaluatorAgent│
│                  │  │                       │
│ - Detects cycles │  │ - Evaluates technique │
│ - Timestamps     │  │ - Scores performance  │
│ - POML parsing   │  │ - Recommendations     │
└──────────────────┘  └───────────────────────┘
```

### Agent Roles

1. **CycleDetectorAgent**
   - Analyzes entire video to detect all dig-dump cycles
   - Provides precise timestamps for each cycle phase
   - Outputs structured POML markup
   - Calculates cycle statistics

2. **TechniqueEvaluatorAgent**
   - Evaluates operator technique and performance
   - Provides category-based scoring
   - Generates prioritized recommendations
   - Uses cycle context for enhanced analysis

3. **OrchestratorAgent**
   - Coordinates agent execution
   - Aggregates results
   - Generates comprehensive reports
   - Manages workflow and error handling

## POML (Prompt-Oriented Markup Language)

POML is a structured markup format used to ensure consistent, parseable outputs from AI models.

### Cycle Detection POML Format

```xml
<cycle id="1" start="00:15.2" end="00:47.8" total_duration="32.6s">
  <dig start="00:15.2" end="00:25.1" duration="9.9s" description="Bucket descends and fills"/>
  <swing_to_dump start="00:25.1" end="00:35.6" duration="10.5s" description="Swing to dump"/>
  <dump start="00:35.6" end="00:40.2" duration="4.6s" description="Release material"/>
  <return start="00:40.2" end="00:47.8" duration="7.6s" description="Return to dig"/>
</cycle>
```

### Technique Evaluation POML Format

```xml
<evaluation>
  <control_precision score="85/100">
    <strength timestamp="00:25.3">Smooth coordinated movement</strength>
    <improvement timestamp="00:42.1">Practice smoother control</improvement>
  </control_precision>
</evaluation>
```

## Usage

### Basic Multi-Agent Analysis

```python
from video_analyzer import VideoAnalyzer

analyzer = VideoAnalyzer()
report = analyzer.analyze_with_agents(
    video_url="https://youtu.be/your-video",
    include_cycle_times=True,
    include_technique_analysis=True,
    save_to_file=True
)
```

### Advanced Configuration

```python
from config.adk_config import ADKConfig, ModelConfig, AgentConfig

# Create custom configuration
config = ADKConfig(
    default_model="gemini-2.0-flash-exp",
    parallel_execution=False,
    timeout=600
)

# Customize agent settings
config.cycle_detector.model.temperature = 0.05  # More deterministic
config.technique_evaluator.model.max_tokens = 6000

# Run analysis with custom config
report = analyzer.analyze_with_agents(
    video_url="https://youtu.be/your-video",
    config=config
)
```

### Using Individual Agents

```python
from agents import CycleDetectorAgent, TechniqueEvaluatorAgent

# Cycle detection only
cycle_agent = CycleDetectorAgent()
results = cycle_agent.process(video_url)
cycles = results['cycles']
summary = results['summary']

# Technique evaluation only
technique_agent = TechniqueEvaluatorAgent()
results = technique_agent.process(video_url, cycle_context={'cycle_count': 10})
evaluation = results['evaluation']
```

## Prompt Templates

Three new POML-based prompt templates have been added:

1. **poml_cycle_detection.toml** - Structured cycle time detection
2. **poml_technique_evaluation.toml** - Structured technique evaluation
3. **cycle_time_analysis.toml** - Comprehensive cycle analysis with benchmarks

### Adding Custom Templates

Create a new TOML file in `prompt_templates/`:

```toml
[metadata]
name = "Custom Analysis"
description = "Your custom analysis type"
version = "1.0"
author = "Your Name"

[template]
content = """
Your prompt template here...
"""

[config]
temperature = 0.2
top_p = 0.95
max_tokens = 4000
```

## Cycle Time Analysis

### Industry Benchmarks

- **Optimal**: 35-45 seconds per cycle
- **Acceptable**: 45-60 seconds per cycle
- **Below Standard**: >60 seconds per cycle

### Phase Benchmarks

- **Dig**: 8-12 seconds
- **Swing to Dump**: 9-13 seconds
- **Dump**: 3-5 seconds
- **Return**: 8-12 seconds

### Metrics Calculated

- Total cycles completed
- Average cycle time
- Fastest/slowest cycles
- Productivity rate (cycles/hour)
- Cycle time consistency score
- Phase-specific averages

## Report Generation

### Cycle Time Report

```python
from cycle_time_report import CycleTimeReport

reporter = CycleTimeReport()

# Generate markdown report
report = reporter.generate_markdown_report(
    cycles=cycles_data,
    summary=summary_data,
    metadata={'video_url': video_url}
)

# Display as table in console
reporter.display_table(cycles_data)

# Save to file
reporter.save_report(report, filename="cycle_analysis")
```

## Configuration

### ADK Configuration Options

```python
@dataclass
class ADKConfig:
    default_model: str = "gemini-2.0-flash-exp"
    fallback_model: str = "gemini-1.5-flash"
    
    # Agent configs
    cycle_detector: AgentConfig
    technique_evaluator: AgentConfig
    orchestrator: AgentConfig
    
    # Orchestration
    parallel_execution: bool = False
    timeout: int = 600
    
    # Performance
    cache_results: bool = True
    cache_ttl: int = 3600
    
    # Output
    save_intermediate_results: bool = True
    output_format: str = "markdown"
```

## Error Handling

The multi-agent system includes comprehensive error handling:

- Individual agent failures don't crash the entire system
- Results include error information when agents fail
- Fallback mechanisms for missing prompts
- Detailed logging at each step

## Performance Optimization

### Tips for Best Results

1. **Use appropriate models**:
   - `gemini-2.0-flash-exp` for fast, accurate analysis
   - `gemini-2.0-pro-exp` for more detailed analysis

2. **Adjust temperature**:
   - Lower (0.05-0.1) for cycle detection (deterministic)
   - Medium (0.2-0.3) for technique evaluation (creative)

3. **Optimize token limits**:
   - Cycle detection: 6000-8000 tokens
   - Technique evaluation: 4000-6000 tokens

4. **Sequential vs Parallel**:
   - Sequential (default) ensures cycle context for technique evaluation
   - Parallel (faster) when agents don't need shared context

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Individual test files:
- `tests/test_agents.py` - Agent functionality
- `tests/test_poml_parser.py` - POML parsing
- `tests/test_cycle_report.py` - Report generation

## Troubleshooting

### Common Issues

1. **Missing API Key**
   - Ensure `GENAI_API_KEY` is set in `.env` file

2. **POML Parsing Errors**
   - Check that prompts are using correct POML format
   - Validate XML structure in outputs

3. **Timeout Errors**
   - Increase `timeout` in ADKConfig
   - Use faster model for long videos

4. **Import Errors**
   - Ensure all dependencies installed: `pip install -r requirements.txt`
   - Check Python version (3.8+)

## Future Enhancements

Potential improvements:
- Real-time video streaming analysis
- Multi-video batch processing
- Dashboard visualization of cycle times
- Historical performance tracking
- Comparative analysis across operators
- Integration with training management systems

## Contributing

When adding new agents:

1. Inherit from `BaseAgent`
2. Implement `process()` method
3. Add to `agents/__init__.py`
4. Create corresponding POML prompt template
5. Add tests
6. Update documentation

## License

See main project LICENSE file.


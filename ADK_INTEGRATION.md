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

## POML (Prompt Orchestration Markup Language)

POML is **Microsoft's HTML-like markup language for prompts**, providing a structured, semantic way to define AI prompts. It's similar to how HTML structures web content, but specifically designed for LLM prompt engineering.

**Learn more**: 
- [POML Blog Post](https://www.blog.brightcoding.dev/2025/08/20/poml-the-html-for-prompts-that-will-reshape-how-we-talk-to-ai/)
- [Microsoft POML Documentation](https://microsoft.github.io/poml/)

### Why POML?

Traditional prompts are messy strings. POML brings:
- **Semantic Tags**: `<role>`, `<task>`, `<example>`, `<document>`, `<stylesheet>`
- **Separation of Concerns**: Content separate from styling (like HTML/CSS)
- **Variable Interpolation**: `{{ variable }}` syntax
- **Multi-modal Support**: `<img>`, `<table>`, `<document>` tags
- **Version Control**: Plain text files that git can diff
- **IDE Support**: Syntax highlighting, validation, live preview

### POML File Structure

```xml
<poml>
  <role>You are an expert excavator analyst.</role>

  <task>
    Analyze the video for cycle {{ cycle_id }} in {{ location }}.
  </task>

  <document src="benchmarks.json" format="json" />

  <example>
    Input: Tokyo site, Cycle 1
    Output: Cycle 1 completed in 38.5s...
  </example>

  <output-format>
    Provide results as markdown table with timestamps.
  </output-format>

  <stylesheet>
    temperature = 0.1
    verbosity = detailed
    format = markdown
  </stylesheet>
</poml>
```

### Key POML Tags Used

| Tag | Purpose | Example |
|-----|---------|---------|
| `<role>` | Define AI persona/expertise | `<role>You are an expert...</role>` |
| `<task>` | Main instruction | `<task>Analyze the video...</task>` |
| `<output-format>` | Structure for response | `<output-format>Use markdown...</output-format>` |
| `<example>` | Few-shot examples | `<example>Input: ... Output: ...</example>` |
| `<stylesheet>` | Configuration (temp, format) | `<stylesheet>temperature = 0.1</stylesheet>` |
| `<let>` | Variable declaration | `<let city = "Tokyo" />` |
| `<if>` | Conditional content | `<if cycle_count>Show summary</if>` |

### POML Templates in This Project

Located in `prompt_templates/`:
- **cycle_detection.poml** - Detects dig-dump cycles with timestamps
- **technique_evaluation.poml** - Evaluates operator technique
- **comprehensive_analysis.poml** - Full analysis with cycles + technique
- **simple_analysis.poml** - Basic performance report

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

### Adding Custom POML Templates

Create a new `.poml` file in `prompt_templates/`:

```xml
<poml>
  <role>
    Define the AI's role and expertise here.
  </role>

  <task>
    Your main instruction for the AI.
  </task>

  <output-format>
    Specify how you want the response structured.
  </output-format>

  <example>
    Provide an example input/output pair.
  </example>

  <stylesheet>
    temperature = 0.2
    top_p = 0.95
    max_tokens = 4000
    format = markdown
    verbosity = detailed
  </stylesheet>
</poml>
```

The system automatically loads all `.poml` files from the `prompt_templates/` directory.

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


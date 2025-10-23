# Quick Start Guide - ADK Multi-Agent Cycle Time Analysis

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
echo "GENAI_API_KEY=your_api_key_here" > .env
```

## Run Analysis (3 Methods)

### Method 1: Multi-Agent Analysis (RECOMMENDED) 🌟

```bash
python video_analyzer.py
```

Or programmatically:

```python
from video_analyzer import VideoAnalyzer

analyzer = VideoAnalyzer()
report = analyzer.analyze_with_agents(
    video_url="https://youtu.be/your-video",
    include_cycle_times=True,
    include_technique_analysis=True,
    save_to_file=True
)
analyzer.display_report(report)
```

**Output:**
- Complete cycle time analysis with timestamps
- Phase-by-phase breakdown (Dig → Swing → Dump → Return)
- Technique evaluation with scores
- Benchmark comparisons
- Actionable recommendations

### Method 2: Individual Agents

```python
from agents import CycleDetectorAgent, TechniqueEvaluatorAgent

# Cycle detection only
cycle_agent = CycleDetectorAgent()
results = cycle_agent.process("https://youtu.be/your-video")
print(f"Found {results['cycle_count']} cycles")
print(f"Average time: {cycle_agent.get_average_cycle_time():.1f}s")

# Technique evaluation only
technique_agent = TechniqueEvaluatorAgent()
results = technique_agent.process("https://youtu.be/your-video")
print(f"Score: {results['overall_score']['score']}")
```

### Method 3: Traditional Single-Model

```python
# Simple analysis
report = analyzer.generate_report(
    video_url="https://youtu.be/your-video",
    prompt_type="simple"
)

# Detailed analysis
report = analyzer.generate_report(
    video_url="https://youtu.be/your-video",
    prompt_type="detailed"
)
```

## Run Examples

```bash
python example_usage.py
```

Choose from:
1. Multi-Agent Analysis
2. Custom Configuration
3. Individual Agents
4. Cycle Time Report
5. Traditional Analysis
6. Run All Examples

## Run Tests

```bash
pytest tests/ -v
```

## What You Get

### Cycle Time Analysis
- ✅ ALL cycles detected (not sampled)
- ✅ Precise timestamps (MM:SS.ms)
- ✅ 4-phase breakdown per cycle
- ✅ Average, fastest, slowest cycles
- ✅ Productivity metrics

### Technique Evaluation
- ✅ Multi-category scores
- ✅ Timestamped examples
- ✅ Prioritized recommendations
- ✅ Overall performance grade

### Reports
- ✅ Markdown formatted
- ✅ Tables and statistics
- ✅ Auto-saved with timestamps
- ✅ Benchmark comparisons

## Customization

```python
from config.adk_config import ADKConfig

config = ADKConfig(
    default_model="gemini-2.0-flash-exp",
    timeout=900
)

# Adjust cycle detector
config.cycle_detector.model.temperature = 0.05  # More precise
config.cycle_detector.model.max_tokens = 10000

# Adjust technique evaluator
config.technique_evaluator.model.temperature = 0.25

# Run with custom config
report = analyzer.analyze_with_agents(video_url, config=config)
```

## File Structure

```
excavator-video-analyzer/
├── agents/                    # Multi-agent system
│   ├── base_agent.py
│   ├── cycle_detector_agent.py
│   ├── technique_evaluator_agent.py
│   └── orchestrator_agent.py
├── config/
│   └── adk_config.py         # Agent configuration
├── prompt_templates/          # POML templates
│   ├── poml_cycle_detection.toml
│   ├── poml_technique_evaluation.toml
│   └── cycle_time_analysis.toml
├── tests/                     # Test suite
├── video_analyzer.py          # Main analyzer
├── cycle_time_report.py       # Report generator
├── example_usage.py           # Usage examples
└── reports/                   # Generated reports
```

## Benchmarks

### Cycle Time Standards
- **Optimal**: 35-45 seconds (skilled operator)
- **Acceptable**: 45-60 seconds (average)
- **Below Standard**: >60 seconds (needs improvement)

### Phase Benchmarks
- **Dig**: 8-12 seconds
- **Swing to Dump**: 9-13 seconds
- **Dump**: 3-5 seconds
- **Return**: 8-12 seconds

## Troubleshooting

**API Key Error:**
```bash
# Check .env file exists and has correct key
cat .env
```

**Import Errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**Timeout Errors:**
```python
# Increase timeout in config
config = ADKConfig(timeout=1200)  # 20 minutes
```

## Documentation

- **[README.md](README.md)** - Full feature documentation
- **[ADK_INTEGRATION.md](ADK_INTEGRATION.md)** - Architecture details
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Implementation overview

## Need Help?

1. Check the example_usage.py for working examples
2. Read ADK_INTEGRATION.md for architecture details
3. Run tests to verify installation: `pytest tests/`
4. Review generated reports in `reports/` directory

---

**Branch**: `cycle_time_analysis`  
**Ready for Production**: ✅  
**Tests Passing**: ✅  
**Documentation**: Complete  


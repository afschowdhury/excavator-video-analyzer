# Simulation Metrics Integration - Quick Start Guide

## Overview

The excavator video analyzer now automatically extracts simulation metrics from PDF reports and includes them in the final analysis report.

## What's Included

The system extracts the following metrics from simulation PDFs:

- **Fuel Burned** (Liters)
- **Time Spent Swinging Left** (seconds)
- **Time Spent Swinging Right** (seconds)

## How It Works

### Automatic Integration

When you analyze a video, the system automatically:

1. **Extracts the video ID** from the filename
   - Example: `B6.mp4` → ID: `B6`
   - Example: `2.mp4` → ID: `2`

2. **Searches for matching PDF** in `simulation_report/` directory
   - Looks for: `simulation_report/{ID}.pdf`

3. **Extracts metrics** from the PDF using text parsing

4. **Adds to report** as a new "Simulation Data" section

### Example Usage

```python
from scripts.video_analyzer_gpt5 import VideoAnalyzerGPT5

# Initialize analyzer
analyzer = VideoAnalyzerGPT5(fps=3, model="gpt-4o")

# Analyze video - simulation metrics are automatically included!
report = analyzer.generate_report("videos/B6.mp4", save_to_file=True)
```

### Report Output Example

The generated report will now include:

```markdown
### Simulation Data

**Simulation Report ID:** B6

| Metric | Value |
|--------|-------|
| Fuel Burned | 1.41 L |
| Time Spent Swinging Left | 44 sec |
| Time Spent Swinging Right | 43 sec |
```

## Requirements

### PDF Naming Convention

For automatic extraction to work, ensure:

1. PDF files are in `simulation_report/` directory
2. PDF filename matches video ID: `{ID}.pdf`
3. Video filename includes the ID: `{ID}.mp4` or similar

### Supported Video IDs

The system supports various ID formats:
- Numeric: `2.mp4`, `21.mp4`, `52.mp4`
- Alphanumeric: `B6.mp4`, `A9.mp4`, `A10.mp4`
- Any combination matching the PDF filename

## Handling Missing PDFs

If no matching PDF is found:
- The system continues normally
- No simulation section is added to the report
- A warning is logged (not an error)
- All other analysis proceeds as usual

## Configuration

### Custom Reports Directory

```python
from agents.core.simulation_report_agent import SimulationReportAgent

config = {"reports_dir": "path/to/your/simulation_reports"}
agent = SimulationReportAgent(config=config)
```

### Using the Agent Directly

```python
from agents.core.simulation_report_agent import SimulationReportAgent

agent = SimulationReportAgent()
metrics = agent.process("B6.mp4")

if metrics['found']:
    print(f"Fuel: {metrics['fuel_burned']} L")
    print(f"Left Swing: {metrics['time_swinging_left']} sec")
    print(f"Right Swing: {metrics['time_swinging_right']} sec")
else:
    print("No simulation report found")
```

## Troubleshooting

### Issue: "No simulation report found"

**Cause**: PDF file doesn't exist or naming doesn't match

**Solution**: 
1. Check that PDF exists in `simulation_report/` directory
2. Verify PDF name matches video ID
3. Example: `B6.mp4` requires `simulation_report/B6.pdf`

### Issue: Metrics show as "N/A"

**Cause**: PDF format differs from expected or metrics missing

**Solution**:
1. Open the PDF and verify metrics exist
2. Check that metrics use expected labels:
   - "Fuel Burned"
   - "Time Spent Swinging Left"
   - "Time Spent Swinging Right"
3. The agent supports both time formats:
   - Direct seconds: "44 sec"
   - Time notation: "00:01:01 mins"

### Issue: Wrong video ID extracted

**Cause**: Filename doesn't match expected pattern

**Solution**:
1. Rename video to use clear ID format: `{ID}.mp4`
2. Or rename PDF to match video filename stem
3. Example: `excavator_B6_final.mp4` → Use `excavator_B6_final.pdf`

## Dependencies

The following package is required:

```bash
conda run -n excavator-env pip install pypdf
```

Already added to `requirements.txt`:
```
pypdf>=6.0.0
```

## Testing

Run the test suite to verify functionality:

```bash
conda run -n excavator-env python -m pytest tests/test_simulation_integration.py -v
```

Expected output:
```
11 passed in 0.83s
```

## Architecture

The integration consists of three main components:

1. **SimulationReportAgent** (`agents/core/simulation_report_agent.py`)
   - Extracts video ID from input
   - Reads and parses PDF files
   - Returns structured metrics

2. **AgentOrchestrator** (`agents/core/orchestrator.py`)
   - Calls SimulationReportAgent in pipeline
   - Passes metrics to ReportGenerator via context

3. **ReportGeneratorAgent** (`agents/gpt/report_generator.py`)
   - Formats simulation metrics section
   - Integrates into final markdown report

## Additional Resources

- **Full Implementation Details**: `SIMULATION_METRICS_INTEGRATION_SUMMARY.md`
- **Test Suite**: `tests/test_simulation_integration.py`
- **Agent Source**: `agents/core/simulation_report_agent.py`

## Support

For questions or issues:
1. Check test suite for examples
2. Review implementation summary
3. Examine agent source code with detailed comments
4. Check linter output for code quality issues

---

**Status**: ✓ Implemented and Tested  
**Version**: 1.0  
**Last Updated**: December 2024


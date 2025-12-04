# Troubleshooting Guide

## HTML Report Generation Hanging

**Symptom:** The program hangs when generating HTML reports, particularly at the `HTMLAssemblerAgent` stage.

**Cause:** The Gemini API call may be hanging due to:
- Large prompts causing slow processing
- Network timeouts
- API rate limiting

**Solutions:**

### Option 1: Use Template-Based Generation (Fast)

Skip AI generation and use the template-based approach:

```bash
conda run -n excavator-env python test_html_quick.py
```

This generates reports using templates instead of AI, which is:
- Much faster (completes in seconds)
- More reliable
- Still produces professional reports

### Option 2: Configure HTMLAssembler to Skip AI

Modify the orchestrator config to disable AI:

```python
from agents.report_orchestrator_agent import ReportOrchestrator

config = {
    "html_assembler": {"use_ai": False}
}
orchestrator = ReportOrchestrator(config=config)
```

### Option 3: Check Prompt Size

The updated code now:
- Logs prompt length before sending to Gemini
- Warns if prompt is > 50,000 characters
- Uses concise data formatting to reduce prompt size

### Option 4: Debug Mode

To see what's happening:

```bash
conda run -n excavator-env python test_html_report.py --sample-only
```

Watch for these log messages:
- `Prompt length: X characters` - Check if too large
- `Waiting for Gemini API response` - Shows when API call starts
- `Received response from Gemini API` - Shows when completed

## VideoMetadata Configuration

The video metadata (fps, start_offset, end_offset) is now centralized in `config.py`:

```python
VIDEO_METADATA_CONFIG = {
    "fps": 1,
    "start_offset": "0s",
    "end_offset": "120s",
}
```

To adjust video processing parameters, edit these values in `config.py`.

## Recent Updates

### 2025-12-03: Centralized Video Config
- Added `VIDEO_METADATA_CONFIG` to config.py
- Updated VideoAnalyzer to use centralized config
- Enhanced test_html_report.py with YouTube video support

### 2025-12-03: HTMLAssembler Improvements
- Added concise data formatting to reduce prompt size
- Added `use_ai` configuration option
- Improved logging for API calls
- Better error handling and fallback to template


# GPT-5 Multi-Agent Video Analyzer

## Overview

This is a modular multi-agent system for analyzing excavator videos using OpenAI's GPT-5 (GPT-4o) with frame-by-frame analysis. Unlike the Gemini analyzer that processes videos natively, this system extracts frames and analyzes them sequentially using a pipeline of specialized agents.

## Architecture

The system consists of 5 specialized agents working in a pipeline:

1. **Frame Extractor Agent** - Extracts frames from video at configurable rates (1, 3, 5, 10 FPS)
2. **Frame Classifier Agent** - Classifies each frame into excavation states using GPT vision
3. **Action Detector Agent** - Detects state transitions and key events
4. **Cycle Assembler Agent** - Assembles complete excavation cycles from events
5. **Report Generator Agent** - Generates markdown analysis reports

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Add your OpenAI API key to the `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Add Video Files

Place your video files in the `videos/` directory. The system is configured for local video analysis.

## Usage

### Command Line Interface

```python
from video_analyzer_gpt5 import VideoAnalyzerGPT5

# Initialize analyzer
analyzer = VideoAnalyzerGPT5(
    fps=3,           # Frame rate: 1, 3, 5, or 10
    model="gpt-4o"   # Model: gpt-4o, gpt-4o-mini, gpt-5, gpt-5-mini, gpt-5-nano
)

# Analyze video
report = analyzer.generate_report(
    video_path="videos/B2.mp4",
    fps=3,
    save_to_file=True,
    filename="analysis_report"
)

# Display report
analyzer.display_report(report)

# Get detailed pipeline data
pipeline_data = analyzer.get_pipeline_data()
print(f"Frames extracted: {len(pipeline_data['frames'])}")
print(f"Cycles detected: {len(pipeline_data['cycles'])}")
```

### Web Interface

1. Start the Flask application:
```bash
python app.py
```

2. Open your browser to `http://localhost:8005`

3. Select "GPT-5 (Multi-Agent)" from the AI Analyzer dropdown

4. Configure:
   - **GPT-5 Model**: Choose the model variant
   - **Frame Rate (FPS)**: Select frame extraction rate
   - **Video Source**: Select "Local Video" and choose your video

5. Click "Analyze Video"

## Frame Rate Guidelines

| FPS | Frames Analyzed* | Processing Time | Cost | Best For |
|-----|-----------------|----------------|------|----------|
| 1   | ~30-60          | Fastest        | $    | Quick estimates, testing |
| 3   | ~90-180         | Balanced       | $$   | Production use, good accuracy |
| 5   | ~150-300        | Slower         | $$$  | Detailed analysis |
| 10  | ~300-600        | Slowest        | $$$$ | Maximum detail, research |

*For a typical 30-60 second video

## Running Experiments

Compare different FPS settings to find optimal configuration:

```bash
python experiments/run_experiments.py
```

This will:
- Test all FPS rates (1, 3, 5, 10)
- Generate comparison reports
- Calculate processing time and costs
- Show cycle detection consistency
- Save results to `experiments/results/`

## Cost Estimation

Approximate costs per analysis (using GPT-4o):

- **1 FPS**: $0.30 - $0.60 per video
- **3 FPS**: $0.90 - $1.80 per video  
- **5 FPS**: $1.50 - $3.00 per video
- **10 FPS**: $3.00 - $6.00 per video

*Costs vary based on video length and model used*

## Excavation States

The Frame Classifier identifies these states:

- **digging**: Bucket entering or digging into material
- **swing_to_dump**: Swinging right to dump area with loaded bucket
- **dumping**: Releasing/dumping material
- **swing_to_dig**: Swinging left back to dig position with empty bucket
- **idle**: No significant action or transitional state

## Cycle Definition

A complete excavation cycle includes:

1. **dig_start** - Beginning of digging
2. **dig_end** - Digging complete, starting swing
3. **dump_start** - Arriving at dump location
4. **dump_end** - Dump complete
5. **return_to_dig** - Returned to original position

## Output Format

Reports include:

- Cycle table with timestamps (MM:SS format)
- Cycle durations
- Phase breakdowns
- Performance analysis
- Observations and recommendations

Example:

```markdown
## Cycle Time Analysis Report

**Video Duration:** 60.0s | **Frames Analyzed:** 180 | **Sample Rate:** 3 FPS

### Excavation Cycles

| Cycle # | Start Time | End Time | Duration | Notes |
|---------|------------|----------|----------|-------|
| 1       | 00:05      | 00:23    | 18.0s    | Normal cycle |
| 2       | 00:24      | 00:41    | 17.0s    | Normal cycle |
| 3       | 00:42      | 00:58    | 16.0s    | Quick dig |

### Analysis
...
```

## Troubleshooting

### "OpenAI API key not found"
- Ensure `OPENAI_API_KEY` is set in your `.env` file
- Restart the application after adding the key

### "Video file not found"
- Check that the video file exists in the specified path
- Use absolute paths or ensure relative paths are correct

### "Unsupported parameter: 'max_tokens'" error
- This happens when using GPT-5 models with old parameter format
- The code automatically detects model type and uses correct parameters:
  - GPT-4 models (gpt-4o, gpt-4o-mini): use `max_tokens`
  - GPT-5 models (gpt-5, gpt-5-mini, gpt-5-nano): use `max_completion_tokens`
- Make sure you're using the latest version of the code

### Analysis takes too long
- Reduce FPS setting (try 1 FPS for testing)
- Use a shorter video clip
- Consider using gpt-4o-mini model

### Inconsistent cycle detection
- Try increasing FPS for more frames
- Check if video quality is sufficient
- Review the classified frames to verify accuracy

## Comparison: Gemini vs GPT-5

| Feature | Gemini | GPT-5 Multi-Agent |
|---------|--------|-------------------|
| Video Support | Native | Frame-by-frame |
| Setup Complexity | Simple | Moderate |
| Processing Speed | Fast | Slower |
| Cost per Analysis | Lower | Higher |
| Customization | Limited | Highly modular |
| Frame Control | No | Yes (1-10 FPS) |
| Local Videos | No* | Yes |
| YouTube Videos | Yes | No |

*Gemini requires video URLs, not local files by default

## Advanced Configuration

### Custom Agent Configuration

```python
config = {
    "frame_extractor": {"fps": 5},
    "frame_classifier": {
        "model": "gpt-4o",
        "temperature": 0.2
    },
    "report_generator": {
        "model": "gpt-4o",
        "temperature": 0.3
    }
}

from agents.orchestrator import AgentOrchestrator
orchestrator = AgentOrchestrator(config)
result = orchestrator.run_pipeline("videos/B2.mp4")
```

### Accessing Intermediate Data

```python
analyzer = VideoAnalyzerGPT5(fps=3)
result = analyzer.analyze_video("videos/B2.mp4")

# Access intermediate results
frames = result['frames']  # Extracted frames
events = result['events']  # Detected events
cycles = result['cycles']  # Assembled cycles

# Examine specific cycle
cycle = cycles[0]
print(f"Cycle {cycle['cycle_number']}")
print(f"Duration: {cycle['duration']}s")
print(f"Phases: {cycle['phases']}")
```

## Contributing

To add a new agent:

1. Create agent class inheriting from `BaseAgent`
2. Implement `process(input_data, context)` method
3. Add agent to orchestrator pipeline
4. Update configuration as needed

## License

Same as main project.


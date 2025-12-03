# Cycle Time Analyzer

A simple average cycle time analyzer that processes excavation cycle data and generates statistical analysis using the Gemini Flash model.

## Overview

The Cycle Time Analyzer extends the excavator video analyzer by automatically parsing cycle time data from video analysis reports and generating detailed statistical insights. It provides:

- Automatic cycle data parsing from markdown reports
- Statistical calculations (average, min, max, standard deviation)
- AI-powered or simple statistical reports
- Web UI integration for seamless analysis

## Features

### 1. **Cycle Data Parser**
- Automatically extracts cycle timestamps from markdown tables
- Converts MM:SS format to seconds
- Parses cycle numbers, start times, end times, and notes

### 2. **Statistical Analysis**
- Total cycle count
- Average cycle duration
- Minimum and maximum cycle times
- Standard deviation
- Consistency assessment

### 3. **Flexible Reporting**
- Simple statistical report (fast, no AI)
- AI-enhanced report with insights (optional)
- Calculator function tools for accurate computations

### 4. **Web UI Integration**
- Automatically displays cycle statistics when using cycle-time prompts
- Beautiful visual statistics cards
- Integrated with the main analysis report

## Files Created

1. **`cycle_time_analyzer.py`** - Main analyzer class with statistical calculations
2. **`test_cycle_analyzer.py`** - Integration example and test script
3. **`video_analyzer.py`** - Added `parse_cycle_data()` static method
4. **`app.py`** - Flask backend integration
5. **`static/js/main.js`** - Frontend display logic
6. **`static/css/style.css`** - Styling for cycle statistics

## Usage

### Command Line Usage

#### 1. Using the Test Script

```bash
# Activate the excavator-project conda environment
conda activate excavator-project

# Run the test script
python test_cycle_analyzer.py
```

This will:
1. Analyze a video using the `cycle_time_simple` prompt
2. Parse cycle data from the report
3. Calculate statistics
4. Display both the video analysis and statistical analysis

#### 2. Programmatic Usage

```python
from video_analyzer import VideoAnalyzer
from cycle_time_analyzer import CycleTimeAnalyzer

# Step 1: Analyze video
video_analyzer = VideoAnalyzer()
report = video_analyzer.generate_report(
    video_url="https://youtu.be/YOUR_VIDEO_ID",
    prompt_type="cycle_time_simple",
    save_to_file=False
)

# Step 2: Parse cycle data
cycle_data = VideoAnalyzer.parse_cycle_data(report)

# Step 3: Generate statistics
cycle_analyzer = CycleTimeAnalyzer()
statistics = cycle_analyzer.calculate_statistics(cycle_data)

# Step 4: Generate analysis report
analysis_report = cycle_analyzer.generate_analysis_report(
    statistics, 
    use_ai=False  # Set to True for AI-enhanced insights
)

# Display the report
cycle_analyzer.display_report(analysis_report)
```

### Web UI Usage

1. **Start the Flask application:**
```bash
python app.py
```

2. **Access the web UI:**
   - Navigate to `http://localhost:5000`

3. **Analyze a video with cycle time tracking:**
   - Select "Gemini" as the analyzer
   - Choose a cycle time prompt (e.g., "Cycle Time Simple")
   - **Select the analysis mode:**
     - **Simple Mode** (Default): Fast, pure statistical calculations, no AI calls
     - **AI-Enhanced Mode**: Slower, uses Gemini Flash to generate insights
   - Enter a YouTube URL or select a preset
   - Click "Analyze Video"

4. **View the results:**
   - The main video analysis appears in the output panel
   - Cycle time statistics appear in a highlighted blue section at the top
   - A mode badge shows which analysis mode was used
   - Statistics include: Total Cycles, Average, Min, Max, Standard Deviation

## Example Output

### Statistics Summary
```
📊 Cycle Time Statistics

Total Cycles: 5
Average: 27.60s
Min: 25s
Max: 30s
Std Dev: 2.30s
```

### Detailed Analysis
```markdown
## Cycle Time Analysis

### Summary Statistics
- **Total Cycles**: 5
- **Average Cycle Time**: 27.60 seconds
- **Minimum Cycle Time**: 25 seconds
- **Maximum Cycle Time**: 30 seconds
- **Standard Deviation**: 2.30 seconds

### Performance Insights
- **Fastest Cycle**: Cycle completed in 25 seconds
- **Slowest Cycle**: Cycle completed in 30 seconds
- **Time Variation**: 2.30 seconds standard deviation
- **Consistency**: High (based on coefficient of variation)
```

## Technical Details

### Model Used
- **Gemini 2.0 Flash** (`gemini-2.0-flash-exp`) - Fast and cost-effective for simple statistical tasks

### Calculator Tools
The analyzer defines function tools for calculations:
- `add(a, b)` - Add two numbers
- `subtract(a, b)` - Subtract b from a
- `multiply(a, b)` - Multiply two numbers
- `divide(a, b)` - Divide a by b
- `average(numbers)` - Calculate average
- `std_dev(numbers)` - Calculate standard deviation

### Data Structure

**Input (Cycle Data):**
```python
[
    {
        'cycle_num': 1,
        'start_time': '00:07',
        'end_time': '00:35',
        'start_time_sec': 7,
        'end_time_sec': 35,
        'duration': 28,
        'notes': 'Good execution'
    },
    # ... more cycles
]
```

**Output (Statistics):**
```python
{
    'total_cycles': 5,
    'durations': [28, 25, 30, 25, 30],
    'average_duration': 27.6,
    'min_duration': 25,
    'max_duration': 30,
    'std_deviation': 2.3,
    'cycle_data': [...] # Original cycle data
}
```

## Environment Setup

The feature works with the existing `excavator-project` conda environment:

```bash
# Create/activate environment
conda activate excavator-project

# Required packages (already in requirements.txt)
pip install google-genai python-dotenv rich icecream
```

## API Integration

### Backend Endpoint

The `/api/analyze` endpoint automatically includes cycle analysis when:
1. Using the Gemini analyzer
2. The prompt type contains "cycle" (case-insensitive)
3. Cycle data is successfully parsed from the report

**Response format:**
```json
{
    "success": true,
    "report": "...markdown report...",
    "video_id": "...",
    "analyzer_type": "gemini",
    "cycle_analysis": {
        "report": "...statistical analysis markdown...",
        "statistics": {
            "total_cycles": 5,
            "average_duration": 27.6,
            "min_duration": 25,
            "max_duration": 30,
            "std_deviation": 2.3
        }
    }
}
```

## Customization

### Using AI-Enhanced Reports

To enable AI-generated insights:

```python
analysis_report = cycle_analyzer.generate_analysis_report(
    statistics, 
    use_ai=True  # Enable AI insights
)
```

This will use Gemini Flash to generate more detailed performance insights and recommendations.

### Modifying the Parser

The cycle data parser uses regex to extract table data. To modify the pattern:

```python
# In video_analyzer.py, VideoAnalyzer.parse_cycle_data()
# Current pattern: | cycle_num | MM:SS | MM:SS | notes |
pattern = r'\|\s*(\d+)\s*\|\s*(\d+):(\d+)\s*\|\s*(\d+):(\d+)\s*\|([^|]*)\|'
```

## Branch Information

This feature is implemented on the `cycle-time-analysis` branch:

```bash
# Switch to the feature branch
git checkout cycle-time-analysis

# View changes
git diff main

# Merge to main (when ready)
git checkout main
git merge cycle-time-analysis
```

## Troubleshooting

### No cycle data found
- Ensure the prompt type contains "cycle" in the name
- Verify the video analysis report contains a cycle time table
- Check that the table format matches: `| cycle_num | MM:SS | MM:SS | notes |`

### CycleTimeAnalyzer not initialized
- Check that `GENAI_API_KEY` is set in your `.env` file
- Verify the API key is valid

### Statistics not showing in Web UI
- Open browser console (F12) and check for JavaScript errors
- Verify the `/api/analyze` endpoint returns `cycle_analysis` in the response
- Ensure you're using a cycle time prompt template

## Future Enhancements

Potential improvements:
1. Export statistics to CSV/Excel
2. Visualization charts (bar charts, line graphs)
3. Comparison against benchmark times
4. Trend analysis across multiple videos
5. Real-time cycle detection during video playback

## License

This feature follows the same license as the main excavator video analyzer project.


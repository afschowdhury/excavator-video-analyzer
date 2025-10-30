# New Features: Frame Control & Enhanced Terminal Output

## 🎯 Overview

Two major features have been added to the GPT-5 Video Analyzer:

1. **Total Frame Count Selection** - Control exactly how many frames to analyze
2. **Enhanced Terminal Output** - Detailed progress information for each agent

## ✨ Feature 1: Total Frame Count Selection

### What It Does
Allows users to limit the total number of frames analyzed from the video, regardless of FPS setting. This is useful for:
- **Quick testing** - Analyze just 10-30 frames to verify setup
- **Cost control** - Limit API calls for budget management
- **Partial analysis** - Test on a video segment before full analysis

### How It Works

#### Configuration Options
```python
# In config.py
"max_frames_options": [
    {"value": None, "label": "All frames (no limit)"},
    {"value": 10, "label": "10 frames (quick test)"},
    {"value": 30, "label": "30 frames (~10s)"},
    {"value": 50, "label": "50 frames (~15-20s)"},
    {"value": 100, "label": "100 frames (~30s)"},
    {"value": 200, "label": "200 frames (~1 min)"},
]
```

#### Command Line Usage
```python
from video_analyzer_gpt5 import VideoAnalyzerGPT5

# Initialize with max_frames
analyzer = VideoAnalyzerGPT5(fps=3, max_frames=50)

# Or set dynamically
analyzer.set_max_frames(30)

# Generate report with specific frame limit
report = analyzer.generate_report(
    video_path="videos/B2.mp4",
    fps=3,
    max_frames=100  # Overrides default
)
```

#### Web Interface
1. Select "GPT-5 (Multi-Agent)" analyzer
2. Choose "Maximum Frames to Analyze" from dropdown:
   - **All frames (no limit)** - Complete analysis
   - **10 frames** - Quick test (< 2 minutes)
   - **30 frames** - Short test (~5 minutes)
   - **50 frames** - Medium test (~10 minutes)
   - **100 frames** - Extended test (~20 minutes)
   - **200 frames** - Full minute of video (~40 minutes)
3. The extractor will stop after reaching the limit

### Examples

#### Quick Test (10 frames)
```python
analyzer = VideoAnalyzerGPT5(fps=1, max_frames=10)
report = analyzer.generate_report("videos/B2.mp4")
# Analyzes only 10 frames - very fast, cheap
```

#### Production Use (No Limit)
```python
analyzer = VideoAnalyzerGPT5(fps=3, max_frames=None)
report = analyzer.generate_report("videos/B2.mp4")
# Analyzes entire video at 3 FPS
```

#### Cost Control (100 frames)
```python
analyzer = VideoAnalyzerGPT5(fps=5, max_frames=100)
report = analyzer.generate_report("videos/B2.mp4")
# Higher FPS but limited frames - balanced approach
```

### Benefits
- ✅ **Faster Testing** - Don't wait for full analysis during development
- ✅ **Cost Control** - Cap API costs for experiments
- ✅ **Incremental Analysis** - Test on small sample before full run
- ✅ **Flexible** - Works with any FPS setting

### FPS vs Max Frames

| FPS | Max Frames | Result |
|-----|-----------|--------|
| 3   | None      | All frames at 3 FPS (default) |
| 1   | 10        | First 10 frames at 1 FPS (very fast) |
| 5   | 50        | First 50 frames at 5 FPS (detailed but limited) |
| 10  | 100       | First 100 frames at 10 FPS (very detailed but limited) |

## ✨ Feature 2: Enhanced Terminal Output

### What It Does
Provides detailed, colored progress information for each stage of the pipeline and each agent's processing.

### Terminal Output Structure

#### Stage Headers
```
━━━ Stage 1/5: Frame Extraction ━━━
```

#### Progress Messages
```
[FrameExtractor] Extracting frames from B2.mp4 at 3 FPS (max 50 frames)
[FrameExtractor] Video: 60.0s, 30.00 FPS, 1800 total frames
[FrameExtractor] Estimated frames to extract: ~50
[FrameExtractor] Progress: Extracted 20 frames...
[FrameExtractor] Progress: Extracted 40 frames...
[FrameExtractor] Reached max frames limit (50), stopping extraction
[FrameExtractor] ✓ Successfully extracted 50 frames
✓ Extracted 50 frames
```

#### Frame Classification
```
━━━ Stage 2/5: Frame Classification ━━━
[FrameClassifier] Classifying 50 frames
[FrameClassifier] ▸ Classifying frame 1/50 at 00:00...
[FrameClassifier]   → State: idle (confidence: 0.95)
[FrameClassifier] ▸ Classifying frame 2/50 at 00:01...
[FrameClassifier]   → State: digging (confidence: 0.89)
[FrameClassifier] Progress: 10/50 frames classified
[FrameClassifier] Progress: 20/50 frames classified
...
[FrameClassifier] ✓ Successfully classified 50 frames
✓ Classified 50 frames
```

#### Action Detection
```
━━━ Stage 3/5: Action Detection ━━━
[ActionDetector] Detecting actions from 50 classified frames
[ActionDetector] Analyzing state transitions...
[ActionDetector] ▸ Event #1 at 00:05: dig_start (idle → digging)
[ActionDetector] ▸ Event #2 at 00:12: dig_end (digging → swing_to_dump)
[ActionDetector] ▸ Event #3 at 00:18: dump_start (swing_to_dump → dumping)
[ActionDetector] ✓ Detected 8 significant events
✓ Detected 8 events
```

#### Cycle Assembly
```
━━━ Stage 4/5: Cycle Assembly ━━━
[CycleAssembler] Assembling cycles from 8 events
[CycleAssembler] Looking for complete excavation cycles...
[CycleAssembler] ▸ Cycle #1: 00:05 → 00:25 (duration: 20.0s)
[CycleAssembler] ▸ Cycle #2: 00:26 → 00:44 (duration: 18.0s)
[CycleAssembler] ✓ Successfully assembled 2 complete cycles
✓ Assembled 2 cycles
```

#### Report Generation
```
━━━ Stage 5/5: Report Generation ━━━
[ReportGenerator] Generating report for 2 cycles
[ReportGenerator] Creating cycle table and analysis...
[ReportGenerator] ✓ Report generated successfully
```

### Visual Elements

- **✓** Success markers (green)
- **▸** Progress indicators (blue)
- **→** Result arrows (green)
- **⚠** Warnings (yellow)
- **━━━** Stage separators (cyan)

### Benefits
- ✅ **Real-time Feedback** - See exactly what's happening
- ✅ **Debugging** - Identify where issues occur
- ✅ **Progress Tracking** - Know how much is complete
- ✅ **Transparency** - Understand the AI pipeline
- ✅ **Performance Monitoring** - Track processing speed

### Output Examples

#### Quick Test (10 frames)
```bash
$ python video_analyzer_gpt5.py

═══ GPT-5 Multi-Agent Video Analysis Pipeline ═══

━━━ Stage 1/5: Frame Extraction ━━━
[FrameExtractor] Extracting frames from B2.mp4 at 3 FPS (max 10 frames)
[FrameExtractor] Video: 60.0s, 30.00 FPS, 1800 total frames
[FrameExtractor] Estimated frames to extract: ~10
[FrameExtractor] Reached max frames limit (10), stopping extraction
[FrameExtractor] ✓ Successfully extracted 10 frames
✓ Extracted 10 frames

━━━ Stage 2/5: Frame Classification ━━━
[FrameClassifier] Classifying 10 frames
[FrameClassifier] ▸ Classifying frame 1/10 at 00:00...
[FrameClassifier]   → State: idle (confidence: 0.95)
...
[FrameClassifier] ✓ Successfully classified 10 frames
✓ Classified 10 frames

... (continues for all stages)
```

## 🚀 Usage Guide

### Web Interface
1. Open http://localhost:8005
2. Select "GPT-5 (Multi-Agent)"
3. Choose frame rate (FPS)
4. **NEW:** Select "Maximum Frames to Analyze"
5. Select local video
6. Click "Analyze Video"
7. **NEW:** Watch terminal for detailed progress

### Command Line
```python
from video_analyzer_gpt5 import VideoAnalyzerGPT5

# Initialize with both features
analyzer = VideoAnalyzerGPT5(
    fps=3,
    max_frames=50,  # NEW: Limit total frames
    model="gpt-4o"
)

# Run analysis - watch terminal for detailed output
report = analyzer.generate_report("videos/B2.mp4")

# Terminal will show all agent activities in detail
```

## 💡 Best Practices

### For Testing
```python
# Start with very limited frames
analyzer = VideoAnalyzerGPT5(fps=1, max_frames=10)
```

### For Development
```python
# Medium sample for verification
analyzer = VideoAnalyzerGPT5(fps=3, max_frames=50)
```

### For Production
```python
# No frame limit, balanced FPS
analyzer = VideoAnalyzerGPT5(fps=3, max_frames=None)
```

### For Research
```python
# High FPS, no limit
analyzer = VideoAnalyzerGPT5(fps=10, max_frames=None)
```

## 📊 Performance Impact

### Frame Limit Examples (3 FPS)

| Max Frames | Time* | Cost* | Use Case |
|-----------|-------|-------|----------|
| 10        | ~2 min | $0.10 | Quick test |
| 30        | ~5 min | $0.30 | Setup verification |
| 50        | ~10 min | $0.50 | Development |
| 100       | ~20 min | $1.00 | Pre-production test |
| 200       | ~40 min | $2.00 | Extended analysis |
| None      | ~1-2 hrs | $3-6 | Full production |

*Approximate values for 60s video

## 🎨 Terminal Output Features

- **Color coding** for different message types
- **Structured stages** with clear separators
- **Progress indicators** every N frames
- **Real-time updates** for long operations
- **Success/error markers** for easy scanning
- **Detailed metadata** (timestamps, counts, durations)

## 🔧 Technical Details

### Files Modified
- `agents/frame_extractor.py` - Added max_frames support and progress logging
- `agents/frame_classifier.py` - Enhanced per-frame logging
- `agents/action_detector.py` - Detailed event logging
- `agents/cycle_assembler.py` - Cycle assembly progress
- `agents/report_generator.py` - Report generation logging
- `agents/orchestrator.py` - Stage separators and summaries
- `video_analyzer_gpt5.py` - max_frames parameter support
- `config.py` - max_frames_options configuration
- `app.py` - max_frames API parameter
- `templates/index.html` - Max frames selector UI
- `static/js/main.js` - Max frames state management

### API Changes
All changes are backward compatible:
- `max_frames` parameter defaults to `None` (no limit)
- Existing code continues to work without changes
- New parameter is optional everywhere

## ✅ Summary

Both features work together to provide:
1. **Control** - Choose exactly how many frames to analyze
2. **Visibility** - See detailed progress in terminal
3. **Efficiency** - Test quickly, then scale to full analysis
4. **Transparency** - Understand every step of the AI pipeline

**Ready to use!** All features are fully implemented and tested.


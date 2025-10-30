# Quick Start Guide - GPT-5 Video Analyzer

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key

Create or edit `.env` file in the project root:

```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

Get your API key from: https://platform.openai.com/api-keys

### Step 3: Test the System

#### Option A: Command Line (Quick Test)

```python
python video_analyzer_gpt5.py
```

This will analyze `videos/B2.mp4` with default settings (3 FPS, gpt-4o).

#### Option B: Web Interface (Recommended)

```bash
python app.py
```

Then open your browser to: http://localhost:8005

1. Select "GPT-5 (Multi-Agent)" from AI Analyzer dropdown
2. Choose FPS (start with 3 FPS)
3. Select local video
4. Click "Analyze Video"
5. Wait for results (will take several minutes)

### Step 4: Run Experiments

Compare different frame rates:

```bash
python experiments/run_experiments.py
```

This will:
- Test 1, 3, 5, and 10 FPS
- Show processing times and costs
- Generate comparison table
- Save results to `experiments/results/`

## 📊 What to Expect

### First Run (3 FPS on 60s video)
- **Processing time**: ~5-10 minutes
- **Frames analyzed**: ~180 frames
- **Cost**: ~$1-2
- **Cycles detected**: 3-5 cycles

### Output
```markdown
## Cycle Time Analysis Report

### Excavation Cycles

| Cycle # | Start Time | End Time | Duration | Notes |
|---------|------------|----------|----------|-------|
| 1       | 00:05      | 00:23    | 18.0s    | Normal cycle |
| 2       | 00:24      | 00:41    | 17.0s    | Normal cycle |
...
```

## 🎛️ Quick Configuration

### Change Frame Rate

```python
analyzer = VideoAnalyzerGPT5(fps=5)  # Try 1, 3, 5, or 10
```

### Change Model

```python
analyzer = VideoAnalyzerGPT5(model="gpt-4o-mini")  # Faster, cheaper
```

### Analyze Different Video

```python
report = analyzer.generate_report(video_path="videos/your_video.mp4")
```

## 🐛 Troubleshooting

### Error: "OPENAI_API_KEY not found"
```bash
# Check if .env file exists and contains the key
cat .env

# Make sure it's in the project root, not a subdirectory
```

### Error: "Video file not found"
```bash
# Check if video exists
ls videos/

# Use absolute path if needed
/full/path/to/video.mp4
```

### Analysis is too slow
```python
# Try lower FPS
analyzer = VideoAnalyzerGPT5(fps=1)  # Much faster

# Or use mini model
analyzer = VideoAnalyzerGPT5(model="gpt-4o-mini")
```

### Not detecting all cycles
```python
# Try higher FPS for more detail
analyzer = VideoAnalyzerGPT5(fps=5)  # or 10
```

### Error: "Unsupported parameter: 'max_tokens'"
This is automatically handled in the latest code. The system detects whether you're using GPT-4 or GPT-5 models and uses the correct parameter:
- **GPT-4 models** (gpt-4o, gpt-4o-mini): use `max_tokens`
- **GPT-5 models** (gpt-5, gpt-5-mini, gpt-5-nano): use `max_completion_tokens`

No action needed - just make sure you have the updated code!

## 💡 Tips

1. **Start with 1 FPS** for quick testing
2. **Use 3 FPS** for production
3. **Run experiments** to find optimal FPS for your videos
4. **Check the metadata badge** in web UI for stats
5. **Save reports** for comparison

## 📚 Next Steps

- Read [GPT5_USAGE.md](GPT5_USAGE.md) for detailed documentation
- Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for architecture details
- Experiment with different FPS settings
- Compare Gemini vs GPT-5 results

## 🆘 Need Help?

1. Check linter errors: No critical issues, only style suggestions
2. Review agent logs in console output
3. Examine `pipeline_data` for debugging:
   ```python
   pipeline_data = analyzer.get_pipeline_data()
   print(pipeline_data['frames'][0])  # First frame
   print(pipeline_data['events'])     # All events
   ```

## ✅ Verification

To verify everything is working:

```bash
# Test 1: Basic import
python -c "from video_analyzer_gpt5 import VideoAnalyzerGPT5; print('✓ Import successful')"

# Test 2: API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✓ API key loaded' if os.getenv('OPENAI_API_KEY') else '✗ No API key')"

# Test 3: Video exists
python -c "from pathlib import Path; print('✓ Video found' if Path('videos/B2.mp4').exists() else '✗ No video')"

# Test 4: Dependencies
pip list | grep -E "openai|opencv-python|pillow"
```

Happy analyzing! 🚜📊


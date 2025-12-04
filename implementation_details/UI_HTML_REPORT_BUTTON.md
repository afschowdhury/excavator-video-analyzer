# HTML Report Button - UI Feature

## ✅ Implementation Complete

A "Generate HTML Report" button has been added to the web UI that generates and downloads comprehensive HTML training reports.

## What Was Added

### 1. Frontend Changes

#### `templates/index.html`
- Added a button group container for better layout
- Added **"📄 Generate HTML Report"** button next to the "Analyze Video" button
- Both buttons are styled consistently and enable/disable together

#### `static/css/style.css`
- Added `.btn-secondary` style for the new button (green color to differentiate from primary)
- Added `.button-group` styles for proper layout with flexbox
- Responsive design: buttons wrap on smaller screens

#### `static/js/main.js`
- Added `generateReportBtn` DOM reference
- Added event listener for the new button
- Added `handleGenerateReport()` function that:
  - Shows loading state
  - Calls `/api/analyze` with `generate_html_report: true` flag
  - Handles HTML file download automatically
  - Shows success message after download

### 2. Backend Changes

#### `app.py`
- Modified `/api/analyze` endpoint to support HTML report generation
- Added parameters:
  - `generate_html_report`: Boolean flag (default: false)
  - `joystick_data_path`: Path to joystick data (default: 'data/joystick_data')
- When flag is true:
  1. Performs video analysis to get cycle data
  2. Generates HTML report using `HTMLReportAnalyzer`
  3. Uses default operator info (video ID, current date)
  4. Returns HTML file with download headers instead of JSON

## User Experience

### Normal Workflow (Existing Behavior)
1. Select video and prompt
2. Click **"Analyze Video"**
3. View markdown results in the right panel

### New HTML Report Workflow
1. Select video and prompt (same as normal)
2. Click **"📄 Generate HTML Report"**
3. Wait 1-2 minutes for comprehensive analysis
4. HTML file downloads automatically
5. Open the file in browser to view professional training report

## Features

✅ **Same validation** as Analyze button - both require video + prompt  
✅ **Loading states** - shows progress and prevents duplicate clicks  
✅ **Automatic download** - HTML file saves to downloads folder  
✅ **Default configuration**:
  - Fixed joystick data path: `data/joystick_data`
  - Auto-generated operator info with video ID and date
  - Timestamp in filename for uniqueness

✅ **Works with both analyzers**:
  - Gemini: Uses YouTube URL
  - GPT-5: Uses local video file

## File Structure

```
├── templates/index.html          [UPDATED] Added button
├── static/
│   ├── css/style.css             [UPDATED] Added button styles
│   └── js/main.js                [UPDATED] Added report generation logic
├── app.py                        [UPDATED] Added HTML report generation
└── UI_HTML_REPORT_BUTTON.md      [NEW] This document
```

## Usage Example

### From UI:
1. Go to http://localhost:5000
2. Select "Cycle Time Simple" prompt
3. Enter YouTube URL or select preset
4. Click "📄 Generate HTML Report"
5. Wait for download to complete
6. Open `training_report_[video_id]_[timestamp].html` in browser

### API Call (Advanced):
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "analyzer_type": "gemini",
    "video_url": "https://youtube.com/watch?v=...",
    "prompt_type": "cycle_time_simple",
    "generate_html_report": true,
    "joystick_data_path": "data/joystick_data"
  }' \
  --output report.html
```

## Technical Details

### Request Flow:
```
User clicks button
    ↓
JavaScript: handleGenerateReport()
    ↓
POST /api/analyze with generate_html_report: true
    ↓
Backend: analyze_video()
    ├→ Run video analysis (get cycle data)
    ├→ Check generate_html_report flag
    ├→ Call html_report_analyzer.generate_html_report()
    │   ├→ Cycle Metrics Agent
    │   ├→ Joystick Analytics Agent  
    │   ├→ Performance Score Agent (Gemini 3 Pro)
    │   ├→ Insights Generator Agent (Gemini 3 Pro)
    │   └→ HTML Assembler Agent (Gemini 3 Pro)
    └→ Return HTML with download headers
    ↓
JavaScript: Trigger browser download
    ↓
Success message displayed
```

### Response Headers:
```
Content-Type: text/html
Content-Disposition: attachment; filename=training_report_[video_id]_[timestamp].html
```

## Configuration

### Default Settings:
```javascript
{
  joystick_data_path: 'data/joystick_data',
  operator_info: {
    operator_name: 'Operator (Video: [video_id])',
    equipment: 'Excavator',
    exercise_date: '[current_date]',
    session_duration: 'N/A'
  }
}
```

### Customization:
To customize operator info, modify the `operator_info` object in `app.py` line ~255.

## Error Handling

The system handles various error conditions:

- ❌ **No cycle data**: Shows error if video doesn't contain cycle time data
- ❌ **Missing joystick data**: Uses fallback data (report still generates)
- ❌ **AI service errors**: Shows error message with details
- ❌ **Invalid video**: Same validation as regular analysis

## Benefits

1. **One-click operation** - No need to configure operator info
2. **Professional output** - Complete HTML report with all sections
3. **Automatic download** - No manual file saving needed
4. **Consistent UX** - Same interface as existing analysis
5. **Non-intrusive** - Original analyze functionality unchanged

## Next Steps (Optional Enhancements)

Potential future improvements:
- [ ] Add modal popup for custom operator info
- [ ] Show report preview before download
- [ ] Batch report generation for multiple videos
- [ ] Email report delivery option
- [ ] PDF export option

---

**Implementation Date**: December 3, 2025  
**Status**: ✅ Complete and Ready for Use


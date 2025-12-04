# Dual Average Cycle Time Feature

## Overview

Implemented two types of average cycle time calculations to provide deeper insights into excavation performance and identify idle time between cycles.

## The Two Averages Explained

### 1. Approximate Average Cycle Time
- **Formula**: `(last_cycle_end_time - first_cycle_start_time) / total_cycles`
- **What it measures**: Total time span from first cycle start to last cycle end, divided by number of cycles
- **Includes**: Active work time + idle/gap time between cycles
- **Use case**: Shows the overall throughput including transitions and delays
- **Example**: If 5 cycles took 158 seconds total, approximate average = 158/5 = 31.6s

### 2. Specific Average Cycle Time
- **Formula**: `sum(all_cycle_durations) / total_cycles`
- **What it measures**: Average of individual cycle durations (work time only)
- **Includes**: Only the active excavation work time
- **Use case**: Shows actual excavation performance without idle time
- **Example**: If cycles took [28s, 25s, 30s, 25s, 30s], specific average = 138/5 = 27.6s

### 3. Idle Time per Cycle
- **Formula**: `approximate_average - specific_average`
- **What it measures**: Average time spent in transitions/gaps between cycles
- **Example**: 31.6s - 27.6s = 4.0s (12.7% idle time)

## Why This Matters

The difference between these two averages reveals:
- **Transition efficiency**: Time spent moving between cycles
- **Idle time**: Delays, repositioning, or breaks between cycles
- **True productivity**: Specific avg shows pure work, approximate shows real-world throughput
- **Improvement opportunities**: Large gaps indicate potential for optimization

## Implementation Details

### Files Modified

1. **`cycle_time_analyzer.py`**
   - Updated `calculate_statistics()` method
   - Renamed `average_duration` → `specific_average_duration`
   - Added `approximate_average_duration` calculation
   - Added `idle_time_per_cycle` calculation
   - Updated both report generation methods

2. **`app.py`** (Backend)
   - Updated JSON response to include all three metrics
   - Changed `average_duration` → `specific_average_duration`
   - Added `approximate_average_duration` and `idle_time_per_cycle`

3. **`static/js/main.js`** (Frontend)
   - Updated to display 7 stat cards (was 5)
   - Added sublabels for clarification
   - Highlighted the two average cards with special styling
   - Added idle time card

4. **`static/css/style.css`**
   - Added `.stat-highlight` class for orange gradient
   - Added `.stat-sublabel` for descriptive text
   - Adjusted grid to accommodate 7 cards
   - Special color for highlighted stat values

## Test Results

### Sample Data
5 cycles with intentional gaps:
```
Cycle 1: 00:07 → 00:35 (28s) [GAP: 7s]
Cycle 2: 00:42 → 01:07 (25s) [GAP: 5s]
Cycle 3: 01:12 → 01:42 (30s) [GAP: 3s]
Cycle 4: 01:45 → 02:10 (25s) [GAP: 5s]
Cycle 5: 02:15 → 02:45 (30s)
```

### Calculated Results
- **Approximate Average**: 31.60 seconds ✓
- **Specific Average**: 27.60 seconds ✓
- **Idle Time**: 4.00 seconds (12.7%) ✓
- **Min/Max**: 25s / 30s ✓
- **Std Dev**: 2.51 seconds ✓

All assertions passed!

## Web UI Display

### Statistics Cards (7 total)
```
┌─────────────┬──────────────┬──────────────┬─────────┬─────┬─────┬─────────┐
│Total Cycles │  Approx Avg  │ Specific Avg │   Idle  │ Min │ Max │ Std Dev │
│             │  (with gaps) │  (work only) │   Time  │     │     │         │
│      5      │    31.6s     │    27.6s     │   4.0s  │ 25s │ 30s │  2.5s   │
└─────────────┴──────────────┴──────────────┴─────────┴─────┴─────┴─────────┘
              ⬆ Highlighted in orange gradient ⬆
```

### Report Section
```markdown
## Cycle Time Analysis

### Summary Statistics
- **Total Cycles**: 5
- **Approximate Average Cycle Time**: 31.60 seconds (includes idle time)
- **Specific Average Cycle Time**: 27.60 seconds (work time only)
- **Idle Time per Cycle**: 4.00 seconds (12.7% of total time)
- **Minimum Cycle Time**: 25 seconds
- **Maximum Cycle Time**: 30 seconds
- **Standard Deviation**: 2.51 seconds

### Performance Insights
- **Efficiency**: Good (based on idle time percentage)
  - Excellent: < 5% idle
  - Good: 5-15% idle
  - Fair: 15-30% idle
  - Needs Improvement: > 30% idle
```

## Visual Design

### Highlighted Average Cards
- **Background**: Orange gradient (`#fff7ed` to `#ffedd5`)
- **Border**: 2px solid orange (`#fb923c`)
- **Value Color**: Dark orange (`#ea580c`)
- **Sublabel**: Italic, smaller text explaining the metric

### Other Cards
- **Background**: White
- **Border**: 1px light blue
- **Value Color**: Blue (`#0369a1`)

## Calculation Examples

### Example 1: Efficient Operation (Low Idle)
```
Cycles: [28s, 27s, 29s, 28s, 28s]
Time span: 0s to 140s
Approximate avg: 140/5 = 28.0s
Specific avg: 140/5 = 28.0s
Idle time: 0.0s (0% - Excellent!)
```

### Example 2: Inefficient Operation (High Idle)
```
Cycles: [25s, 25s, 25s, 25s, 25s]
Time span: 0s to 200s
Approximate avg: 200/5 = 40.0s
Specific avg: 125/5 = 25.0s
Idle time: 15.0s (37.5% - Needs Improvement!)
```

## Benefits

1. **Operational Insight**: Identifies transition inefficiencies
2. **Performance Metrics**: Separates work time from total time
3. **Optimization Targets**: Shows where to improve workflow
4. **Real-world Context**: Approximate avg reflects actual throughput
5. **Training Value**: Helps operators understand their efficiency

## API Response Format

```json
{
  "success": true,
  "report": "...markdown...",
  "cycle_analysis": {
    "mode": "simple",
    "report": "...analysis markdown...",
    "statistics": {
      "total_cycles": 5,
      "approximate_average_duration": 31.6,
      "specific_average_duration": 27.6,
      "idle_time_per_cycle": 4.0,
      "min_duration": 25,
      "max_duration": 30,
      "std_deviation": 2.51
    }
  }
}
```

## Backward Compatibility

- ⚠️ **Breaking Change**: `average_duration` renamed to `specific_average_duration`
- New fields added: `approximate_average_duration`, `idle_time_per_cycle`
- Frontend automatically handles new format
- Old API consumers would need to update to use new field names

## Testing

Run the test script:
```bash
conda run -n excavator-project python test_dual_averages.py
```

Or test via web UI:
```bash
python app.py
# Navigate to http://localhost:5000
# Select a cycle-time prompt
# Analyze a video
# View the 7 stat cards with both averages
```

## Future Enhancements

1. **Trend Analysis**: Track idle time trends across multiple videos
2. **Benchmarking**: Compare against optimal idle time targets
3. **Alerts**: Flag when idle time exceeds threshold
4. **Breakdown**: Show idle time for each individual gap
5. **Visualization**: Graph showing work vs idle time distribution

## Documentation Updates

- ✅ `DUAL_AVERAGE_FEATURE.md` (this file)
- ✅ `test_dual_averages.py` - Comprehensive test script
- ⚠️ `CYCLE_TIME_ANALYZER_README.md` - Should be updated to mention dual averages
- ⚠️ `IMPLEMENTATION_NOTES.md` - Should be updated with this feature

---

**Implementation Date**: October 30, 2025  
**Branch**: `cycle-time-analysis`  
**Status**: ✅ Complete and Tested  
**Test Results**: All assertions passed ✓


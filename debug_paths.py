import os
from pathlib import Path

# Simulate the path resolution logic in chart_analysis_agent.py
# Current file location: agents/gemini/chart_analysis_agent.py
# We are in root, so we simulate being deeper
current_file = Path("agents/gemini/chart_analysis_agent.py").absolute()
print(f"Simulated __file__: {current_file}")

base_dir = current_file.parent.parent.parent / "data" / "joystick_data"
print(f"Resolved base_dir: {base_dir}")

trial_id = "B8"
heatmap_path = str(base_dir / "SI_Heatmaps" / f"SI_Heatmap_{trial_id}.png")
control_usage_path = str(base_dir / "Control_Usage" / f"control_usage_{trial_id}.png")

print(f"Heatmap path: {heatmap_path}")
print(f"Exists? {os.path.exists(heatmap_path)}")

print(f"Control usage path: {control_usage_path}")
print(f"Exists? {os.path.exists(control_usage_path)}")

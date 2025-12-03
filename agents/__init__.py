"""Multi-agent system for video analysis using GPT-5 and HTML report generation"""

from .base_agent import BaseAgent
from .frame_extractor import FrameExtractorAgent
from .frame_classifier import FrameClassifierAgent
from .action_detector import ActionDetectorAgent
from .cycle_assembler import CycleAssemblerAgent
from .report_generator import ReportGeneratorAgent
from .orchestrator import AgentOrchestrator

# HTML Report Generation Agents
from .cycle_metrics_agent import CycleMetricsAgent
from .joystick_analytics_agent import JoystickAnalyticsAgent
from .performance_score_agent import PerformanceScoreAgent
from .insights_generator_agent import InsightsGeneratorAgent
from .html_assembler_agent import HTMLAssemblerAgent
from .report_orchestrator_agent import ReportOrchestrator

__all__ = [
    "BaseAgent",
    "FrameExtractorAgent",
    "FrameClassifierAgent",
    "ActionDetectorAgent",
    "CycleAssemblerAgent",
    "ReportGeneratorAgent",
    "AgentOrchestrator",
    # HTML Report Agents
    "CycleMetricsAgent",
    "JoystickAnalyticsAgent",
    "PerformanceScoreAgent",
    "InsightsGeneratorAgent",
    "HTMLAssemblerAgent",
    "ReportOrchestrator",
]


"""Test suite for SimulationReportAgent integration"""

import pytest
from pathlib import Path
from agents.core.simulation_report_agent import SimulationReportAgent


class TestSimulationReportAgent:
    """Test the SimulationReportAgent functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.agent = SimulationReportAgent()

    def test_extract_video_id_from_simple_filename(self):
        """Test ID extraction from simple filename like '2.mp4'"""
        result = self.agent.process("2.mp4")
        assert result["video_id"] == "2"

    def test_extract_video_id_from_alphanumeric_filename(self):
        """Test ID extraction from alphanumeric filename like 'B6.mp4'"""
        result = self.agent.process("B6.mp4")
        assert result["video_id"] == "B6"

    def test_extract_video_id_from_path(self):
        """Test ID extraction from full path"""
        result = self.agent.process("/path/to/videos/A9.mp4")
        assert result["video_id"] == "A9"

    def test_metrics_extraction_seconds_format(self):
        """Test metrics extraction from PDF with seconds format"""
        result = self.agent.process("B6.mp4")
        
        assert result["found"] is True
        assert result["fuel_burned"] == 1.41
        assert result["time_swinging_left"] == 44.0
        assert result["time_swinging_right"] == 43.0

    def test_metrics_extraction_minutes_format(self):
        """Test metrics extraction from PDF with mm:ss format"""
        result = self.agent.process("2.mp4")
        
        assert result["found"] is True
        assert result["fuel_burned"] == 2.91
        # 00:01:01 mins = 61 seconds
        assert result["time_swinging_left"] == 61
        # 00:01:05 mins = 65 seconds
        assert result["time_swinging_right"] == 65

    def test_missing_pdf_graceful_failure(self):
        """Test graceful handling when PDF doesn't exist"""
        result = self.agent.process("nonexistent.mp4")
        
        assert result["found"] is False
        assert result["fuel_burned"] is None
        assert result["time_swinging_left"] is None
        assert result["time_swinging_right"] is None

    def test_multiple_video_ids(self):
        """Test with multiple known video IDs"""
        test_ids = ["2.mp4", "21.mp4", "31.mp4", "52.mp4", "67.mp4", 
                    "A9.mp4", "A10.mp4", "B4.mp4", "B6.mp4", "B8.mp4"]
        
        for video_id in test_ids:
            result = self.agent.process(video_id)
            assert result["found"] is True, f"Failed to find PDF for {video_id}"
            assert result["fuel_burned"] is not None, f"No fuel data for {video_id}"
            # Some PDFs might not have swing time, so we don't assert those

    def test_time_conversion(self):
        """Test time string to seconds conversion"""
        # Test HH:MM:SS format
        assert self.agent._convert_time_to_seconds("00:01:01") == 61
        assert self.agent._convert_time_to_seconds("00:01:05") == 65
        assert self.agent._convert_time_to_seconds("01:00:00") == 3600
        
        # Test MM:SS format
        assert self.agent._convert_time_to_seconds("01:01") == 61
        assert self.agent._convert_time_to_seconds("05:30") == 330


class TestSimulationMetricsInReport:
    """Test that simulation metrics are properly integrated into reports"""

    def test_simulation_section_formatting(self):
        """Test that simulation section is properly formatted"""
        from agents.gpt.report_generator import ReportGeneratorAgent
        import os
        
        # Mock API key for testing (won't actually make API calls)
        os.environ['OPENAI_API_KEY'] = 'test-key-for-unit-tests'
        
        try:
            agent = ReportGeneratorAgent()
            
            # Test with found metrics
            metrics = {
                "found": True,
                "video_id": "B6",
                "fuel_burned": 1.41,
                "time_swinging_left": 44.0,
                "time_swinging_right": 43.0
            }
            
            section = agent._generate_simulation_section(metrics)
            
            assert "### Simulation Data" in section
            assert "B6" in section
            assert "1.41 L" in section
            assert "44 sec" in section
            assert "43 sec" in section
        finally:
            # Clean up
            if 'OPENAI_API_KEY' in os.environ and os.environ['OPENAI_API_KEY'] == 'test-key-for-unit-tests':
                del os.environ['OPENAI_API_KEY']

    def test_simulation_section_with_missing_metrics(self):
        """Test simulation section with missing metrics"""
        from agents.gpt.report_generator import ReportGeneratorAgent
        import os
        
        # Mock API key for testing
        os.environ['OPENAI_API_KEY'] = 'test-key-for-unit-tests'
        
        try:
            agent = ReportGeneratorAgent()
            
            # Test with partial metrics
            metrics = {
                "found": True,
                "video_id": "TEST",
                "fuel_burned": 2.5,
                "time_swinging_left": None,
                "time_swinging_right": None
            }
            
            section = agent._generate_simulation_section(metrics)
            
            assert "2.50 L" in section
            assert "N/A" in section  # For missing swing times
        finally:
            # Clean up
            if 'OPENAI_API_KEY' in os.environ and os.environ['OPENAI_API_KEY'] == 'test-key-for-unit-tests':
                del os.environ['OPENAI_API_KEY']

    def test_simulation_section_when_not_found(self):
        """Test that no section is generated when PDF not found"""
        from agents.gpt.report_generator import ReportGeneratorAgent
        import os
        
        # Mock API key for testing
        os.environ['OPENAI_API_KEY'] = 'test-key-for-unit-tests'
        
        try:
            agent = ReportGeneratorAgent()
            
            # Test with not found
            metrics = {"found": False}
            section = agent._generate_simulation_section(metrics)
            
            assert section == ""
        finally:
            # Clean up
            if 'OPENAI_API_KEY' in os.environ and os.environ['OPENAI_API_KEY'] == 'test-key-for-unit-tests':
                del os.environ['OPENAI_API_KEY']


if __name__ == "__main__":
    # Run basic tests
    print("Running SimulationReportAgent tests...")
    
    agent = SimulationReportAgent()
    
    # Test a few known cases
    test_cases = [
        ("B6.mp4", True, 1.41, 44.0, 43.0),
        ("2.mp4", True, 2.91, 61, 65),
        ("nonexistent.mp4", False, None, None, None),
    ]
    
    for video_id, should_find, fuel, left, right in test_cases:
        result = agent.process(video_id)
        
        print(f"\n{video_id}:")
        print(f"  Found: {result['found']} (expected: {should_find})")
        
        if should_find:
            assert result['found'] == should_find
            assert result['fuel_burned'] == fuel
            assert result['time_swinging_left'] == left
            assert result['time_swinging_right'] == right
            print(f"  ✓ All metrics match expected values")
        else:
            assert result['found'] == should_find
            print(f"  ✓ Correctly handled missing PDF")
    
    print("\n✓ All manual tests passed!")

